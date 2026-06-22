using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// Editor utility (RG2 DZ2): procedurally generates a sky cubemap (blue gradient + sun),
/// builds a skybox material from it, and assigns it as the scene skybox. This gives the
/// water surface a vivid environment to reflect — literally the "ambient cube map" the
/// assignment asks for — without needing any external image asset.
///
/// Run via the menu: RG2 > Generate Sky Cubemap.
/// </summary>
public static class SkyboxCubemapGenerator
{
    private const int FaceSize = 128;
    private const string CubemapPath = "Assets/SkyCubemap.cubemap";
    private const string MaterialPath = "Assets/SkyboxMaterial.mat";

    [MenuItem("RG2/Generate Sky Cubemap")]
    public static void Generate()
    {
        // Sky look — tweak freely.
        Vector3 sunDir = new Vector3(0.35f, 0.45f, 0.4f).normalized;
        Color zenith = new Color(0.12f, 0.35f, 0.75f);
        Color horizon = new Color(0.70f, 0.82f, 0.95f);
        Color ground = new Color(0.20f, 0.22f, 0.25f);
        Color sunColor = new Color(3.0f, 2.8f, 2.4f); // HDR, > 1 for a bright glint
        const float sunSharpness = 600f;

        var cube = new Cubemap(FaceSize, TextureFormat.RGBAHalf, false);

        for (int face = 0; face < 6; face++)
        {
            var pixels = new Color[FaceSize * FaceSize];
            for (int y = 0; y < FaceSize; y++)
            {
                for (int x = 0; x < FaceSize; x++)
                {
                    float u = (x + 0.5f) / FaceSize * 2f - 1f;
                    float v = (y + 0.5f) / FaceSize * 2f - 1f;
                    Vector3 dir = DirectionFor((CubemapFace)face, u, v).normalized;

                    Color sky;
                    if (dir.y >= 0f)
                        sky = Color.Lerp(horizon, zenith, Mathf.Sqrt(dir.y));
                    else
                        sky = Color.Lerp(horizon, ground, Mathf.Clamp01(-dir.y * 2f));

                    float sun = Mathf.Pow(Mathf.Clamp01(Vector3.Dot(dir, sunDir)), sunSharpness);
                    sky += sunColor * sun;

                    pixels[y * FaceSize + x] = sky;
                }
            }
            cube.SetPixels(pixels, (CubemapFace)face);
        }
        cube.Apply();

        // Save / replace the cubemap asset.
        AssetDatabase.DeleteAsset(CubemapPath);
        AssetDatabase.CreateAsset(cube, CubemapPath);

        // Build (or refresh) the skybox material and assign it to the scene.
        var mat = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath);
        if (mat == null)
        {
            mat = new Material(Shader.Find("Skybox/Cubemap"));
            AssetDatabase.CreateAsset(mat, MaterialPath);
        }
        mat.SetTexture("_Tex", cube);

        RenderSettings.skybox = mat;
        AssetDatabase.SaveAssets();
        DynamicGI.UpdateEnvironment(); // refresh ambient + the default reflection probe
        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());

        Debug.Log("RG2: sky cubemap generated and assigned as scene skybox.");
    }

    // Maps a cubemap face + uv in [-1,1] to a world-space direction (standard convention).
    private static Vector3 DirectionFor(CubemapFace face, float u, float v)
    {
        switch (face)
        {
            case CubemapFace.PositiveX: return new Vector3(1f, -v, -u);
            case CubemapFace.NegativeX: return new Vector3(-1f, -v, u);
            case CubemapFace.PositiveY: return new Vector3(u, 1f, v);
            case CubemapFace.NegativeY: return new Vector3(u, -1f, -v);
            case CubemapFace.PositiveZ: return new Vector3(u, -v, 1f);
            default: return new Vector3(-u, -v, -1f); // NegativeZ
        }
    }
}
