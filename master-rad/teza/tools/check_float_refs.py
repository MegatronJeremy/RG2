#!/usr/bin/env python3
"""Find figure/table labels that no \\ref points at.

A float nothing refers to is a float the reader has no reason to look at, and LaTeX does not warn
about it the way it warns about an undefined reference: the error is silent and in the other
direction. Two of chapter 4's result plots and the frame-overview diagram were unreferenced.

    py check_float_refs.py
"""
import io
import re
import sys
from pathlib import Path

CH = Path(__file__).resolve().parents[1] / "latex" / "chapters"
LABEL = re.compile(r"\\label\{((?:fig|tab):[A-Za-z0-9:_-]+)\}")
REF = re.compile(r"\\ref\{((?:fig|tab):[A-Za-z0-9:_-]+)\}")


def main() -> int:
    labels, refs = {}, set()
    for f in sorted(CH.glob("*.tex")):
        t = io.open(f, encoding="utf-8").read()
        for m in LABEL.finditer(t):
            labels[m.group(1)] = f.name
        refs |= set(REF.findall(t))

    orphans = sorted((k, v) for k, v in labels.items() if k not in refs)
    dangling = sorted(refs - set(labels))

    for k, v in orphans:
        print(f"  unreferenced: {k:<30} defined in {v}")
    for k in dangling:
        print(f"  DANGLING ref: {k}")
    print(f"{len(labels)} float labels, {len(orphans)} unreferenced, {len(dangling)} dangling")
    return 1 if orphans or dangling else 0


if __name__ == "__main__":
    raise SystemExit(main())
