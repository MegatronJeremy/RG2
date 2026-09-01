#!/usr/bin/env python3
"""Is the headline quality lift an artifact of a dark scene? Re-score it on the lit pixels only.

Sponza here is lit by a sun and four torches with the three authored window-shaft spots disabled, so
most of the frame is dim: a reader looking at the figures will ask whether the raster-to-all-RT lift
is really just both renders agreeing about darkness. The reference shares the exposure, so the
comparison is sound either way, but the SIZE of the lift does depend on it.

This masks by the REFERENCE's luminance (never the technique's, which would let a technique choose
its own favourable pixels) and reports the lift over progressively brighter subsets. It reuses
quality-bench's own capture path and cached path-traced reference, so the numbers are the gate's
numbers restricted to a mask, not a separate measurement.

Writes exposure_results.json for gen_quality_tables.py. Needs a real GPU.

    py exposure_check.py [--viewpoint atrium]
"""
import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np

THESIS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = THESIS_DIR.parent / "Snowstorm-Engine"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "Scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_qb = _load("quality-bench")

LAYER_PATH = REPO_ROOT / "vcpkg" / "installed" / "x64-windows" / "bin"
RUNTIME_EXE = REPO_ROOT / "build" / "Snowstorm-Runtime" / "Debug" / "Snowstorm-Runtime.exe"
SCENE = "Projects/Sandbox/assets/scenes/Sponza.world"
FRAMES, MAXFRAMES, REF_FRAMES, TIMEOUT = 90, 200, 400, 180

RASTER = {"SS_RENDER_SHADOWS_MODE": "1", "SS_RENDER_AO_MODE": "0",
          "SS_RENDER_REFLECTIONS_MODE": "0", "SS_RENDER_GI_MODE": "0", "SS_RENDER_AA": "2"}
ALL_RT = {"SS_RENDER_SHADOWS_MODE": "2", "SS_RENDER_AO_MODE": "2",
          "SS_RENDER_REFLECTIONS_MODE": "2", "SS_RENDER_GI_MODE": "2", "SS_RENDER_AA": "2"}

# Rec.709 luma thresholds on the tonemapped image. 0 is the whole frame, the rest progressively
# discard the dim majority.
CUTS = [0.0, 0.02, 0.10, 0.25]


def luma(img):
    a = img[..., :3].astype(np.float64) / 255.0
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def masked_psnr(a, b, mask):
    d = ((a[..., :3].astype(np.float64) - b[..., :3].astype(np.float64)) / 255.0) ** 2
    sel = d[np.broadcast_to(mask[..., None], d.shape)]
    return float(10 * np.log10(1.0 / max(sel.mean(), 1e-12)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--viewpoint", default="atrium", choices=sorted(_qb.VIEWPOINTS))
    args = ap.parse_args()
    if not RUNTIME_EXE.exists():
        print(f"FAIL: {RUNTIME_EXE} not found (build it first)")
        return 1

    pose = _qb.VIEWPOINTS[args.viewpoint]
    tmp = THESIS_DIR / "tools" / ".capture-cache"
    tmp.mkdir(parents=True, exist_ok=True)

    ref, _dev, _cached = _qb.capture_reference(args.viewpoint, pose, REF_FRAMES, RUNTIME_EXE,
                                               REPO_ROOT, max(TIMEOUT, REF_FRAMES // 2 + 60),
                                               LAYER_PATH, SCENE, tmp, fresh=False)
    if ref is None:
        print("FAIL: reference capture failed")
        return 1

    caps = {}
    for name, env in (("raster", RASTER), ("all-rt", ALL_RT)):
        img, dev = _qb.run_capture({**env, **_qb.camera_env(pose)}, tmp / f"exposure_{name}",
                                   FRAMES, RUNTIME_EXE, REPO_ROOT, TIMEOUT, LAYER_PATH, SCENE,
                                   max_frames=MAXFRAMES)
        if img is None:
            print(f"FAIL: {name} capture failed")
            return 1
        caps[name] = img
        device = dev

    refL = luma(ref)
    out = {"viewpoint": args.viewpoint, "device": device,
           "darkShareBelow10Pct": round(float((refL < 0.10).mean()) * 100, 1),
           "medianLuma": round(float(np.median(refL)), 4), "cuts": []}
    print(f"{'reference pixels kept':<26}{'share':>8}{'raster':>9}{'all-RT':>9}{'lift':>8}")
    for c in CUTS:
        m = refL >= c if c > 0 else np.ones_like(refL, bool)
        r, a = masked_psnr(caps["raster"], ref, m), masked_psnr(caps["all-rt"], ref, m)
        out["cuts"].append({"minLuma": c, "sharePct": round(float(m.mean()) * 100, 1),
                            "rasterPsnr": round(r, 2), "allRtPsnr": round(a, 2),
                            "liftDb": round(a - r, 2)})
        label = "all" if c == 0 else f"luma >= {c:.2f}"
        print(f"{label:<26}{m.mean() * 100:>7.1f}%{r:>9.2f}{a:>9.2f}{a - r:>8.2f}")

    dst = THESIS_DIR / "tools" / "exposure_results.json"
    dst.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
