using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

/// <summary>
/// Editor utility (RG2 DZ2): opens the water scene. Called by run.ps1 through -executeMethod,
/// because Unity has no command line flag that opens a scene; without it a fresh checkout
/// starts on an empty "Untitled" scene and the water is nowhere to be seen.
/// </summary>
public static class SceneLauncher
{
    private const string ScenePath = "Assets/Scenes/Water.unity";

    [MenuItem("RG2/Open Water Scene")]
    public static void OpenWaterScene()
    {
        if (EditorSceneManager.GetActiveScene().path == ScenePath)
        {
            return;
        }

        EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo();
        EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        Debug.Log($"RG2: opened {ScenePath}.");
    }
}
