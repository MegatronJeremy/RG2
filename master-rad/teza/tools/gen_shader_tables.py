#!/usr/bin/env python3
"""Emit the cross-vendor shader register/occupancy table from the engine's committed baselines.

Two artifacts, deliberately different in authority:

  Scripts/rga-baseline/occupancy-gfx1200.json   offline RGA over every cooked shader and permutation.
      Authoritative for AMD: deterministic, complete, and it labels permutations, which the runtime
      capture cannot (both DefaultLit variants appear under one pipeline name there).
  Scripts/shader-stats-baseline/*.json          driver-reported via VK_KHR_pipeline_executable_properties.
      The only source for NVIDIA, since register allocation happens in the driver JIT and no offline
      analyser exists. Covers only what the app actually compiled.

The AMD register counts agree between the two, which is what justifies carrying the RGA permutation
labels over to the runtime numbers.

    py gen_shader_tables.py [--check]
"""
import argparse
import json
import sys
from pathlib import Path

THESIS = Path(__file__).resolve().parents[1]
ENGINE = THESIS.parent / "Snowstorm-Engine"
DATA = THESIS / "latex" / "data"

RGA = ENGINE / "Scripts" / "rga-baseline" / "occupancy-gfx1201.json"
NV = ENGINE / "Scripts" / "shader-stats-baseline" / "nvidia-geforce-rtx-5070.json"

# gfx1201 is Navi 48 (RX 9070 / 9070 XT); gfx1200 is Navi 44 (RX 9060 / 9060 XT), per RGA's own target
# list. The table names the 9070 XT, so it has to read the 9070 XT's ASIC even though the two agree:
# all 47 cooked shaders allocate identically on both, so this changes provenance, not numbers.
ASIC = "gfx1201"

# The occupancy models are IMPORTED, never restated here. A copy in this file would be a third
# definition of the AMD one, and the two that already existed disagreed (granularity 8 against 24),
# which put wrong wave counts in a draft of this table. rga-occupancy.py owns the AMD model because
# it is the one the project gates on; shader-stats.py owns the NVIDIA one because no offline
# analyser exists there.
def _engine_module(name):
    import importlib.util
    path = ENGINE / "Scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# (RGA permutation name, runtime shader file, stage, thesis label)
ROWS = [
    ("DefaultLit.frag[inlineshadow]", "DefaultLit.frag.hlsl", "fragment", r"\texttt{DefaultLit.frag} (inline shadows)"),
    ("DefaultLit.frag[noinlineshadow]", "DefaultLit.frag.hlsl", "fragment", r"\texttt{DefaultLit.frag} (no inline shadows)"),
    ("GI.comp[norestir]", "GI.comp.hlsl", "compute", r"\texttt{GI.comp}"),
    ("Reflection.comp", "Reflection.comp.hlsl", "compute", r"\texttt{Reflection.comp}"),
    ("AO.comp", "AO.comp.hlsl", "compute", r"\texttt{AO.comp}"),
    # one shader, compiled per signal; [gi] is the variant on the half-res GI chain
    ("GIDenoise.comp[gi]", "GIDenoise.comp.hlsl", "compute", r"\texttt{GIDenoise.comp} (GI)"),
]


_rga = _engine_module("rga-occupancy")
_stats = _engine_module("shader-stats")

AMD_MAX = _rga.max_waves_for(ASIC)
NV_MAX_WARPS = _stats.NV_MAX_WARPS


def amd_waves(v):
    return _rga.vgpr_occupancy(float(v), ASIC)


def nv_warps(r):
    waves, _ = _stats.occupancy(r, is_amd=False)
    return waves


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    rga = json.loads(RGA.read_text(encoding="utf-8"))["shaders"]
    nv = json.loads(NV.read_text(encoding="utf-8"))["executables"]

    # runtime NVIDIA entries keyed by (file, stage); a shader compiled in several permutations appears
    # more than once, so keep every register count and match by rank against the RGA figure
    nvmap = {}
    for e in nv:
        f = e["pipeline"].split("|")[-1].split("/")[-1]
        r = e["stats"].get("Register Count", {}).get("value")
        if r:
            nvmap.setdefault((f, e["stages"]), []).append(int(r))
    for k in nvmap:
        nvmap[k].sort()

    rows, missing = [], []
    for rga_name, f, stage, label in ROWS:
        entry = rga.get(rga_name)
        if entry is None:
            missing.append(rga_name)
            continue
        v = int(entry["vgprs"])
        cands = nvmap.get((f, stage), [])
        # the inline-shadow permutation is the register-heavier of the two on both vendors
        if not cands:
            missing.append(f"{f} ({stage}) on NVIDIA")
            continue
        # match on the bracketed permutation, not a substring: "[noinlineshadow]" contains
        # "inlineshadow]" and would otherwise select the heavier variant for both rows
        r = cands[-1] if "[inlineshadow]" in rga_name else cands[0]
        rows.append(rf"{label} & {v} & {amd_waves(v)}/{AMD_MAX} & {r} & {nv_warps(r)}/{NV_MAX_WARPS} \\")

    if missing:
        sys.exit("FAIL: no baseline entry for " + ", ".join(missing))

    body = "\n".join(rows)
    table = (
        "\\begin{tabular}{lrrrr}\n\\toprule\n"
        "& \\multicolumn{2}{c}{RX 9070 XT (RDNA4)} & \\multicolumn{2}{c}{RTX 5070 (Blackwell)} \\\\\n"
        "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\n"
        "Shader & VGPR & waves/SIMD & registers & warps/SM \\\\\n\\midrule\n"
        + body + "\n\\bottomrule\n\\end{tabular}\n"
    )

    # The occupancy curve itself: waves against VGPR count, sampled across the whole range, so the
    # step structure is visible rather than asserted. The cliff the thesis cares about is that 127
    # allocates 144 and drops to 10 waves while 87 allocates 96 and keeps all 16.
    curve = ["vgpr\twaves"]
    for v in range(24, 193, 1):
        curve.append(f"{v}\t{amd_waves(v)}")
    curve_txt = "\n".join(curve) + "\n"

    # the shaders to mark on that curve, from the same baseline
    marks = ["vgpr\twaves\tlabel"]
    for rga_name, _f, _s, _label in ROWS:
        e = rga.get(rga_name)
        if e:
            v = int(e["vgprs"])
            short = rga_name.replace(".comp", "").replace(".frag", "")
            marks.append(f"{v}\t{amd_waves(v)}\t{short}")
    marks_txt = "\n".join(marks) + "\n"

    DATA.mkdir(parents=True, exist_ok=True)
    outputs = {
        "shader-occupancy.tex": table,
        "occupancy-curve.dat": curve_txt,
        "occupancy-marks.dat": marks_txt,
    }
    stale = []
    for name, text in outputs.items():
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
