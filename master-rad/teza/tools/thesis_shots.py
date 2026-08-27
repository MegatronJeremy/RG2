#!/usr/bin/env python3
"""Captures every rendered figure in the thesis into latex/figures/. Reuses the engine's
quality-bench.py run_capture/camera_env (headless Snowstorm-Runtime.exe, env-var CVar overrides,
.npy readback), so a figure is reproduced by the same path the quality gate measures.

Lives in the thesis rather than in the engine because which shots the thesis needs is thesis
knowledge: the engine submodule is standalone and must not reach up into its parent.
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np

THESIS_DIR = Path(__file__).resolve().parents[1]           # master-rad/teza
REPO_ROOT = THESIS_DIR.parent / "Snowstorm-Engine"          # the engine submodule

_spec = importlib.util.spec_from_file_location("quality_bench", REPO_ROOT / "Scripts" / "quality-bench.py")
_qb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_qb)
run_capture, camera_env = _qb.run_capture, _qb.camera_env

FIG_DIR = THESIS_DIR / "latex" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

BUILD_DIR = REPO_ROOT / "build"
LAYER_PATH = REPO_ROOT / "vcpkg" / "installed" / "x64-windows" / "bin"
EXE = BUILD_DIR / "Snowstorm-Runtime" / "Debug" / "Snowstorm-Runtime.exe"
SCENE = "Projects/Sandbox/assets/scenes/Sponza.world"

# rot is [pitch, yaw, roll] in radians. POSITIVE PITCH LOOKS UP: TransformComponent builds Y*X*Z
# against a -Z forward, giving forward.y = sin(pitch). The names below say what is actually framed.
ATRIUM = {"pos": [8.519126892089844, 1.4949023723602295, -0.4308139383792877], "rot": [0.027, 1.496, 0.0]}
CEILING = {"pos": [8.519126892089844, 1.4949023723602295, -0.4308139383792877], "rot": [0.55, 1.496, 0.0]}
FLOOR = {"pos": [8.519126892089844, 1.4949023723602295, -0.4308139383792877], "rot": [-0.5, 1.496, 0.0]}
# Frames the sunlit floor strip and its transverse edge, the one shadow boundary in the scene with a
# long occluder-to-receiver throw (the roof light-well lip, ~10.4 units up).
SUNSTRIP = {"pos": [8.519126892089844, 1.4949023723602295, -0.4308139383792877], "rot": [-0.35, 1.496, 0.0]}
# Shallow pitch: the arcade recedes across most of the frame, which maximises the grazing-angle
# specular where RT reflections differ most from the prefiltered-environment fallback.
GRAZING = {"pos": [8.519126892089844, 1.4949023723602295, -0.4308139383792877], "rot": [0.22, 1.496, 0.0]}

BASE_ENV = {"SS_RENDER_AA": "2"}
ALL_RT = {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "2", "SS_RENDER_AO_MODE": "2",
          "SS_RENDER_REFLECTIONS_MODE": "2", "SS_RENDER_GI_MODE": "2"}
TECH_FRAMES = 90
TECH_MAXFRAMES = 200
REF_FRAMES = 400

# name, viewpoint, env overrides, is_reference
SHOTS = [
    ("teaser", ATRIUM, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "2", "SS_RENDER_AO_MODE": "2",
                        "SS_RENDER_REFLECTIONS_MODE": "2", "SS_RENDER_GI_MODE": "2"}, False),
    # Penumbra width is 2*H*tan(theta/2) in the source's angular size theta, so it needs a receiver with
    # a distant occluder H. The sun is the only light in Sponza that has one: the other four enabled
    # lights are torches a couple of units from the walls they light. Hence the sunlit floor strip, whose
    # transverse edge is cast by the roof light-well lip ~10.4 units up.
    #
    # render.shadow.source_radius stays at its 0.1 default. Widening it does move the frame a lot, but
    # most of that is not penumbra: DefaultLit.frag.hlsl:179-185 skips cone samples below the shading
    # normal's horizon while :207 still divides by the full SHADOW_RAY_COUNT, so a wider cone
    # systematically darkens grazing surfaces. At a 1.5-unit radius that wash is 75% of the total
    # difference (signed mean -1.20: soft darker on 22% of pixels against lighter on 8%). Driving the sun
    # keeps the sign right (+1.46, lighter on 7.5% against darker on 5.2%) since the near-vertical sun
    # meets the floor at dot(N,dir) ~ 1, where nothing is horizon-rejected.
    #
    # 3 degrees is ~6x the sun's real 0.53 and is a deliberate didactic exaggeration: at the physical
    # angle the penumbra on this edge is ~36 px of a 2560-wide capture, invisible once scaled into the
    # page. The caption states the value.
    #
    # render.shadows.rays is not set: SHADOW_RAY_COUNT is a compile-time #define
    # (DefaultLit.frag.hlsl:152), and the CVar feeds only the stochastic pass (ViewportEffects.cpp:982),
    # which render.shadows.stochastic leaves off by default, so mode 2 runs the inline path and ignores it.
    ("shadow_hard", SUNSTRIP, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "2",
                               "SS_RENDER_SHADOW_SUN_ANGLE_DEG": "3.0", "SS_RENDER_SHADOW_SOFT": "0"}, False),
    ("shadow_soft", SUNSTRIP, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "2",
                               "SS_RENDER_SHADOW_SUN_ANGLE_DEG": "3.0", "SS_RENDER_SHADOW_SOFT": "1"}, False),
    # The cone A/B is invisible in a COMPOSITED frame (cone_scale 0 vs 3 moves 0.16/255 at the best of
    # six poses tried) because the reflection is a small additive term next to direct lighting. In the
    # raw reflection buffer it is the dominant signal: the same A/B moves 44.1/255 and drops
    # high-frequency energy from 16.1 to 8.8. Same lesson as the effect gallery: isolate the signal.
    ("cone_sharp", GRAZING, {**BASE_ENV, "SS_RENDER_REFLECTIONS_MODE": "2", "SS_RENDER_DEBUGVIEW": "3",
                             "SS_RENDER_REFLECTIONS_MAX_ROUGHNESS": "1.0",
                             "SS_RENDER_REFLECTIONS_CONE_SCALE": "0"}, False),
    ("cone_glossy", GRAZING, {**BASE_ENV, "SS_RENDER_REFLECTIONS_MODE": "2", "SS_RENDER_DEBUGVIEW": "3",
                              "SS_RENDER_REFLECTIONS_MAX_ROUGHNESS": "1.0",
                              "SS_RENDER_REFLECTIONS_CONE_SCALE": "3"}, False),
    # These four isolate ONE effect, so everything else should be the configuration the thesis
    # recommends rather than whatever the defaults happen to be. Shadows are traced here: the raster
    # path caps at MAX_SHADOW_POINTS = 2 while Sponza has four enabled shadow-casting point lights, so
    # leaving it at the default renders two torches with no shadow at all and puts an artifact in a
    # figure whose subject is something else entirely.
    ("refl_off", GRAZING, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "2"}, False),
    ("refl_rt", GRAZING, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "2",
                          "SS_RENDER_REFLECTIONS_MODE": "2",
                          "SS_RENDER_REFLECTIONS_MAX_ROUGHNESS": "1.0"}, False),
    ("gi_off", ATRIUM, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "2"}, False),
    ("gi_on", ATRIUM, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "2",
                       "SS_RENDER_GI_MODE": "2"}, False),
    ("pt_ref", ATRIUM, {"SS_RENDER_PATHTRACE": "1", "SS_RENDER_PATHTRACE_CLAMP": "0",
                        "SS_RENDER_PATHTRACE_WEIGHTCLAMP": "0"}, True),

    # render.debugview writes its overlay through the same LDR chain as the beauty pass, so every mode
    # is capturable headlessly. Modes 6/7 and 8/9 are raw-vs-denoised pairs of the SAME buffer, which
    # is the denoiser's contribution as an image rather than as a table row.
    ("dbg_ao", ATRIUM, {**ALL_RT, "SS_RENDER_DEBUGVIEW": "2"}, False),
    ("dbg_refl", ATRIUM, {**ALL_RT, "SS_RENDER_DEBUGVIEW": "3"}, False),
    ("dbg_gi", ATRIUM, {**ALL_RT, "SS_RENDER_DEBUGVIEW": "4"}, False),
    ("dbg_normals", ATRIUM, {**ALL_RT, "SS_RENDER_DEBUGVIEW": "5"}, False),
    # The half- versus full-resolution GI trace, shown on the buffer itself rather than on the
    # composited frame, where the difference is not measurable. Both scales are named explicitly even
    # though gi_halfres duplicates dbg_gi_raw's config today: the pair has to stay a controlled A/B if
    # the default gi.scale ever moves, and reusing dbg_gi_raw would silently relabel whatever the new
    # default is as "half".
    ("gi_halfres", ATRIUM, {**ALL_RT, "SS_RENDER_DEBUGVIEW": "6", "SS_RENDER_GI_SCALE": "0.5"}, False),
    ("gi_fullres", ATRIUM, {**ALL_RT, "SS_RENDER_DEBUGVIEW": "6", "SS_RENDER_GI_SCALE": "1.0"}, False),

    # Screen-space against ray-traced in the RAW effect buffer rather than the composited frame. The
    # composited pair (ss_all/rt_all) is dominated by direct lighting, so the off-screen error that is
    # the whole point of tracing is a few grey levels there; the debug views isolate the term itself.
    # SSR writes the same full-res ReflectionTarget as the RT path, so debug view 3 shows both.
    # max_roughness stays at its 0.8 default here. Forcing it to 1.0 puts SSR on every surface
    # including ones whose march cannot hit anything, and its miss path falls back to the prefiltered
    # env cube, so the buffer goes near-white: that is the override talking, not the technique.
    ("ssvsrt_ssr", GRAZING, {**BASE_ENV, "SS_RENDER_REFLECTIONS_MODE": "1",
                             "SS_RENDER_DEBUGVIEW": "3"}, False),
    ("ssvsrt_rtrefl", GRAZING, {**BASE_ENV, "SS_RENDER_REFLECTIONS_MODE": "2",
                                "SS_RENDER_DEBUGVIEW": "3"}, False),
    # These two back a statistic rather than a figure. The isolated AO term is median 255 of 255 over
    # this view with only 14.1% (SSAO) and 17.6% (RT AO) of pixels below 240, which is what makes the
    # near-parity FLIP result unsurprising. As an image the pair is near-white and unreadable in print,
    # so section sec:poredjenje quotes the numbers and shows nothing; they are captured so the numbers
    # can be recomputed rather than taken on trust.
    ("ssvsrt_ssao", ATRIUM, {**BASE_ENV, "SS_RENDER_AO_MODE": "1", "SS_RENDER_DEBUGVIEW": "2"}, False),
    ("ssvsrt_rtao", ATRIUM, {**BASE_ENV, "SS_RENDER_AO_MODE": "2", "SS_RENDER_DEBUGVIEW": "2"}, False),

    # The raster shadow fallback against the traced one, at the same pose. Chapter 3 asserts the
    # difference (full-res exact visibility, cost linear in light count) and never shows it.
    ("shadow_map", SUNSTRIP, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "1"}, False),
    ("shadow_rt", SUNSTRIP, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "2"}, False),

    ("dbg_gi_raw", ATRIUM, {**ALL_RT, "SS_RENDER_DEBUGVIEW": "6"}, False),
    ("dbg_gi_denoised", ATRIUM, {**ALL_RT, "SS_RENDER_DEBUGVIEW": "7"}, False),
    ("dbg_shadow_raw", ATRIUM, {**ALL_RT, "SS_RENDER_SHADOWS_STOCHASTIC": "1",
                                "SS_RENDER_DEBUGVIEW": "8"}, False),
    ("dbg_shadow_denoised", ATRIUM, {**ALL_RT, "SS_RENDER_SHADOWS_STOCHASTIC": "1",
                                     "SS_RENDER_DEBUGVIEW": "9"}, False),

    # Two COMPLETE configurations at one pose, not one variable held against three. Shadows differ
    # with the rest because screen space has no analogue of a traced shadow: the shadow map is what
    # that family actually ships. Matching quality-bench's own matrix, where all-rt is the only
    # technique that overrides render.shadows.mode, keeps this pair and the all-RT row of the quality
    # table describing the same renderer.
    ("ss_all", ATRIUM, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "1", "SS_RENDER_AO_MODE": "1",
                        "SS_RENDER_REFLECTIONS_MODE": "1", "SS_RENDER_GI_MODE": "1"}, False),
    ("rt_all", ATRIUM, {**BASE_ENV, "SS_RENDER_SHADOWS_MODE": "2", "SS_RENDER_AO_MODE": "2",
                        "SS_RENDER_REFLECTIONS_MODE": "2", "SS_RENDER_GI_MODE": "2"}, False),

    # Debug view 1 is identically black under a pinned camera, since nothing moves, so this is the one
    # shot that needs camera.path (a deterministic orbit) instead of a fixed pose. pose=None leaves
    # SS_CAMERA_OVERRIDE unset so the orbit is not fighting a pinned pose. camera.path.fixed steps at a
    # fixed 60 Hz, so frame N is the same pose and the same velocity magnitude on every run, and the
    # hard 60-frame cap below picks a point where the orbit faces down the arcade rather than a wall.
    ("dbg_motion", None, {**BASE_ENV, "SS_CAMERA_PATH": "1", "SS_CAMERA_PATH_FIXED": "1",
                          "SS_RENDER_DEBUGVIEW": "1"}, False),
]

# Shots whose capture must be cut off at a chosen frame rather than allowed to settle. A moving camera
# never converges, so without a cap the run burns to the engine's 3000-frame safety limit and lands on
# an arbitrary pose.
MAXFRAMES_OVERRIDE = {"dbg_motion": 60}


def save_png(img: np.ndarray, path: Path):
    from PIL import Image
    arr = np.clip(img[..., :3], 0, 255).astype(np.uint8)
    Image.fromarray(arr, mode="RGB").save(path)


def main() -> int:
    if not EXE.exists():
        print(f"FAIL: {EXE} not found (build Snowstorm-Runtime first)")
        return 1
    tmp = THESIS_DIR / "tools" / ".capture-cache"
    tmp.mkdir(parents=True, exist_ok=True)
    ok = True
    for name, pose, env, is_ref in SHOTS:
        print(f"capturing {name} ...")
        env_full = {**env, **camera_env(pose)}
        frames = REF_FRAMES if is_ref else TECH_FRAMES
        max_frames = 0 if is_ref else TECH_MAXFRAMES
        if name in MAXFRAMES_OVERRIDE:
            frames, max_frames = 2, MAXFRAMES_OVERRIDE[name]
        img, device = run_capture(env_full, tmp / name, frames, EXE, REPO_ROOT,
                                   180, LAYER_PATH, SCENE, max_frames=max_frames)
        if img is None:
            print(f"  FAIL: {name} capture failed")
            ok = False
            continue
        out_png = FIG_DIR / f"{name}.png"
        save_png(img, out_png)
        print(f"  OK -> {out_png} (device={device})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
