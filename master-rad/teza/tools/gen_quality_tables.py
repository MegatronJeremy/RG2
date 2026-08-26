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
ENGINE = THESIS.parent / "Snowstorm-Engine"
DATA = THESIS / "latex" / "data"
FIGS = THESIS / "latex" / "figures"
RESULTS = HERE / "raycount_denoise_results.json"
HALFRES = HERE / "halfres_results.json"

QUALITY = ENGINE / "Scripts" / "quality-baseline" / "amd-radeon-rx-9070-xt"
MOTION = ENGINE / "Scripts" / "quality-motion-baseline" / "amd-radeon-rx-9070-xt"

# Motion rows in ascending FLIP, so the table reads as a ranking. megalights* are the experimental
# stochastic shadow producer and are labelled as such rather than sitting unmarked beside shipping paths.
MOTION_LABELS = {
    "raster": "raster",
    "ssao": "SSAO",
    "rtao": "RT AO",
    "ssr": "SSR",
    "rtrefl": "RT refleksije",
    "rtshadow": "RT senke",
    "ssgi": "SSGI",
    "rtgi": "RT GI",
    "megalights": r"stohasti\v{c}ke senke",
    "megalights-nospec": r"stohasti\v{c}ke senke (bez spec.)",
    "all-rt": r"sve RT (all-RT)",
}
PROBES = [("dolly", "naprednica"), ("strafe", "bo\\v{c}no"),
          ("reversal", "zaokret"), ("static", r"parkirana")]

