#!/usr/bin/env python3
"""Find figure/table labels that no \\ref points at.

A float nothing refers to is a float the reader has no reason to look at, and LaTeX does not warn
about it the way it warns about an undefined reference: the error is silent and in the other
direction. Two of chapter 4's result plots and the frame-overview diagram were unreferenced.

    py check_float_refs.py [--sr]

--sr checks latex-sr/ instead; labels of chapters not yet translated are taken from latex/ so refs to
them are not reported as dangling.
"""
import io
import re
import sys
from pathlib import Path

TEZA = Path(__file__).resolve().parents[1]
SR_MODE = "--sr" in sys.argv
CH = TEZA / ("latex-sr" if SR_MODE else "latex") / "chapters"
LABEL = re.compile(r"\\label\{((?:fig|tab):[A-Za-z0-9:_-]+)\}")
REF = re.compile(r"\\ref\{((?:fig|tab):[A-Za-z0-9:_-]+)\}")


def main() -> int:
    labels, refs, other = {}, set(), {}
    for f in sorted(CH.glob("*.tex")):
        t = io.open(f, encoding="utf-8").read()
        for m in LABEL.finditer(t):
            labels[m.group(1)] = f.name
        refs |= set(REF.findall(t))

    if SR_MODE:
        done = {f.name for f in CH.glob("*.tex")}
        for f in sorted((TEZA / "latex" / "chapters").glob("*.tex")):
            if f.name not in done:
                for m in LABEL.finditer(io.open(f, encoding="utf-8").read()):
                    other[m.group(1)] = f.name
    orphans = sorted((k, v) for k, v in labels.items() if k not in refs)
    dangling = sorted(refs - set(labels) - set(other))

    for k, v in orphans:
        print(f"  unreferenced: {k:<30} defined in {v}")
    for k in dangling:
        print(f"  DANGLING ref: {k}")
    if SR_MODE:
        pend = sorted(refs & set(other))
        print(f"  {len(pend)} ref(s) to untranslated chapters (resolve to ?? until translated): {pend}")
    print(f"{len(labels)} float labels, {len(orphans)} unreferenced, {len(dangling)} dangling")
    return 1 if orphans or dangling else 0


if __name__ == "__main__":
    raise SystemExit(main())
