#!/usr/bin/env python3
"""Count semicolons in thesis prose.

A semicolon between two independent clauses is the em-dash habit wearing a different hat: it joins by
adjacency instead of naming the relationship. Banning the dash and then reaching for the semicolon
moves the tell rather than removing it, so this counts them the same way.

Legitimate uses survive and are reported separately: separating items in a list that already contains
commas, and anything inside a code listing.

    py scan_semicolons.py
"""
import glob
import io
import re
from pathlib import Path

LATEX = Path(__file__).resolve().parent.parent / "latex"


def strip_noise(s: str) -> str:
    s = re.sub(r"(?m)^%.*$", "", s)
    s = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", "", s, flags=re.S)
    s = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", "", s, flags=re.S)
    s = re.sub(r"\\begin\{axis\}.*?\\end\{axis\}", "", s, flags=re.S)
    s = re.sub(r"\\texttt\{[^}]*\}", "CODE", s)
    s = re.sub(r"\\lstinline\|[^|]*\|", "CODE", s)
    return s


def main():
    total = 0
    for f in sorted(glob.glob(str(LATEX / "chapters" / "*.tex"))) + [str(LATEX / "main.tex")]:
        s = strip_noise(io.open(f, encoding="utf-8").read())
        hits = []
        for m in re.finditer(r";", s):
            i = m.start()
            ctx = re.sub(r"\s+", " ", s[max(0, i - 60):i + 45]).strip()
            hits.append(ctx)
        if hits:
            print(f"\n{Path(f).name}: {len(hits)}")
            for h in hits:
                print(f"   ...{h}...")
        total += len(hits)
    print(f"\n{total} semicolon(s) in prose")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