# thesis row order and label, keyed by the technique slug the gate writes
TECHNIQUES = [
    ("raster", r"raster (bez efekata)"),
    ("ssao", "SSAO"),
    ("rtao", "RT AO"),
    ("ssr", "SSR"),
    ("rtrefl", "RT refleksije"),
    ("ssgi", "SSGI"),
    ("rtgi", "RT GI"),
    ("all-rt", r"sve RT (all-RT)"),
]


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

    # The technique comparison averages each metric over the three viewpoints, which is what the section
    # claims and what quality-tune.py optimises, so a tuned parameter cannot overfit one frame.
    means, qmacros = {}, []
    for slug, _label in TECHNIQUES:
        files = sorted(QUALITY.glob(f"*__{slug}.json"))
        if not files:
            sys.exit(f"FAIL: no committed quality baseline for technique '{slug}' in {QUALITY}")
        vals = [json.loads(f.read_text(encoding="utf-8")) for f in files]
        means[slug] = tuple(sum(v[k] for v in vals) / len(vals) for k in ("flip", "psnr", "ssim"))
    rows = []
    for slug, label in TECHNIQUES:
        f, p, s = means[slug]
        cell = (rf"\textbf{{{f:.3f}}} & \textbf{{{p:.2f}}} & \textbf{{{s:.3f}}}"
                if slug == "all-rt" else rf"{f:.3f} & {p:.2f} & {s:.3f}")
        rows.append(rf"{label:<20} & {cell} \\")
    out["quality.tex"] = tabular(
        "lrrr", r"Tehnika & FLIP $\downarrow$ & PSNR (dB) $\uparrow$ & SSIM $\uparrow$", rows)

    for slug, name in (("raster", "Raster"), ("rtgi", "RtGi"), ("all-rt", "AllRt")):
        f, p, s = means[slug]
        qmacros += [rf"\newcommand{{\q{name}Flip}}{{{f:.3f}}}",
                    rf"\newcommand{{\q{name}Psnr}}{{{p:.2f}}}",
                    rf"\newcommand{{\q{name}Ssim}}{{{s:.3f}}}"]

    # Motion: the section had no table at all, so its eleven techniques lived only in prose.
    mot = {}
    for f in sorted(MOTION.glob("*.json")):
        m = json.loads(f.read_text(encoding="utf-8"))
        mot[m["technique"]] = m
    if not mot:
        sys.exit(f"FAIL: no committed motion baselines in {MOTION}")
    order = sorted(mot, key=lambda t: mot[t]["flip"])
    out["motion.tex"] = tabular(
        "lrrrr",
        r"Tehnika & FLIP $\downarrow$ & tFLIP $\downarrow$ & ka\v{s}njenje $\downarrow$ & JOD $\uparrow$",
        [rf"{MOTION_LABELS.get(t, t):<32} & {mot[t]['flip']:.3f} & {mot[t]['tflip']:.4f} & "
         rf"{mot[t]['motionPenalty']:.3f} & {mot[t]['cvvdpJod']:.2f} \\" for t in order])

    # Per-probe lag for the two endpoints of the ranking, which is where the probe ordering argument lives:
    # the costliest motion is the direction reversal, and it is not the fastest or the most angular.
    def probe_row(t, key):
        pp = {p["probe"]: p for p in mot[t]["perPair"]}
        return " & ".join(f"{pp[p][key]:.4f}" if key == "tflip" else f"{pp[p][key]:.3f}"
                          for p, _lab in PROBES)
    out["motion-probes.tex"] = tabular(
        "llrrrr",
        "Tehnika & mera & " + " & ".join(lab for _p, lab in PROBES),
        [rf"{MOTION_LABELS[t]} & tFLIP & {probe_row(t, 'tflip')} \\" + "\n"
         + rf"{MOTION_LABELS[t]} & ka\v{{s}}njenje & {probe_row(t, 'motionPenalty')} \\"
         for t in ("raster", "all-rt")])

    for slug, name in (("all-rt", "AllRt"), ("rtgi", "RtGi"), ("raster", "Raster")):
        m = mot[slug]
        qmacros += [rf"\newcommand{{\m{name}Tflip}}{{{m['tflip']:.4f}}}",
                    rf"\newcommand{{\m{name}Jod}}{{{m['cvvdpJod']:.2f}}}",
                    rf"\newcommand{{\m{name}Lag}}{{{m['motionPenalty']:.3f}}}"]

    # Half- versus full-resolution GI/AO tracing (sec:halfres). Previously hand-typed from an
    # uncommitted sweep, which is how its stated +54% came to disagree with its own cells.
    if not HALFRES.exists():
        sys.exit(f"FAIL: {HALFRES.name} not found; run halfres_sweep.py first")
    hr = json.loads(HALFRES.read_text(encoding="utf-8"))
    half, full = (next(x for x in hr["scales"] if x["scale"] == s) for s in (0.5, 1.0))

    def ratio(a, b):
        return rf"$\times {b / a:.1f}$" if a else "--"

    dtot = full["gpu_total_ms"] - half["gpu_total_ms"]
    out["halfres.tex"] = tabular(
        "lrrr",
        r" & polovi\v{c}na (0.5) & puna (1.0) & razlika",
        [rf"Ukupno GPU (ms) & {half['gpu_total_ms']:.2f} & {full['gpu_total_ms']:.2f} & "
         rf"$+{100 * dtot / half['gpu_total_ms']:.0f}\%$ \\",
         rf"\texttt{{GI}} prolaz (ms) & {half['passes']['GI']:.2f} & {full['passes']['GI']:.2f} & "
         rf"{ratio(half['passes']['GI'], full['passes']['GI'])} \\",
         rf"\texttt{{AO}} prolaz (ms) & {half['passes']['AO']:.2f} & {full['passes']['AO']:.2f} & "
         rf"{ratio(half['passes']['AO'], full['passes']['AO'])} \\",
         r"\midrule",
         rf"PSNR (dB) & {half['psnr']:.2f} & {full['psnr']:.2f} & ${full['psnr'] - half['psnr']:+.2f}$ \\",
         rf"SSIM & {half['ssim']:.4f} & {full['ssim']:.4f} & ${full['ssim'] - half['ssim']:+.4f}$ \\",
         rf"FLIP & {half['flip']:.4f} & {full['flip']:.4f} & ${full['flip'] - half['flip']:+.4f}$ \\"])

    qmacros += [rf"\newcommand{{\hrDeltaMs}}{{{dtot:.2f}}}",
                rf"\newcommand{{\hrDeltaPct}}{{{100 * dtot / half['gpu_total_ms']:.0f}}}",
                rf"\newcommand{{\hrHalfTotal}}{{{half['gpu_total_ms']:.2f}}}",
                rf"\newcommand{{\hrPsnrGain}}{{{full['psnr'] - half['psnr']:.2f}}}"]

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
    out["quality-macros.tex"] = "\n".join(macros + qmacros) + "\n"

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
