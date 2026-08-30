#!/usr/bin/env python3
"""Does a-trous tap stride drive the cross-vendor cost ratio? A 2x2 control.

The committed baselines show the AMD/NVIDIA per-pass ratio INVERTING along the GI and AO a-trous
chains (iteration 0 ~1.40, iteration 2 ~0.71, replicated in six independent chains across five
configs with quartiles under 0.01 ms). The shadow chain, running the SAME shader, is flat at
0.63-0.67. Two things differ there and the baselines cannot separate them:

  penumbra  render.shadows.denoise.penumbra > 0 makes the tap stride per-pixel and data-dependent
            (kStep = Step * lerp(0.4, 2.2, penumbra)), so shadows never see the clean 1/2/4
            geometric progression that GI and AO do. Setting it to 0 restores a uniform kernel.
  scale     shadows trace and denoise at full resolution (render.shadows.scale 1.0) while GI and AO
            run at half (0.5), so the shadow chain also works on 4x the pixels.

This runs both factors independently. If stride is the mechanism, the inversion appears whenever
penumbra is 0 regardless of resolution; if the working-set size is, it tracks scale instead.

Not a gate: prints a table and writes stride_results.json. Needs a real GPU, one run per adapter.

    py stride_sweep.py [--gpu 9070]
"""
import argparse
import importlib.util
import json
from pathlib import Path

THESIS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = THESIS_DIR.parent / "Snowstorm-Engine"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "Scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_pb = _load("perf-bench")

BUILD_DIR = REPO_ROOT / "build"
LAYER_PATH = REPO_ROOT / "vcpkg" / "installed" / "x64-windows" / "bin"
EDITOR_EXE = BUILD_DIR / "Snowstorm-Editor" / "Debug" / "Snowstorm-Editor.exe"
SCENE = "Projects/Sandbox/assets/scenes/Sponza.world"

PERF_FRAMES, PERF_TIMEOUT = 300, 120

# Stochastic shadows only, so the ShadowDenoise chain exists at all. Everything else off, matching
# the shadows-stoch rung the committed baselines use.
STOCH = {"SS_RENDER_SHADOWS_MODE": "2", "SS_RENDER_AO_MODE": "0",
         "SS_RENDER_REFLECTIONS_MODE": "0", "SS_RENDER_GI_MODE": "0",
         "SS_RENDER_SHADOWS_STOCHASTIC": "1"}

# The 2x2. "default" reproduces the committed shadows-stoch row as a sanity check.
ARMS = [
    ("default",        {"SS_RENDER_SHADOWS_DENOISE_PENUMBRA": "0.1", "SS_RENDER_SHADOWS_SCALE": "1.0"}),
    ("uniform-full",   {"SS_RENDER_SHADOWS_DENOISE_PENUMBRA": "0",   "SS_RENDER_SHADOWS_SCALE": "1.0"}),
    ("uniform-half",   {"SS_RENDER_SHADOWS_DENOISE_PENUMBRA": "0",   "SS_RENDER_SHADOWS_SCALE": "0.5"}),
    ("penumbra-half",  {"SS_RENDER_SHADOWS_DENOISE_PENUMBRA": "0.1", "SS_RENDER_SHADOWS_SCALE": "0.5"}),
]

CHAIN = ("ShadowDenoise0", "ShadowDenoise1", "ShadowDenoise2")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu", default="", help="adapter index or name substring")
    args = ap.parse_args()

    if not EDITOR_EXE.exists():
        print(f"FAIL: {EDITOR_EXE} not found (build it first)")
        return 1

    out = {"device": None, "arms": []}
    for name, knobs in ARMS:
        env = {**STOCH, **knobs}
        print(f"\n=== {name}  penumbra={knobs['SS_RENDER_SHADOWS_DENOISE_PENUMBRA']} "
              f"scale={knobs['SS_RENDER_SHADOWS_SCALE']} ===")
        r = _pb.run_config(f"stride_{name}", env, EDITOR_EXE, REPO_ROOT, PERF_FRAMES,
                           PERF_TIMEOUT, LAYER_PATH, SCENE, args.gpu)
        if r is None or r is _pb.NO_TIMESTAMPS:
            print("  FAIL: run produced no timings")
            return 1
        out["device"] = out["device"] or r.get("device")
        passes = r.get("passes", {})
        row = {"arm": name, **{k.replace("SS_RENDER_SHADOWS_", "").lower(): v for k, v in knobs.items()},
               "totalGpuMs": r.get("totalGpuMs"),
               "chain": {p: passes[p]["avgMs"] for p in CHAIN if p in passes}}
        out["arms"].append(row)
        print("  " + "  ".join(f"{p}={row['chain'].get(p, float('nan')):.4f}" for p in CHAIN))

    dst = THESIS_DIR / "tools" / "stride_results.json"
    dst.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\ndevice: {out['device']}")
    print(f"wrote {dst}")
    print("\nPair this with the same file from the other adapter to get the ratio per arm.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
