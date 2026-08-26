#!/usr/bin/env python3
"""Report sentence pairs that say the same thing in two places.

Volume alone is a bad trim target: cutting a unique paragraph loses information, cutting the second
statement of a fact loses none. This scores sentence pairs by shared rare-word overlap so the second
statements surface.

    py find_dupes.py [min_score]
"""
import glob
import io
import re
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

LATEX = Path(__file__).resolve().parent.parent / "latex"

STOP = set("""the a an and or but of to in on for with as is are was were be been by that this these
those it its from at not no than then so such which who whom whose what when where how why all any
each other some more most much many few both either neither can could may might must shall should
will would do does did have has had here there they them their he she his her we our you your""".split())


def sentences():
    out = []
    for f in sorted(glob.glob(str(LATEX / "chapters" / "*.tex"))):
        s = io.open(f, encoding="utf-8").read()
        s = re.sub(r"(?m)^%.*$", "", s)
        # drop float bodies, listings and math: duplication there is structural, not prose
        s = re.sub(r"\\begin\{(figure|table|lstlisting|tikzpicture|axis|equation)\*?\}.*?"
                   r"\\end\{\1\*?\}", " ", s, flags=re.S)
        s = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", s)
        s = re.sub(r"[{}$~\\]", " ", s)
        for raw in re.split(r"(?<=[.!?])\s+", s):
            t = " ".join(raw.split())
            if len(t.split()) >= 9:
                out.append((Path(f).name, t))
    return out


def main():
    floor = float(sys.argv[1]) if len(sys.argv) > 1 else 0.42
    sents = sentences()
    df = Counter()
    toks = []
    for _f, t in sents:
        w = {x.lower().strip(".,;:()") for x in t.split() if len(x) > 3}
        w -= STOP
        toks.append(w)
        for x in w:
            df[x] += 1
    n = len(sents)
    hits = []
    for i, j in combinations(range(n), 2):
        a, b = toks[i], toks[j]
        if not a or not b:
            continue
        inter = a & b
        if len(inter) < 4:
            continue
        # weight by rarity: two sentences sharing rare terms are the same claim twice
        w = sum(1.0 / df[x] for x in inter) / min(len(a), len(b))
        score = len(inter) / min(len(a), len(b)) * (1 + w)
        if score >= floor:
            hits.append((score, i, j))
    hits.sort(reverse=True)
    for score, i, j in hits[:18]:
        print(f"--- {score:.2f}  {sents[i][0]} / {sents[j][0]}")
        print("  A:", sents[i][1][:150])
        print("  B:", sents[j][1][:150])
    print(f"\n{len(hits)} candidate duplicate pairs at score >= {floor}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
