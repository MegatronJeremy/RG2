#!/usr/bin/env python3
"""Emit the thesis's performance data from the engine's committed perf baselines.

latex/data/perf-cost.dat was hand-maintained and silently desynchronised from the baselines: nothing
regenerated it and no gate compared it, so a re-baseline in the engine left the thesis chart wrong
with no symptom. Everything this writes is derived, so the drift cannot recur; the .tex fragments are
\\input by the tables in chapter 4 rather than retyped.

    py gen_perf_tables.py            # write the files
    py gen_perf_tables.py --check    # exit 1 if regenerating would change anything (a gate)

Per-effect cost is the adjacent-rung difference in whole-frame GPU time, which is how perf-bench
defines it: the default shadow path traces inline inside Forward and has no timestamp scope of its
own, so a per-pass reading cannot isolate it.
"""
import argparse
import json
import sys
from pathlib import Path

THESIS = Path(__file__).resolve().parents[1]
ENGINE = THESIS.parent / "Snowstorm-Engine"
BASE = ENGINE / "Scripts" / "perf-baseline"
DATA = THESIS / "latex" / "data"

# (directory slug, short column label used in the thesis)
ADAPTERS = [("amd-radeon-rx-9070-xt", "9070"), ("nvidia-geforce-rtx-5070", "5070")]

# rung -> (Serbian effect label for the chart, Serbian label for the table)
LADDER = [
    ("shadows", "shadows", "shadows"),
    ("+ao", "AO", "ambient occlusion"),
    ("+refl", "refl", "reflections"),
    ("+gi", "GI", "global illumination (RT)"),
]
PREV = {"shadows": "rt-off", "+ao": "shadows", "+refl": "+ao", "+gi": "+refl"}

# passes worth a row in the per-pass table, as (prefix, label); a prefix collapses its numbered
# iterations (ReflectionDenoise0..2) into one summed row
PASSES = [
    ("Forward", r"\texttt{Forward} (includes inline shadows)"),
    ("Reflection@", r"\texttt{Reflection}"),
    ("ReflectionDenoise", r"\texttt{ReflectionDenoise*}"),
    ("GI@", r"\texttt{GI}"),
    ("GIDenoise", r"\texttt{GIDenoise*}"),
    ("AODenoise", r"\texttt{AODenoise*}"),
    ("AO@", r"\texttt{AO}"),
    ("DepthNormal", r"\texttt{DepthNormal}"),
    ("TemporalResolve", r"\texttt{TemporalResolve} (TAA)"),
]


