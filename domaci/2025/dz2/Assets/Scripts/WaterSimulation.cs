using UnityEngine;
using UnityEngine.Rendering;

/// <summary>
/// Interactive water surface simulation (RG2 DZ2).
///
/// Every frame a compute shader rebuilds the height map (ping-pong between two RFloat
/// render textures) and the matching normal map; the water shader displaces the grid
/// vertices from the height map and shades them with cube-map reflection, a directional
/// specular highlight and Fresnel transparency. Dragging the cursor injects waves.
///
/// Two height-update modes are available (see <see cref="SimulationMode"/>): the literal
/// diffusion scheme from the assignment, and a wave equation with propagating ripples.
/// </summary>
public enum SimulationMode
{
    Diffusion, // literal assignment pseudocode — the surface smooths out
    Wave       // wave equation — propagating, interfering ripples
}

[RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
public class WaterSimulation : MonoBehaviour
{
    [Header("Surface mesh")]
    [Tooltip("Number of quads per side. Vertex count is (resolution + 1)^2.")]
    [Range(2, 512)]
    [SerializeField] private int resolution = 128;

    [Tooltip("World-space size of the (square) water surface, in units.")]
    [Min(0.01f)]
    [SerializeField] private float surfaceSize = 10f;

    [Header("Height map (compute)")]
    [Tooltip("Compute shader that builds the height map. Drag Assets/Shaders/WaterSim.compute here.")]
    [SerializeField] private ComputeShader simShader;

    [Tooltip("Resolution of the (square) height map texture. Tune empirically.")]
    [Range(16, 1024)]
    [SerializeField] private int heightMapSize = 256;

    [Header("Wave simulation")]
    [Tooltip("Diffusion = literal assignment pseudocode (surface smooths out). " +
             "Wave = wave equation with propagating, interfering ripples (matches the " +
             "assignment's result image).")]
    [SerializeField] private SimulationMode mode = SimulationMode.Wave;

    [Tooltip("Diffusion mode: 0 = frozen, 1 = instantly smoothed (try ~0.3). " +
             "Wave mode: this is the damping of the ripples — use ~0.95–0.99.")]
    [Range(0f, 1f)]
    [SerializeField] private float dampFactor = 0.97f;

    [Tooltip("How quickly the surface settles back to its rest level. Prevents repeated " +
             "splashes from raising the whole surface. Higher = calmer, dies out faster. " +
             "(Diffusion mode only.)")]
    [Range(0f, 0.2f)]
    [SerializeField] private float restoreFactor = 0.02f;

    [Tooltip("Simulation steps per second. Lower = ripples propagate more slowly across " +
             "the surface (the wave travels one cell per step).")]
    [Range(5f, 120f)]
    [SerializeField] private float simulationRate = 30f;

    [Tooltip("Maximum vertical displacement of the surface, in units.")]
    [SerializeField] private float maxWaveHeight = 0.5f;

    [Tooltip("Scales the slope used when building the normal map (step c). Tune empirically.")]
    [SerializeField] private float normalStrength = 2f;

    [Header("Appearance")]
    [SerializeField] private Color waterColor = new Color(0.1f, 0.3f, 0.5f, 1f);

    [Tooltip("How much of the environment reflection shows at a head-on view (0 = only water color).")]
    [Range(0f, 1f)]
    [SerializeField] private float reflectivity = 0.4f;

    [Tooltip("Tightness of the specular highlight from the directional light.")]
    [Range(1f, 256f)]
    [SerializeField] private float shininess = 80f;

    [Tooltip("Sharpness of the Fresnel falloff for reflection/transparency.")]
    [Range(0.5f, 8f)]
    [SerializeField] private float fresnelPower = 5f;

    [Tooltip("Transparency when looking straight down at the surface (0 = fully transparent).")]
    [Range(0f, 1f)]
    [SerializeField] private float minAlpha = 0.2f;

    [Header("Interaction")]
    [Tooltip("Intensity of the wave created when dragging the cursor across the surface.")]
    [Range(0f, 1f)]
    [SerializeField] private float interactionStrength = 0.5f;

    [Tooltip("Radius of the cursor disturbance, as a fraction of the surface.")]
    [Range(0.005f, 0.2f)]
    [SerializeField] private float brushRadius = 0.03f;

    private MeshRenderer _renderer;
    private Material _material;

    private RenderTexture _heightA;
    private RenderTexture _heightB;
    private RenderTexture _normalMap;
    private int _initKernel;
    private int _stepKernel;
    private int _stepWaveKernel;
    private int _normalsKernel;
    private int _splashKernel;
    private int _groups; // dispatch groups per axis (numthreads is 8x8)
    private Camera _camera;
    private float _stepAccumulator;

    private static readonly int HeightMapId = Shader.PropertyToID("_HeightMap");
    private static readonly int NormalMapId = Shader.PropertyToID("_NormalMap");
    private static readonly int MaxWaveHeightId = Shader.PropertyToID("_MaxWaveHeight");
    private static readonly int WaterColorId = Shader.PropertyToID("_WaterColor");
    private static readonly int FresnelPowerId = Shader.PropertyToID("_FresnelPower");
    private static readonly int MinAlphaId = Shader.PropertyToID("_MinAlpha");
    private static readonly int ReflectivityId = Shader.PropertyToID("_Reflectivity");
    private static readonly int ShininessId = Shader.PropertyToID("_Shininess");

    private void Start()
    {
        GetComponent<MeshFilter>().sharedMesh = BuildGrid(resolution, surfaceSize);
        SetupMaterial();
        SetupSimulation();
    }

    private void Update()
    {
        if (simShader == null) return;
        HandleInteraction();

        // Advance the simulation at a fixed rate (decoupled from frame rate) so the
        // ripple propagation speed is controllable and frame-rate independent.
        float stepTime = 1f / Mathf.Max(1f, simulationRate);
        _stepAccumulator += Time.deltaTime;
        int steps = 0;
        while (_stepAccumulator >= stepTime && steps < 8) // cap to avoid spiral of death
        {
            StepSimulation();
            _stepAccumulator -= stepTime;
            steps++;
        }
    }

    private void OnDestroy()
    {
        if (_heightA != null) _heightA.Release();
        if (_heightB != null) _heightB.Release();
        if (_normalMap != null) _normalMap.Release();
        if (Application.isPlaying && _material != null) Destroy(_material);
    }

    // ----------------------------------------------------------------- material

    private void SetupMaterial()
    {
        _renderer = GetComponent<MeshRenderer>();
        var shader = Shader.Find("RG2/Water");
        if (shader == null)
        {
            Debug.LogError("WaterSimulation: shader 'RG2/Water' not found.");
            return;
        }
        _material = new Material(shader);
        _material.SetColor(WaterColorId, waterColor);
        _material.SetFloat(MaxWaveHeightId, maxWaveHeight);
        _renderer.sharedMaterial = _material;
    }

    // --------------------------------------------------------------- simulation

    private void SetupSimulation()
    {
        if (simShader == null)
        {
            Debug.LogError("WaterSimulation: 'Sim Shader' is not assigned " +
                           "(drag Assets/Shaders/WaterSim.compute into the field).");
            return;
        }

        _heightA = CreateHeightTexture();
        _heightB = CreateHeightTexture();
        _normalMap = CreateNormalTexture();
        _groups = Mathf.CeilToInt(heightMapSize / 8f);

        _initKernel = simShader.FindKernel("CSInit");
        _stepKernel = simShader.FindKernel("CSStep");
        _stepWaveKernel = simShader.FindKernel("CSStepWave");
        _normalsKernel = simShader.FindKernel("CSNormals");
        _splashKernel = simShader.FindKernel("CSSplash");
        _camera = Camera.main;

        // Seed both buffers identically with random values (assignment: "arbitrary values").
        // Equal buffers mean zero initial velocity for the wave-equation mode.
        simShader.SetInts("Size", heightMapSize, heightMapSize);
        simShader.SetFloat("Seed", Random.value * 1000f);
        // Wave mode starts from calm (flat) water; diffusion keeps the random "cloud" map.
        simShader.SetFloat("InitFlat", mode == SimulationMode.Wave ? 1f : 0f);
        simShader.SetTexture(_initKernel, "Current", _heightA);
        simShader.Dispatch(_initKernel, _groups, _groups, 1);
        simShader.SetTexture(_initKernel, "Current", _heightB);
        simShader.Dispatch(_initKernel, _groups, _groups, 1);

        _material.SetTexture(HeightMapId, _heightA);
    }

    private void StepSimulation()
    {
        simShader.SetInts("Size", heightMapSize, heightMapSize);
        simShader.SetFloat("DampFactor", dampFactor);
        simShader.SetFloat("RestoreFactor", restoreFactor);
        int stepKernel = mode == SimulationMode.Wave ? _stepWaveKernel : _stepKernel;
        simShader.SetTexture(stepKernel, "Current", _heightA);
        simShader.SetTexture(stepKernel, "Next", _heightB);
        simShader.Dispatch(stepKernel, _groups, _groups, 1);

        // Ping-pong: _heightB now holds the newest map.
        (_heightA, _heightB) = (_heightB, _heightA);

        // Build the normal map from the newest height map.
        simShader.SetFloat("MaxWaveHeight", maxWaveHeight);
        simShader.SetFloat("NormalStrength", normalStrength);
        simShader.SetTexture(_normalsKernel, "Current", _heightA);
        simShader.SetTexture(_normalsKernel, "Normals", _normalMap);
        simShader.Dispatch(_normalsKernel, _groups, _groups, 1);

        _material.SetTexture(HeightMapId, _heightA);
        _material.SetTexture(NormalMapId, _normalMap);
        _material.SetFloat(MaxWaveHeightId, maxWaveHeight);
        _material.SetColor(WaterColorId, waterColor);
        _material.SetFloat(FresnelPowerId, fresnelPower);
        _material.SetFloat(MinAlphaId, minAlpha);
        _material.SetFloat(ReflectivityId, reflectivity);
        _material.SetFloat(ShininessId, shininess);
    }

    /// <summary>
    /// While the left mouse button is held, raycasts the cursor onto the surface
    /// plane and injects a height bump there (the "finger through water" splash).
    /// </summary>
    private void HandleInteraction()
    {
        if (!Input.GetMouseButton(0)) return;
        if (_camera == null) _camera = Camera.main;
        if (_camera == null) return;

        // Intersect the cursor ray with the flat base plane of the surface.
        var plane = new Plane(transform.up, transform.position);
        Ray ray = _camera.ScreenPointToRay(Input.mousePosition);
        if (!plane.Raycast(ray, out float enter)) return;

        Vector3 local = transform.InverseTransformPoint(ray.GetPoint(enter));
        float u = local.x / surfaceSize + 0.5f;
        float v = local.z / surfaceSize + 0.5f;
        if (u < 0f || u > 1f || v < 0f || v > 1f) return;

        simShader.SetInts("Size", heightMapSize, heightMapSize);
        simShader.SetVector("BrushUV", new Vector4(u, v, 0f, 0f));
        simShader.SetFloat("BrushRadius", Mathf.Max(1f, brushRadius * heightMapSize));
        simShader.SetFloat("BrushStrength", interactionStrength);
        simShader.SetTexture(_splashKernel, "Current", _heightA);
        simShader.Dispatch(_splashKernel, _groups, _groups, 1);
    }

    private RenderTexture CreateHeightTexture()
    {
        var rt = new RenderTexture(heightMapSize, heightMapSize, 0, RenderTextureFormat.RFloat)
        {
            enableRandomWrite = true,
            filterMode = FilterMode.Bilinear,
            wrapMode = TextureWrapMode.Clamp
        };
        rt.Create();
        return rt;
    }

    private RenderTexture CreateNormalTexture()
    {
        var rt = new RenderTexture(heightMapSize, heightMapSize, 0, RenderTextureFormat.ARGBHalf)
        {
            enableRandomWrite = true,
            filterMode = FilterMode.Bilinear,
            wrapMode = TextureWrapMode.Clamp
        };
        rt.Create();
        return rt;
    }

    // --------------------------------------------------------------------- mesh

    /// <summary>
    /// Builds a flat (n+1)x(n+1) vertex grid in the XZ plane, centered at the
    /// local origin, with Y = 0, UVs in [0,1], and two triangles per quad.
    /// </summary>
    private static Mesh BuildGrid(int n, float size)
    {
        int verticesPerSide = n + 1;
        int vertexCount = verticesPerSide * verticesPerSide;

        var vertices = new Vector3[vertexCount];
        var uvs = new Vector2[vertexCount];
        var normals = new Vector3[vertexCount];

        float step = size / n;
        float half = size * 0.5f;

        for (int z = 0; z < verticesPerSide; z++)
        {
            for (int x = 0; x < verticesPerSide; x++)
            {
                int idx = z * verticesPerSide + x;
                vertices[idx] = new Vector3(x * step - half, 0f, z * step - half);
                uvs[idx] = new Vector2((float)x / n, (float)z / n);
                normals[idx] = Vector3.up;
            }
        }

        var triangles = new int[n * n * 6];
        int t = 0;
        for (int z = 0; z < n; z++)
        {
            for (int x = 0; x < n; x++)
            {
                int bottomLeft = z * verticesPerSide + x;
                int bottomRight = bottomLeft + 1;
                int topLeft = bottomLeft + verticesPerSide;
                int topRight = topLeft + 1;

                // Two triangles, CCW so the surface faces +Y.
                triangles[t++] = bottomLeft;
                triangles[t++] = topLeft;
                triangles[t++] = topRight;

                triangles[t++] = bottomLeft;
                triangles[t++] = topRight;
                triangles[t++] = bottomRight;
            }
        }

        var mesh = new Mesh
        {
            name = "WaterGrid",
            // Allow grids larger than 65k vertices (resolution > 254).
            indexFormat = vertexCount > 65000 ? IndexFormat.UInt32 : IndexFormat.UInt16
        };
        mesh.vertices = vertices;
        mesh.uv = uvs;
        mesh.normals = normals;
        mesh.triangles = triangles;
        mesh.RecalculateBounds();
        return mesh;
    }

    [ContextMenu("Rebuild Mesh")]
    private void RebuildMesh()
    {
        GetComponent<MeshFilter>().sharedMesh = BuildGrid(resolution, surfaceSize);
    }
}
