using System;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

/// <summary>
/// Editor utility (RG2 DZ2): builds a standalone Windows player containing the water scene.
/// Invoked from run.ps1 via -executeMethod, and available from the menu as RG2 > Build Player.
///
/// The scene list is passed explicitly, so ProjectSettings/EditorBuildSettings.asset stays empty
/// and the build works on a fresh checkout without anyone configuring Build Settings first.
/// </summary>
public static class PlayerBuild
{
    private const string ScenePath = "Assets/Scenes/Water.unity";
    private const string DefaultOutput = "Build/DZ2.exe";

    [MenuItem("RG2/Build Player")]
    public static void BuildFromMenu()
    {
        BuildReport report = RunBuild(DefaultOutput);
        if (report.summary.result != BuildResult.Succeeded)
        {
            Debug.LogError($"RG2: build failed ({report.summary.result}).");
        }
    }

    /// <summary>
    /// Batch-mode entry point. Output path comes from -buildOutput &lt;path&gt; when given,
    /// otherwise <see cref="DefaultOutput"/>. Exits with a non-zero code on failure so the
    /// calling script can tell success from failure without scraping the log.
    /// </summary>
    public static void BuildFromCommandLine()
    {
        string output = ArgumentValue("-buildOutput") ?? DefaultOutput;
        BuildReport report = RunBuild(output);
        BuildSummary summary = report.summary;

        Debug.Log($"RG2 build: result={summary.result} errors={summary.totalErrors} " +
                  $"warnings={summary.totalWarnings} output={output}");

        EditorApplication.Exit(summary.result == BuildResult.Succeeded ? 0 : 1);
    }

    private static BuildReport RunBuild(string outputPath)
    {
        var options = new BuildPlayerOptions
        {
            scenes = new[] { ScenePath },
            locationPathName = outputPath,
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.None
        };

        return BuildPipeline.BuildPlayer(options);
    }

    private static string ArgumentValue(string flag)
    {
        string[] args = Environment.GetCommandLineArgs();
        for (int i = 0; i < args.Length - 1; i++)
        {
            if (args[i] == flag)
            {
                return args[i + 1];
            }
        }
        return null;
    }
}
