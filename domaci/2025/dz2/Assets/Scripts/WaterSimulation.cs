using UnityEngine;
using UnityEngine.Rendering;

/// <summary>
/// Interactive water surface simulation (RG2 DZ2).
///
/// Step (a): builds a flat triangle-grid mesh that will later be displaced in the
/// vertex shader from a runtime height map. Simulation parameters are exposed here
/// as the skeleton; they are wired into the compute shader / material in later steps.
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

    // --- Parameters below are part of the skeleton and get used in later steps. ---

    [Header("Wave simulation (step b/c)")]
    [Tooltip("Damping of the wave propagation. Lower = waves die out faster. Tune empirically.")]
    [Range(0f, 1f)]
    [SerializeField] private float dampFactor = 0.99f;

    [Tooltip("Maximum vertical displacement of the surface, in units.")]
    [SerializeField] private float maxWaveHeight = 0.5f;

    [Tooltip("Scales the slope used when building the normal map. Tune empirically.")]
    [SerializeField] private float normalStrength = 2f;

    [Header("Appearance (step c/d)")]
    [SerializeField] private Color waterColor = new Color(0.1f, 0.3f, 0.5f, 1f);

    [Header("Interaction (step e)")]
    [Tooltip("Intensity of the wave created when dragging the cursor across the surface.")]
    [SerializeField] private float interactionStrength = 1f;

    private MeshFilter _meshFilter;

    private void Start()
    {
        _meshFilter = GetComponent<MeshFilter>();
        _meshFilter.sharedMesh = BuildGrid(resolution, surfaceSize);
        EnsurePlaceholderMaterial();
    }

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

    /// <summary>
    /// Assigns a simple lit material at runtime so the surface is visible before the
    /// dedicated water shader exists. Replaced by Water.shader in a later step.
    /// </summary>
    private void EnsurePlaceholderMaterial()
    {
        var renderer = GetComponent<MeshRenderer>();
        if (renderer.sharedMaterial == null)
        {
            var shader = Shader.Find("Standard");
            if (shader != null)
            {
                renderer.sharedMaterial = new Material(shader) { color = waterColor };
            }
        }
    }

    [ContextMenu("Rebuild Mesh")]
    private void RebuildMesh()
    {
        GetComponent<MeshFilter>().sharedMesh = BuildGrid(resolution, surfaceSize);
    }
}
