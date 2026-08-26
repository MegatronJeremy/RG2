#!/usr/bin/env python3
"""Inventory the load-bearing content of the thesis source, so a prose trim can be proved lossless.

A trim is allowed to delete sentences. It is NOT allowed to drop a citation, a cross-reference target,
a generated macro, or a measured number. This snapshots exactly those four sets before and compares
after, which turns "I think I only cut filler" into a check.

    py trim_inventory.py snapshot <out.json>
    py trim_inventory.py compare  <before.json>
"""
import collections
import glob
import io
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LATEX = HERE.parent / "latex"

# A measured number is a decimal literal in the prose. Integers are excluded: section numbers, ray
# counts and years are not measurements and churn for reasons a trim cannot control.
NUM = re.compile(r"(?<![A-Za-z0-9.])\d+\.\d+(?![0-9])")
MACRO = re.compile(r"\\(perf[A-Za-z]+|q[A-Z][A-Za-z]*|rc[A-Za-z]+|flicker[A-Za-z]*|hf[A-Za-z]+|m[A-Z][A-Za-z]*)\b")


def scan():
    cites, labels, refs, macros, nums = (collections.Counter(), set(),
                                         collections.Counter(), collections.Counter(),
                                         collections.Counter())
    files = sorted(glob.glob(str(LATEX / "chapters" / "*.tex"))) + [str(LATEX / "main.tex")]
    for f in files:
        s = io.open(f, encoding="utf-8").read()
        s = re.sub(r"(?m)^%.*$", "", s)  # LaTeX comments are not printed content
        # Numbers are counted on prose only. Decimals inside TikZ/pgfplots coordinates, image widths
        # and plot heights are layout, not measurements, and treating them as measurements made the
        # gate fire on every cosmetic resize.
        prose = re.sub(r"\\begin\{(tikzpicture|axis)\}.*?\\end\{\1\}", " ", s, flags=re.S)
        prose = re.sub(r"\\includegraphics\[[^\]]*\]", " ", prose)
        for group in re.findall(r"\\cite\{([^}]*)\}", s):
            for k in group.split(","):
                cites[k.strip()] += 1
        labels |= set(re.findall(r"\\label\{([^}]*)\}", s))
        # listings carry their label as an lstlisting option, not a \label command
        labels |= set(re.findall(r"label=\{([^}]*)\}", s))
        for r in re.findall(r"\\ref\{([^}]*)\}", s):
            refs[r] += 1
        for m in MACRO.findall(s):
            macros[m] += 1
        for n in NUM.findall(prose):
            nums[n] += 1
    return {"cites": dict(cites), "labels": sorted(labels),
            "refs": dict(refs), "macros": dict(macros), "nums": dict(nums)}


def main():
    mode, path = sys.argv[1], Path(sys.argv[2])
    cur = scan()
    if mode == "snapshot":
        io.open(path, "w", encoding="utf-8").write(json.dumps(cur, ensure_ascii=False, indent=0))
        print(f"cites {len(cur['cites'])}  labels {len(cur['labels'])}  "
              f"macros {len(cur['macros'])}  distinct decimals {len(cur['nums'])}")
        return 0

    old = json.loads(io.open(path, encoding="utf-8").read())
    bad = 0
    for key in ("cites", "macros", "nums"):
        lost = sorted(set(old[key]) - set(cur[key]))
        if lost:
            bad += len(lost)
            print(f"LOST {key} ({len(lost)}): {', '.join(lost[:20])}")
    lost_labels = sorted(set(old["labels"]) - set(cur["labels"]))
    if lost_labels:
        print(f"REMOVED labels ({len(lost_labels)}): {', '.join(lost_labels)}")
    # a \ref whose target no longer exists is a build error, but catch it here with a better message
    dangling = sorted(set(cur["refs"]) - set(cur["labels"]))
    if dangling:
        bad += len(dangling)
        print(f"DANGLING refs ({len(dangling)}): {', '.join(dangling)}")
    print("OK: no citation, macro or measured number lost" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
