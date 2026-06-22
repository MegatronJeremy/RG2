using UnityEngine;
using UnityEngine.Rendering;

/// <summary>
/// Interactive water surface simulation (RG2 DZ2).
///
/// Step (a): flat triangle grid.
/// Step (b): every frame a compute shader rebuilds the height map (ping-pong between
/// two RFloat render textures); the water shader displaces vertices from that map.
/// Normals, reflection, transparency and cursor interaction follow in later steps.
/// </summary>
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
    [Tooltip("Damping of the relaxation. 0 = frozen, 1 = instantly smoothed. Tune empirically.")]
    [Range(0f, 1f)]
    [SerializeField] private float dampFactor = 0.5f;

    [Tooltip("Maximum vertical displacement of the surface, in units.")]
    [SerializeField] private float maxWaveHeight = 0.5f;

    [Tooltip("Scales the slope used when building the normal map (step c). Tune empirically.")]
    [SerializeField] private float normalStrength = 2f;

    [Header("Appearance")]
    [SerializeField] private Color waterColor = new Color(0.1f, 0.3f, 0.5f, 1f);

    [Header("Interaction (step e)")]
    [Tooltip("Intensity of the wave created when dragging the cursor across the surface.")]
    [SerializeField] private float interactionStrength = 1f;

    private MeshRenderer _renderer;
    private Material _material;

    private RenderTexture _heightA;
    private RenderTexture _heightB;
    private int _initKernel;
    private int _stepKernel;
    private int _groups; // dispatch groups per axis (numthreads is 8x8)

    private static readonly int HeightMapId = Shader.PropertyToID("_HeightMap");
    private static readonly int MaxWaveHeightId = Shader.PropertyToID("_MaxWaveHeight");
    private static readonly int WaterColorId = Shader.PropertyToID("_WaterColor");

    private void Start()
    {
        GetComponent<MeshFilter>().sharedMesh = BuildGrid(resolution, surfaceSize);
        SetupMaterial();
        SetupSimulation();
    }

    private void Update()
    {
        if (simShader == null) return;
        StepSimulation();
    }

    private void OnDestroy()
    {
        if (_heightA != null) _heightA.Release();
        if (_heightB != null) _heightB.Release();
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
        _groups = Mathf.CeilToInt(heightMapSize / 8f);

        _initKernel = simShader.FindKernel("CSInit");
        _stepKernel = simShader.FindKernel("CSStep");

        // Seed the initial height map with random values.
        simShader.SetInts("Size", heightMapSize, heightMapSize);
        simShader.SetFloat("Seed", Random.value * 1000f);
        simShader.SetTexture(_initKernel, "Current", _heightA);
        simShader.Dispatch(_initKernel, _groups, _groups, 1);

        _material.SetTexture(HeightMapId, _heightA);
    }

    private void StepSimulation()
    {
        simShader.SetInts("Size", heightMapSize, heightMapSize);
        simShader.SetFloat("DampFactor", dampFactor);
        simShader.SetTexture(_stepKernel, "Current", _heightA);
        simShader.SetTexture(_stepKernel, "Next", _heightB);
        simShader.Dispatch(_stepKernel, _groups, _groups, 1);

        // Ping-pong: _heightB now holds the newest map.
        (_heightA, _heightB) = (_heightB, _heightA);

        _material.SetTexture(HeightMapId, _heightA);
        _material.SetFloat(MaxWaveHeightId, maxWaveHeight);
        _material.SetColor(WaterColorId, waterColor);
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
