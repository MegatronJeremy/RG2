#!/usr/bin/env python3
"""Half- versus full-resolution GI/AO tracing, for thesis sec:halfres (Table 4.6).

That table was previously typed by hand from a sweep whose output was never committed, so its numbers
could not be rechecked and one of them (a +54% that should have been +56%) had already drifted from
its own cells. This measures the pair and writes halfres_results.json, which gen_quality_tables.py
turns into the table, so the thesis and the measurement cannot separate again.

One variable: render.gi.scale and render.ao.scale, 0.5 (shipped) against 1.0. Everything else is the
all-RT configuration. Quality is the atrium viewpoint against the cached path-traced reference, which
is the same reference quality-bench uses; cost is the +gi rung measured by perf-bench's run_config,
whole-frame and per-pass.

Not a gate: it prints a table and writes JSON.

    py halfres_sweep.py
"""
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


_qb = _load("quality-bench")
_pb = _load("perf-bench")

BUILD_DIR = REPO_ROOT / "build"
LAYER_PATH = REPO_ROOT / "vcpkg" / "installed" / "x64-windows" / "bin"
RUNTIME_EXE = BUILD_DIR / "Snowstorm-Runtime" / "Debug" / "Snowstorm-Runtime.exe"
EDITOR_EXE = BUILD_DIR / "Snowstorm-Editor" / "Debug" / "Snowstorm-Editor.exe"
SCENE = "Projects/Sandbox/assets/scenes/Sponza.world"

ATRIUM = {"pos": [8.519126892089844, 1.4949023723602295, -0.4308139383792877],
          "rot": [0.027, 1.496, 0.0]}

ALL_RT = {"SS_RENDER_SHADOWS_MODE": "2", "SS_RENDER_AO_MODE": "2",
          "SS_RENDER_REFLECTIONS_MODE": "2", "SS_RENDER_GI_MODE": "2"}

TECH_FRAMES, TECH_MAXFRAMES, REF_FRAMES = 90, 200, 400
TIMEOUT, PERF_FRAMES, PERF_TIMEOUT = 180, 300, 120

# the passes whose cost the resolution change is supposed to move
TRACE_PASSES = ("GI", "AO")


def main() -> int:
    for exe in (RUNTIME_EXE, EDITOR_EXE):
        if not exe.exists():
            print(f"FAIL: {exe} not found (build it first)")
            return 1

    tmp = THESIS_DIR / "tools" / ".capture-cache"
    tmp.mkdir(parents=True, exist_ok=True)

    print("=== reference (path traced) ===")
    ref, ref_dev, cached = _qb.capture_reference("atrium", ATRIUM, REF_FRAMES, RUNTIME_EXE,
                                                 REPO_ROOT, max(TIMEOUT, REF_FRAMES // 2 + 60),
                                                 LAYER_PATH, SCENE, tmp, fresh=False)
    if ref is None:
        print("FAIL: reference capture failed")
        return 1
    print(f"  {'cached' if cached else 'captured'}, device={ref_dev or '(cached)'}")

    out = {"viewpoint": "atrium", "device": None, "scales": []}
    for scale in ("0.5", "1.0"):
        env = {**ALL_RT, "SS_RENDER_GI_SCALE": scale, "SS_RENDER_AO_SCALE": scale}
        print(f"\n=== gi.scale = ao.scale = {scale} ===")

        img, dev = _qb.run_capture({**env, "SS_RENDER_AA": "2", **_qb.camera_env(ATRIUM)},
                                   tmp / f"halfres_{scale}", TECH_FRAMES, RUNTIME_EXE, REPO_ROOT,
                                   TIMEOUT, LAYER_PATH, SCENE, max_frames=TECH_MAXFRAMES)
        if img is None:
            print("  FAIL: capture failed")
            return 1
        out["device"] = out["device"] or dev
        psnr, ssim = _qb.psnr(img, ref), _qb.ssim(img, ref)
        flip = _qb.flip(img, ref)

        perf = _pb.run_config(f"halfres_{scale}", {**env, "SS_RENDER_AA": "2"}, EDITOR_EXE,
                              REPO_ROOT, PERF_FRAMES, PERF_TIMEOUT, LAYER_PATH, SCENE, "")
        passes = (perf or {}).get("passes", {})
        row = {
            "scale": float(scale),
            "psnr": psnr, "ssim": ssim, "flip": flip,
            "gpu_total_ms": (perf or {}).get("totalGpuMs"),
            "passes": {p: passes[p]["avgMs"] for p in TRACE_PASSES if p in passes},
        }
        out["scales"].append(row)
        print(f"  PSNR {psnr:.2f}  SSIM {ssim:.4f}  FLIP {flip:.4f}  "
              f"total {row['gpu_total_ms']} ms  {row['passes']}")

    dst = THESIS_DIR / "tools" / "halfres_results.json"
    dst.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nwrote {dst.name}")

    half, full = out["scales"]
    d = full["gpu_total_ms"] - half["gpu_total_ms"]
    print(f"full-res costs {d:.2f} ms more, {100 * d / half['gpu_total_ms']:.0f}%, "
          f"for {full['psnr'] - half['psnr']:+.2f} dB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
