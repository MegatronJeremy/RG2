#!/usr/bin/env python3
"""Emit pgfplots data files for the performance chapter from the committed perf baselines.

A table is read one cell at a time; these three shapes are the ones the numbers only show as a shape:

  passcost-vendor.dat   per-pass ms on both adapters, and the AMD/NVIDIA ratio. The chapter's claim is
                        that the two vendors rank the effects differently, which is a per-pass pattern
                        rather than any single number.
  ladder.dat            cumulative total GPU time along the rt-off -> shadows -> +ao -> +refl -> +gi
                        ladder for both adapters, so the divergence point is visible.
  quality-spread.dat    FLIP per technique with the min/max across the three viewpoints, which says
                        whether a technique's ranking is stable or an artifact of one frame.

No GPU run: everything here is read from Scripts/{perf,quality}-baseline/.

    py gen_perf_plots.py [--check]
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
THESIS = HERE.parent
ENGINE = THESIS.parent / "Snowstorm-Engine"
DATA = THESIS / "latex" / "data"

PERF = ENGINE / "Scripts" / "perf-baseline"
QUALITY = ENGINE / "Scripts" / "quality-baseline"

AMD = "amd-radeon-rx-9070-xt"
NV = "nvidia-geforce-rtx-5070"

LADDER = ["rt-off", "shadows", "+ao", "+refl", "+gi"]

# Passes worth plotting: everything the RT effects own, plus Forward (which carries inline shadows) and
# the temporal resolve. Sub-0.05 ms passes are timestamp noise and are dropped by MIN_MS below.
MIN_MS = 0.05

# Must stay in the same order as gen_quality_tables.TECHNIQUES: the spread figure's caption claims it
# plots the same data as the quality table, and the two lists were separately written, so adding a
# technique to one silently made the figure show a different set from the table it points at.
TECHNIQUES = ["raster", "ssao", "rtao", "ssr", "rtrefl", "rtshadow", "megalights",
              "ssgi", "rtgi", "all-rt"]

# (label, screen-space config, shared baseline config, ray-traced config, SS technique, RT technique).
# The first four name perf configs, the last two quality ones.
TRADEOFF = [
    ("AO", "ssao", "shadows", "+ao", "ssao", "rtao"),
    ("Reflections", "ssr", "+ao", "+refl", "ssr", "rtrefl"),
    ("GI", "ssgi", "+refl", "+gi", "ssgi", "rtgi"),
]


def load(dev, config):
    p = PERF / dev / f"{config}.json"
    if not p.exists():
        sys.exit(f"FAIL: missing perf baseline {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def pass_ms(doc, name):
    e = doc["passes"].get(name)
    return None if e is None else float(e["avgMs"])


def total(dev, config):
    return float(load(dev, config)["totalGpuMs"])


def flip_mean(technique):
    files = sorted((QUALITY / AMD).glob(f"*__{technique}.json"))
    if not files:
        sys.exit(f"FAIL: no quality baseline for {technique}")
    vals = [json.loads(f.read_text(encoding="utf-8"))["flip"] for f in files]
    return sum(vals) / len(vals)


def build():
    out = {}

    amd, nv = load(AMD, "+gi"), load(NV, "+gi")
    shared = [n for n in amd["passes"] if n in nv["passes"]]
    rows = []
    for n in shared:
        a, b = pass_ms(amd, n), pass_ms(nv, n)
        if a is None or b is None or max(a, b) < MIN_MS:
            continue
        rows.append((n, a, b))
    rows.sort(key=lambda r: -max(r[1], r[2]))
    lines = ["pass\tamd\tnv\tratio"]
    for n, a, b in rows:
        lines.append(f"{n}\t{a:.4f}\t{b:.4f}\t{(a / b if b else 0):.4f}")
    out["passcost-vendor.dat"] = "\n".join(lines) + "\n"

    lines = ["i\tconfig\tamd\tnv"]
    for i, cfg in enumerate(LADDER):
        a = load(AMD, cfg)["totalGpuMs"]
        b = load(NV, cfg)["totalGpuMs"]
        lines.append(f"{i}\t{cfg}\t{a:.4f}\t{b:.4f}")
    out["ladder.dat"] = "\n".join(lines) + "\n"

    # The two shadow strategies, each as cost over rt-off on both adapters. The figure's point is that
    # the lines cross, so the coordinates must come from the baselines: hand-typed ones would keep the
    # crossing drawn after a re-capture moved it.
    lines = ["i\tadapter\tinline\tstochastic"]
    for i, (slug, name) in enumerate([(AMD, "9070XT"), (NV, "5070")]):
        base = load(slug, "rt-off")["totalGpuMs"]
        inline = load(slug, "shadows")["totalGpuMs"] - base
        stoch = load(slug, "shadows-stoch")["totalGpuMs"] - base
        lines.append(f"{i}\t{name}\t{inline:.4f}\t{stoch:.4f}")
    out["shadow-strategy.dat"] = "\n".join(lines) + "\n"

    lines = ["i\ttech\tflip\tlo\thi"]
    for i, t in enumerate(TECHNIQUES):
        files = sorted((QUALITY / AMD).glob(f"*__{t}.json"))
        if not files:
            sys.exit(f"FAIL: no quality baseline for {t}")
        vals = [json.loads(f.read_text(encoding="utf-8"))["flip"] for f in files]
        mean = sum(vals) / len(vals)
        lines.append(f"{i}\t{t}\t{mean:.4f}\t{min(vals):.4f}\t{max(vals):.4f}")
    out["quality-spread.dat"] = "\n".join(lines) + "\n"

    # What ray tracing costs against what it returns, per effect. Both quantities are computed WITHIN a
    # screen-space/ray-traced pair (a cost ratio and a FLIP difference), which is what makes them
    # comparable across effects: neither depends on which ladder rung the pair sits on, so the perf
    # ladder's cumulative baselines and the quality matrix's single-effect ones do not have to agree.
    # Plotting the two absolute values against each other instead would silently mix the two matrices.
    lines = ["effect\tmultAmd\tmultNv\tflipGain"]
    for label, ss, base, rt, ssq, rtq in TRADEOFF:
        def delta(dev, cfg):
            return total(dev, cfg) - total(dev, base)
        gain = flip_mean(ssq) - flip_mean(rtq)
        lines.append(f"{label}\t{delta(AMD, rt) / delta(AMD, ss):.2f}\t"
                     f"{delta(NV, rt) / delta(NV, ss):.2f}\t{gain:.4f}")
    out["tradeoff.dat"] = "\n".join(lines) + "\n"

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    out = build()
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
    print(("wrote " + ", ".join(stale)) if stale else "up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
