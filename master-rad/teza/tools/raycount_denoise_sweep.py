#!/usr/bin/env python3
"""One-off sweep for thesis sec:raycount + sec:denoise-eval. Reuses quality-bench.py's
run_capture/camera_env/psnr/ssim/flip/capture_reference and perf-bench.py's run_config
(both imported dynamically, same pattern as thesis_shots.py).

Two independent measurements, both against the GI effect (render.gi.*):

1. Raycount sweep (sec:raycount): at each of SS_RENDER_GI_RAYS in {1,2,4,8}, with the shipped
   realistic pipeline (denoiser + temporal accumulation ON, TAA ON, settled at 90 frames),
   measure PSNR/SSIM vs the path-traced reference and the GPU ms of the +gi rung (perf-bench
   run_config). This is the "knee" data: quality/cost against ray count on the pipeline as it
   ships, not raw noise.
   Separately captures 4 screenshots at 1/2/4/8 rays with the denoiser AND temporal accumulation
   forced OFF and only 2 frames run, to show raw per-frame noise before any reconstruction --
   with either denoiser or temporal on, 90 frames would look mostly clean and defeat the point
   of the figure.

2. Denoiser eval (sec:denoise-eval): at a fixed GI ray count (2, the engine default), isolates
   the spatial SVGF denoiser's own contribution:
   - FLIP/PSNR/SSIM for denoiser off vs on, BOTH settled at 90 frames with temporal accumulation
     ON in both -- this isolates the spatial denoiser from the temporal accumulation, which stays
     constant across the A/B.
   - Denoiser GPU cost: perf-bench run_config A/B on SS_RENDER_GI_DENOISE with GI otherwise on.
   - Temporal-stability proxy: this repo's capture pipeline dumps one settled frame per run, not
     a video, so there is no motion sequence to diff. As a stand-in, capture the SAME static view
     at frame N and frame N+1 (two independent runs) and report the RMS delta between them, for
     denoiser on vs off. This measures frame-to-frame flicker at steady state under a STATIC
     camera, not stability under camera motion; report it as that, not as a full motion metric.
   - Three stacked screenshots: noisy (denoiser+temporal off, 2 frames), denoised (settled, 90
     frames), reference (path traced, reused from the cached pt_ref).

Not a gate: prints a results table + writes PNGs into teza/latex/figures/ + a JSON dump for
reproducibility.
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

THESIS_DIR = Path(__file__).resolve().parents[1]           # master-rad/teza
REPO_ROOT = THESIS_DIR.parent / "Snowstorm-Engine"          # the engine submodule


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "Scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_qb = _load("quality-bench")
_pb = _load("perf-bench")

FIG_DIR = THESIS_DIR / "latex" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

BUILD_DIR = REPO_ROOT / "build"
LAYER_PATH = REPO_ROOT / "vcpkg" / "installed" / "x64-windows" / "bin"
RUNTIME_EXE = BUILD_DIR / "Snowstorm-Runtime" / "Debug" / "Snowstorm-Runtime.exe"
EDITOR_EXE = BUILD_DIR / "Snowstorm-Editor" / "Debug" / "Snowstorm-Editor.exe"
SCENE = "Projects/Sandbox/assets/scenes/Sponza.world"

ATRIUM = {"pos": [8.519126892089844, 1.4949023723602295, -0.4308139383792877], "rot": [0.027, 1.496, 0.0]}

TECH_FRAMES = 90
TECH_MAXFRAMES = 200
REF_FRAMES = 400
# Raw-noise screenshots. quality.capture.frames is the minimum SETTLE, not a cap, and the pass
# captures on epsilon convergence, so a noise shot also needs a hard maxframes cap or it waits for
# the image to stop moving. TAA must be off too: it is a temporal accumulator, and left on it
# averages away the very noise the figure exists to show (measured: high-frequency energy 5.9 with
# TAA on, i.e. identical to the denoised image, against 10.6 with it off).
NOISE_FRAMES = 2
NOISE_MAXFRAMES = 30
NOISE_ENV = {"SS_RENDER_AA": "0", "SS_RENDER_GI_DENOISE": "0", "SS_RENDER_GI_TEMPORAL": "0"}

TIMEOUT = 180
PERF_FRAMES = 300
PERF_TIMEOUT = 120


def save_png(img: np.ndarray, path: Path):
    from PIL import Image
    arr = np.clip(img[..., :3], 0, 255).astype(np.uint8)
    Image.fromarray(arr, mode="RGB").save(path)


def rms(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a[..., :3] - b[..., :3]) ** 2)))


def capture_quality(env: dict, name: str, frames: int, max_frames: int, tmp: Path):
    full_env = {**env, **_qb.camera_env(ATRIUM)}
    img, device = _qb.run_capture(full_env, tmp / name, frames, RUNTIME_EXE, REPO_ROOT,
                                  TIMEOUT, LAYER_PATH, SCENE, max_frames=max_frames)
    return img, device


def gpu_ms_for(env: dict, name: str) -> dict | None:
    return _pb.run_config(name, {**env, "SS_RENDER_AA": "2"}, EDITOR_EXE, REPO_ROOT,
                          PERF_FRAMES, PERF_TIMEOUT, LAYER_PATH, SCENE, "")


def main() -> int:
    if not RUNTIME_EXE.exists():
        print(f"FAIL: {RUNTIME_EXE} not found (build Snowstorm-Runtime first)")
        return 1
    if not EDITOR_EXE.exists():
        print(f"FAIL: {EDITOR_EXE} not found (build Snowstorm-Editor first)")
        return 1

    tmp = THESIS_DIR / "tools" / ".capture-cache"
    tmp.mkdir(parents=True, exist_ok=True)

    results = {"raycount": [], "denoise_eval": {}}

    print("=== reference (path traced) ===")
    ref_img, ref_dev, cached = _qb.capture_reference("atrium", ATRIUM, REF_FRAMES, RUNTIME_EXE,
                                                      REPO_ROOT, max(TIMEOUT, REF_FRAMES // 2 + 60),
                                                      LAYER_PATH, SCENE, tmp, fresh=False)
    if ref_img is None:
        print("FAIL: reference capture failed")
        return 1
    print(f"  {'cached' if cached else 'captured'}, device={ref_dev or '(cached)'}")

    # ---- 1. raycount sweep -----------------------------------------------------------------
    print("\n=== raycount sweep (sec:raycount): quality + GPU ms vs GI rays ===")
    for spp in (1, 2, 4, 8):
        env = {"SS_RENDER_GI_MODE": "2", "SS_RENDER_GI_RAYS": str(spp), "SS_RENDER_AA": "2"}
        img, dev = capture_quality(env, f"raycount_{spp}spp", TECH_FRAMES, TECH_MAXFRAMES, tmp)
        if img is None:
            print(f"  spp={spp}: FAIL capture")
            continue
        p, s, fl = _qb.psnr(ref_img, img), _qb.ssim(ref_img, img), _qb.flip(ref_img, img)
        perf = gpu_ms_for(env, f"raycount_{spp}spp")
        gpu_ms = perf["totalGpuMs"] if perf else None
        fl_s = f"{fl:.4f}" if fl is not None else "n/a"
        gpu_s = f"{gpu_ms:.3f}" if gpu_ms is not None else "n/a"
        print(f"  spp={spp:<2}  PSNR={p:6.2f}dB  SSIM={s:.4f}  FLIP={fl_s}  GPU total={gpu_s}ms  (device={dev or ref_dev})")
        results["raycount"].append({"spp": spp, "psnr": p, "ssim": s, "flip": fl, "gpu_total_ms": gpu_ms,
                                    "device": dev or ref_dev})

    print("\n=== raycount sweep: raw-noise screenshots (denoiser+temporal+TAA off, capped) ===")
    for spp in (1, 2, 4, 8):
        env = {"SS_RENDER_GI_MODE": "2", "SS_RENDER_GI_RAYS": str(spp), **NOISE_ENV}
        img, dev = capture_quality(env, f"spp_sweep_{spp}", NOISE_FRAMES, NOISE_MAXFRAMES, tmp)
        if img is None:
            print(f"  spp={spp}: FAIL capture")
            continue
        out = FIG_DIR / f"spp_sweep_{spp}.png"
        save_png(img, out)
        print(f"  spp={spp} -> {out} (device={dev})")

    # ---- 2. denoiser eval -------------------------------------------------------------------
    print("\n=== denoiser eval (sec:denoise-eval): fixed 2 rays, denoiser on/off vs reference ===")
    fixed_rays = "2"
    for tag, denoise_on in (("off", "0"), ("on", "1")):
        env = {"SS_RENDER_GI_MODE": "2", "SS_RENDER_GI_RAYS": fixed_rays, "SS_RENDER_AA": "2",
               "SS_RENDER_GI_DENOISE": denoise_on}
        img, dev = capture_quality(env, f"denoise_{tag}", TECH_FRAMES, TECH_MAXFRAMES, tmp)
        if img is None:
            print(f"  denoiser={tag}: FAIL capture")
            continue
        p, s, fl = _qb.psnr(ref_img, img), _qb.ssim(ref_img, img), _qb.flip(ref_img, img)
        fl_s = f"{fl:.4f}" if fl is not None else "n/a"
        print(f"  denoiser={tag:<3}  PSNR={p:6.2f}dB  SSIM={s:.4f}  FLIP={fl_s}  (device={dev})")
        results["denoise_eval"][f"quality_{tag}"] = {"psnr": p, "ssim": s, "flip": fl, "device": dev}

    print("\n  GPU cost of the denoiser itself (A/B on render.gi.denoise, GI otherwise on):")
    for tag, denoise_on in (("off", "0"), ("on", "1")):
        env = {"SS_RENDER_GI_MODE": "2", "SS_RENDER_GI_RAYS": fixed_rays, "SS_RENDER_GI_DENOISE": denoise_on}
        perf = gpu_ms_for(env, f"denoise_perf_{tag}")
        gpu_ms = perf["totalGpuMs"] if perf else None
        gpu_s = f"{gpu_ms:.3f}" if gpu_ms is not None else "n/a"
        print(f"    denoiser={tag:<3}  GPU total={gpu_s}ms")
        results["denoise_eval"][f"gpu_{tag}"] = gpu_ms

    print("\n  Frame-to-frame RMS at steady state (static-view flicker proxy, NOT camera motion):")
    for tag, denoise_on in (("off", "0"), ("on", "1")):
        env = {"SS_RENDER_GI_MODE": "2", "SS_RENDER_GI_RAYS": fixed_rays, "SS_RENDER_AA": "2",
               "SS_RENDER_GI_DENOISE": denoise_on}
        img_n, _ = capture_quality(env, f"flicker_{tag}_n", TECH_FRAMES, TECH_MAXFRAMES, tmp)
        img_n1, _ = capture_quality(env, f"flicker_{tag}_n1", TECH_FRAMES + 1, TECH_MAXFRAMES + 1, tmp)
        if img_n is None or img_n1 is None:
            print(f"    denoiser={tag}: FAIL capture")
            continue
        delta = rms(img_n, img_n1)
        print(f"    denoiser={tag:<3}  frame-to-frame RMS={delta:.4f}")
        results["denoise_eval"][f"flicker_rms_{tag}"] = delta

    print("\n=== denoiser eval: stacked screenshots ===")
    noisy_env = {"SS_RENDER_GI_MODE": "2", "SS_RENDER_GI_RAYS": fixed_rays, **NOISE_ENV}
    img, dev = capture_quality(noisy_env, "denoise_compare_noisy", NOISE_FRAMES, NOISE_MAXFRAMES, tmp)
    if img is not None:
        save_png(img, FIG_DIR / "denoise_compare_noisy.png")
        print(f"  noisy -> {FIG_DIR / 'denoise_compare_noisy.png'} (device={dev})")

    denoised_env = {"SS_RENDER_GI_MODE": "2", "SS_RENDER_GI_RAYS": fixed_rays, "SS_RENDER_AA": "2",
                    "SS_RENDER_GI_DENOISE": "1"}
    img, dev = capture_quality(denoised_env, "denoise_compare_denoised", TECH_FRAMES, TECH_MAXFRAMES, tmp)
    if img is not None:
        save_png(img, FIG_DIR / "denoise_compare_denoised.png")
        print(f"  denoised -> {FIG_DIR / 'denoise_compare_denoised.png'} (device={dev})")

    save_png(ref_img, FIG_DIR / "denoise_compare_reference.png")
    print(f"  reference -> {FIG_DIR / 'denoise_compare_reference.png'}")

    dump = THESIS_DIR / "tools" / "raycount_denoise_results.json"
    dump.write_text(json.dumps(results, indent=2))
    print(f"\nResults JSON: {dump}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
