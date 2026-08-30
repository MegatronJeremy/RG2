#!/usr/bin/env python3
"""Which per-effect cost differences are resolved by the measurement, and which are not.

A per-effect cost is a DIFFERENCE of two configs, so it inherits both configs' run-to-run spread.
Ranking effects by their point estimates alone reads an ordering the measurement may not support:
on the RTX 5070 shadows and reflections differ by less than their combined spread, so their order
is not a result. Uncertainty is the config's total spread (max-min across the medianed runs) carried
into the difference in quadrature.

    py effect_separation.py
"""
import json
from itertools import combinations
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent / "Snowstorm-Engine" / "Scripts" / "perf-baseline"
DEVICES = [("amd-radeon-rx-9070-xt", "RX 9070 XT"), ("nvidia-geforce-rtx-5070", "RTX 5070")]
LADDER = [("shadows", "rt-off", "shadows"), ("ao", "shadows", "+ao"),
          ("refl", "+ao", "+refl"), ("gi", "+refl", "+gi")]


def main():
    for slug, label in DEVICES:
        cfg = {c: json.load(open(BASE / slug / f"{c}.json"))
               for c in ["rt-off", "shadows", "+ao", "+refl", "+gi", "ssgi", "shadows-stoch"]}
        ms = {c: j["totalGpuMs"] for c, j in cfg.items()}
        sd = {c: j["totalSpreadPct"] / 100.0 * j["totalGpuMs"] for c, j in cfg.items()}

        eff = {n: (ms[b] - ms[a], (sd[a] ** 2 + sd[b] ** 2) ** 0.5) for n, a, b in LADDER}
        print(f"=== {label} ===")
        for n, (v, u) in eff.items():
            print(f"  {n:<9}{v:>7.3f} +/- {u:.3f} ms")

        print("  pairwise:")
        for x, y in combinations(eff, 2):
            dv = abs(eff[x][0] - eff[y][0])
            du = (eff[x][1] ** 2 + eff[y][1] ** 2) ** 0.5
            verdict = "resolved" if dv > du else "NOT resolved"
            print(f"    {x:>5} vs {y:<5} d={dv:.3f}  combined={du:.3f}  {verdict}")

        top = max(eff, key=lambda k: eff[k][0])
        rest = [k for k in eff if k != top]
        clear = all(eff[top][0] - eff[k][0] > (eff[top][1] ** 2 + eff[k][1] ** 2) ** 0.5 for k in rest)
        print(f"  most expensive: {top} ({'resolved against all others' if clear else 'NOT resolved against all'})")

        inline = ms["shadows"] - ms["rt-off"]
        stoch = ms["shadows-stoch"] - ms["rt-off"]
        print(f"  shadow strategy: inline {inline:.3f}  stochastic {stoch:.3f}  "
              f"diff {abs(inline - stoch):.3f}  ratio {max(inline, stoch) / min(inline, stoch):.2f}x")
        print(f"  all four: {ms['+gi'] - ms['rt-off']:.3f} ms   ssgi: {ms['ssgi'] - ms['+refl']:.3f} ms")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