def load(slug, config):
    p = BASE / slug / f"{config}.json"
    if not p.exists():
        sys.exit(f"FAIL: missing baseline {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def tabular(spec, header, rows):
    r"""A complete booktabs tabular.

    The fragment carries the whole environment rather than just its rows. \input inside an alignment
    lets TeX's implicit end-of-file line become a spurious row, which makes the following \bottomrule
    fail with "Misplaced \noalign"; emitting the environment whole keeps the \input outside any
    alignment.
    """
    body = "\n".join(rows)
    return (
        "\\begin{tabular}{" + spec + "}\n"
        "\\toprule\n"
        + header + " \\\\\n"
        "\\midrule\n"
        + body + "\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
    )


def pass_ms(passes, key):
    """Sum the avgMs of passes matching key. A trailing @ means exact name, else prefix."""
    if key.endswith("@"):
        v = passes.get(key[:-1])
        return v["avgMs"] if v else 0.0
    return sum(v["avgMs"] for k, v in passes.items() if k.startswith(key))


def build():
    out = {}
    totals, rtoff, res, spreads = {}, {}, {}, {}
    for slug, col in ADAPTERS:
        for cfg in ("rt-off", "shadows", "+ao", "+refl", "+gi"):
            d = load(slug, cfg)
            totals[(col, cfg)] = d["totalGpuMs"]
            spreads[(col, cfg)] = d.get("totalSpreadPct", 0.0) / 100.0 * d["totalGpuMs"]
        rtoff[col] = totals[(col, "rt-off")]
        gi = load(slug, "+gi")
        res[col] = (gi.get("width"), gi.get("height"), gi.get("frames"))

    def delta(col, cfg):
        return totals[(col, cfg)] - totals[(col, PREV[cfg])]

    # 1. chart data for pgfplots
    lines = ["effect\tms9070\tms5070"]
    for cfg, chart, _ in LADDER:
        lines.append(f"{chart}\t{delta('9070', cfg):.3f}\t{delta('5070', cfg):.3f}")
    out["perf-cost.dat"] = "\n".join(lines) + "\n"

    # 2. per-effect table rows
    rows = [rf"\texttt{{rt-off}}   & baseline (total) & {rtoff['9070']:.3f} & {rtoff['5070']:.3f} \\"]
    for cfg, _, label in LADDER:
        tag = "+shadows" if cfg == "shadows" else cfg
        rows.append(rf"\texttt{{{tag}}} & {label} & {delta('9070', cfg):.3f} & {delta('5070', cfg):.3f} \\")
    rows.append(r"\midrule")
    # The Configuration cell is deliberately blank here. Repeating "+gi" put the same tag on two
    # adjacent rows carrying very different numbers (the GI delta and the whole frame), which reads as
    # a duplicated row rather than as a change of quantity. Which rung the total comes from is in the
    # Effect cell instead, where it cannot be mistaken for another ladder step.
    rows.append(rf" & \textbf{{whole frame at \texttt{{+gi}}}} & "
                rf"\textbf{{{totals[('9070', '+gi')]:.3f}}} & \textbf{{{totals[('5070', '+gi')]:.3f}}} \\")
    # ssgi repeats the +gi rung with the screen-space producer, so it is diffed against +refl and is
    # an alternative to the RT GI row rather than another step on the ladder.
    rows.append(r"\midrule")
    ss = {}
    for slug, col in ADAPTERS:
        ss[col] = load(slug, "ssgi")["totalGpuMs"] - totals[(col, "+refl")]
    rows.append(rf"\texttt{{ssgi}} & screen-space GI (alternative to +gi) & "
                rf"{ss['9070']:.3f} & {ss['5070']:.3f} \\")
    out["perf-effects.tex"] = tabular("llrr", r"Configuration & Effect & ms (9070 XT) & ms (5070)", rows)

    # the two shadow strategies, both expressed as cost over rt-off
    st = {}
    for slug, col in ADAPTERS:
        st[col] = load(slug, "shadows-stoch")["totalGpuMs"] - rtoff[col]
    out["perf-shadow-strategy.tex"] = tabular("lrr", r"Strategy & ms (9070 XT) & ms (5070)", [
        rf"inline, per light (default) & {delta('9070', 'shadows'):.3f} & {delta('5070', 'shadows'):.3f} \\",
        rf"stochastic, RIS + denoiser & {st['9070']:.3f} & {st['5070']:.3f} \\",
    ])

    # 3. per-pass table rows, from the +gi rung on both adapters
    p9 = load(ADAPTERS[0][0], "+gi")["passes"]
    p5 = load(ADAPTERS[1][0], "+gi")["passes"]
    prows = []
    for key, label in PASSES:
        a, b = pass_ms(p9, key), pass_ms(p5, key)
        if a or b:
            prows.append(rf"{label} & {a:.3f} & {b:.3f} \\")
    out["perf-passes.tex"] = tabular("lrr", r"Pass & ms (9070 XT) & ms (5070)", prows)

    # 4. the scalars the prose quotes, so they are not retyped either
    four9 = sum(delta("9070", c) for c, _, _ in LADDER)
    four5 = sum(delta("5070", c) for c, _, _ in LADDER)
    macros = [
        rf"\newcommand{{\perfFourEffectsAMD}}{{{four9:.2f}}}",
        rf"\newcommand{{\perfFourEffectsNV}}{{{four5:.2f}}}",
        rf"\newcommand{{\perfTotalAMD}}{{{totals[('9070', '+gi')]:.2f}}}",
        rf"\newcommand{{\perfTotalNV}}{{{totals[('5070', '+gi')]:.2f}}}",
        rf"\newcommand{{\perfBaseAMD}}{{{rtoff['9070']:.2f}}}",
        rf"\newcommand{{\perfBaseNV}}{{{rtoff['5070']:.2f}}}",
        rf"\newcommand{{\perfWidth}}{{{res['9070'][0]}}}",
        rf"\newcommand{{\perfHeight}}{{{res['9070'][1]}}}",
        rf"\newcommand{{\perfFrames}}{{{res['9070'][2]}}}",
    ]
    # The conclusion quotes the per-effect costs and the NVIDIA spread; both were hand-typed and both
    # move whenever a rung is re-baselined.
    for cfg, name in (("shadows", "Shadows"), ("+ao", "Ao"), ("+refl", "Refl"), ("+gi", "Gi")):
        macros.append(rf"\newcommand{{\perfEff{name}AMD}}{{{delta('9070', cfg):.3f}}}")
        macros.append(rf"\newcommand{{\perfEff{name}NV}}{{{delta('5070', cfg):.3f}}}")
    nv3 = [delta("5070", c) for c in ("shadows", "+refl", "+gi")]
    macros.append(rf"\newcommand{{\perfNVSpread}}{{{max(nv3) - min(nv3):.3f}}}")
    # The screen-space GI producer, diffed against +refl like the table row. Section 4.2 sets it
    # against \perfEffGi* in the same sentence, so leaving it typed meant half of one comparison
    # regenerated and the other half did not.
    for slug, col in ADAPTERS:
        macros.append(rf"\newcommand{{\perfSsgi{'AMD' if col == '9070' else 'NV'}}}"
                      rf"{{{load(slug, 'ssgi')['totalGpuMs'] - totals[(col, '+refl')]:.3f}}}")

    # Which effect is most expensive is a claim the prose makes per adapter, and re-baselining can flip
    # it: on the 5070 it moved from shadows to GI. A per-effect cost is a DIFFERENCE of two configs, so
    # it carries both configs' run spread; effects closer together than that combined spread are not
    # ordered by the measurement. Generating the winner (and the closest unresolved gap) keeps the
    # sentence honest across a re-capture instead of silently falsifying it.
    EFFECT_LABEL = {"shadows": "shadows", "+ao": "ambient occlusion",
                    "+refl": "reflections", "+gi": "global illumination"}
    for col, tag in (("9070", "AMD"), ("5070", "NV")):
        unc = {cfg: (spreads[(col, PREV[cfg])] ** 2 + spreads[(col, cfg)] ** 2) ** 0.5
               for cfg, _, _ in LADDER}
        costs = {cfg: delta(col, cfg) for cfg, _, _ in LADDER}
        top = max(costs, key=costs.__getitem__)
        resolved = all(costs[top] - costs[c] > (unc[top] ** 2 + unc[c] ** 2) ** 0.5
                       for c in costs if c != top)
        macros.append(rf"\newcommand{{\perfTopEffect{tag}}}{{{EFFECT_LABEL[top]}}}")
        macros.append(rf"\newcommand{{\perfTopResolved{tag}}}{{{'yes' if resolved else 'no'}}}")
        pairs = [(abs(costs[a] - costs[b]), (unc[a] ** 2 + unc[b] ** 2) ** 0.5, a, b)
                 for i, a in enumerate(costs) for b in list(costs)[i + 1:]]
        tight = [p for p in pairs if p[0] <= p[1]]
        macros.append(rf"\newcommand{{\perfUnresolvedPairs{tag}}}{{{len(tight)}}}")
        if tight:
            d, _, a, b = min(tight)
            macros.append(rf"\newcommand{{\perfUnresolved{tag}}}{{{EFFECT_LABEL[a]} and {EFFECT_LABEL[b]}}}")
            macros.append(rf"\newcommand{{\perfUnresolvedGap{tag}}}{{{d:.3f}}}")
    # Whole-frame AMD-minus-NVIDIA gap at each end of the ladder, quoted in the ladder figure's caption.
    macros.append(rf"\newcommand{{\perfGapBase}}{{{rtoff['9070'] - rtoff['5070']:.2f}}}")
    macros.append(rf"\newcommand{{\perfGapGi}}"
                  rf"{{{totals[('9070', '+gi')] - totals[('5070', '+gi')]:.2f}}}")

    # Span of the per-pass AMD/NVIDIA cost ratio. The chapter's point is that this is a RANGE rather
    # than one clock factor, so both ends are quoted in two places and both move on every re-capture.
    ratios = [pass_ms(p9, n) / pass_ms(p5, n) for n in p9
              if n in p5 and pass_ms(p9, n) and pass_ms(p5, n)
              and max(pass_ms(p9, n), pass_ms(p5, n)) >= 0.05]
    macros.append(rf"\newcommand{{\perfRatioMin}}{{{min(ratios):.2f}}}")
    macros.append(rf"\newcommand{{\perfRatioMax}}{{{max(ratios):.2f}}}")

    # The shadow-strategy pair, which the prose quotes on both adapters plus the margin each way. The
    # ranking inverts between vendors, so these four are the chapter's load-bearing numbers and were
    # the ones a re-capture silently falsified while they were typed by hand.
    for col, tag in (("9070", "AMD"), ("5070", "NV")):
        inline, stoch = delta(col, "shadows"), st[col]
        macros.append(rf"\newcommand{{\perfShadowInline{tag}}}{{{inline:.3f}}}")
        macros.append(rf"\newcommand{{\perfShadowStoch{tag}}}{{{stoch:.3f}}}")
        macros.append(rf"\newcommand{{\perfShadowGap{tag}}}{{{abs(inline - stoch):.3f}}}")
        macros.append(rf"\newcommand{{\perfShadowRatio{tag}}}"
                      rf"{{{max(inline, stoch) / min(inline, stoch):.1f}}}")
        macros.append(rf"\newcommand{{\perfShadowWinner{tag}}}"
                      rf"{{{'stochastic' if stoch < inline else 'inline'}}}")

    # The a-trous chain's own cost, summed over its three iterations. Read from the timestamp scopes
    # rather than a whole-frame A/B, which for this filter is smaller than the run-to-run spread.
    for tag, passes in (("AMD", p9), ("NV", p5)):
        tot = sum(pass_ms(passes, f"GIDenoise{i}") or 0.0 for i in range(3))
        macros.append(rf"\newcommand{{\perfDenoise{tag}}}{{{tot:.3f}}}")
    out["perf-macros.tex"] = "\n".join(macros) + "\n"

    if res["9070"][:2] != res["5070"][:2]:
        sys.exit(f"FAIL: adapters were captured at different resolutions: {res}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed files differ from what the baselines imply")
    args = ap.parse_args()

    out = build()
    DATA.mkdir(parents=True, exist_ok=True)
    stale = []
    for name, text in out.items():
        p = DATA / name
        old = p.read_text(encoding="utf-8") if p.exists() else None
        if old != text:
            stale.append(name)
            if not args.check:
                p.write_text(text, encoding="utf-8")

    if args.check:
        if stale:
            print("STALE (regenerate with gen_perf_tables.py): " + ", ".join(stale))
            return 1
        print("up to date")
        return 0

    print(("rewrote " + ", ".join(stale)) if stale else "already up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
