#!/usr/bin/env python3
"""Emit the ray-count and denoiser tables from the sweep's own result file.

These two tables were typed by hand from a sweep's console output and then drifted when the sweep was
re-run against a changed engine: the flicker figures moved from 0.3229/0.1949 to 0.2185/0.2038 after
the capture-reproducibility fix, which is a large enough change to alter what the section concludes.
Generating them from raycount_denoise_results.json means re-running the sweep updates the thesis.

The high-frequency energies are recomputed here from the committed figures rather than stored, so the
number in the text and the image a reader looks at cannot disagree.

    py gen_quality_tables.py [--check]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
THESIS = HERE.parent
DATA = THESIS / "latex" / "data"
FIGS = THESIS / "latex" / "figures"
RESULTS = HERE / "raycount_denoise_results.json"


def tabular(spec, header, rows):
    return ("\\begin{tabular}{" + spec + "}\n\\toprule\n" + header + " \\\\\n\\midrule\n"
            + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")


def high_freq(name):
    """Mean absolute vertical neighbour difference of the grayscale channel, as defined in the text."""
    a = np.asarray(Image.open(FIGS / name).convert("RGB")).astype(np.float64)
    g = a.mean(2)
    return float(np.abs(g[1:, :] - g[:-1, :]).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not RESULTS.exists():
        sys.exit(f"FAIL: {RESULTS.name} not found; run raycount_denoise_sweep.py first")
    d = json.loads(RESULTS.read_text(encoding="utf-8"))

    rc = sorted(d["raycount"], key=lambda r: r["spp"])
    out = {
        "raycount.tex": tabular(
            "@{}rrrrr@{}",
            r"Zraka/piksel & PSNR (dB) & SSIM & FLIP & GPU ukupno (ms)",
            [rf"{r['spp']} & {r['psnr']:.2f} & {r['ssim']:.4f} & {r['flip']:.4f} & {r['gpu_total_ms']:.2f} \\"
             for r in rc]),
    }

    de = d["denoise_eval"]
    off, on = de["quality_off"], de["quality_on"]
    out["denoise-eval.tex"] = tabular(
        "@{}lrrr@{}", r"Denoiser & PSNR (dB) & SSIM & FLIP",
        [rf"isklju\v{{c}}en & {off['psnr']:.2f} & {off['ssim']:.4f} & {off['flip']:.4f} \\",
         rf"uklju\v{{c}}en & {on['psnr']:.2f} & {on['ssim']:.4f} & {on['flip']:.4f} \\"])

    knee = rc[-1]["gpu_total_ms"] / rc[0]["gpu_total_ms"] - 1.0
    macros = [
        rf"\newcommand{{\rcGpuLow}}{{{rc[0]['gpu_total_ms']:.2f}}}",
        rf"\newcommand{{\rcGpuHigh}}{{{rc[-1]['gpu_total_ms']:.2f}}}",
        rf"\newcommand{{\rcGpuPct}}{{{knee * 100:.0f}}}",
        rf"\newcommand{{\rcPsnrGain}}{{{rc[-1]['psnr'] - rc[0]['psnr']:.2f}}}",
        rf"\newcommand{{\rcFlipLow}}{{{rc[0]['flip']:.4f}}}",
        rf"\newcommand{{\rcFlipHigh}}{{{rc[-1]['flip']:.4f}}}",
        rf"\newcommand{{\flickerOff}}{{{de['flicker_rms_off']:.4f}}}",
        rf"\newcommand{{\flickerOn}}{{{de['flicker_rms_on']:.4f}}}",
        rf"\newcommand{{\flickerPct}}{{{(1 - de['flicker_rms_on'] / de['flicker_rms_off']) * 100:.1f}}}",
    ]
    for spp in (1, 2, 4, 8):
        macros.append(rf"\newcommand{{\hfSpp{'One Two Four Eight'.split()[[1,2,4,8].index(spp)]}}}"
                      rf"{{{high_freq(f'spp_sweep_{spp}.png'):.1f}}}")
    macros += [
        rf"\newcommand{{\hfGiRaw}}{{{high_freq('dbg_gi_raw.png'):.1f}}}",
        rf"\newcommand{{\hfGiDenoised}}{{{high_freq('dbg_gi_denoised.png'):.1f}}}",
        rf"\newcommand{{\hfConeSharp}}{{{high_freq('cone_sharp.png'):.1f}}}",
        rf"\newcommand{{\hfConeGlossy}}{{{high_freq('cone_glossy.png'):.1f}}}",
    ]
    out["quality-macros.tex"] = "\n".join(macros) + "\n"

    DATA.mkdir(parents=True, exist_ok=True)
    stale = []
    for name, text in out.items():
        p = DATA / name
        if (p.read_text(encoding="utf-8") if p.exists() else None) != text:
            stale.append(name)
            if not args.check:
                p.write_text(text, encoding="utf-8")
    if args.check:
        print(("STALE: " + ", ".join(stale)) if stale else "up to date")
        return 1 if stale else 0
    print(("rewrote " + ", ".join(stale)) if stale else "up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
