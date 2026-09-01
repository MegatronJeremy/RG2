#!/usr/bin/env python3
"""Count the surface markers of machine-written prose in the thesis body.

None of these is proof of anything on its own: a thesis can legitimately say "robust" and a colon is
a normal piece of punctuation. What the counts are good for is RATE. Generated text tends to reach
for the same few connectives at a rate human writing does not, and it tends to produce sentences of
suspiciously even length. Both are measurable; "does this sound like a person" is not.

Reports per 10,000 words so the numbers stay comparable as the thesis grows.

    py scan_ai_tells.py
"""
import glob
import io
import re
import statistics
import sys
from pathlib import Path

CHAPTERS = Path(__file__).resolve().parent.parent / "latex" / "chapters"

# Float bodies, code listings and TikZ are not prose and would skew every count.
STRIP_ENV = ("figure", "table", "tikzpicture", "axis", "lstlisting", "tabular", "tabularx")

MARKERS = {
    "em-dash (banned)":        r"\u2014",
    "'not just X but Y'":      r"not (?:just|only)\b[^.]{0,60}\bbut\b",
    "'it is worth noting'":    r"(?:it is|it's) worth (?:noting|mentioning)",
    "'Importantly,'":          r"\bImportantly,",
    "'Notably,'":              r"\bNotably,",
    "'Furthermore/Moreover'":  r"\b(?:Furthermore|Moreover|Additionally),",
    "'In conclusion/summary'": r"\bIn (?:conclusion|summary),",
    "delve":                   r"\bdelv",
    "leverage (verb)":         r"\bleverag",
    "robust":                  r"\brobust",
    "crucial":                 r"\bcrucial",
    "seamless":                r"\bseamless",
    "realm / landscape":       r"\b(?:realm|landscape)\b",
    "semicolon":               r"; ",
    "colon mid-sentence":      r"[a-z]: [a-z]",
}


def body_text() -> str:
    out = []
    for f in sorted(glob.glob(str(CHAPTERS / "0*.tex"))):
        s = io.open(f, encoding="utf-8").read()
        s = re.sub(r"(?m)^%.*", "", s)
        for env in STRIP_ENV:
            s = re.sub(r"\\begin\{" + env + r"\}.*?\\end\{" + env + r"\}", " ", s, flags=re.S)
        s = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", s)
        s = s.replace("{", " ").replace("}", " ").replace("$", " ")
        out.append(s)
    return " ".join(" ".join(out).split())


def main() -> int:
    txt = body_text()
    words = len(txt.split())
    sents = [x for x in re.split(r"(?<=[.!?])\s+", txt) if len(x.split()) > 3]
    lens = [len(x.split()) for x in sents]

    print(f"{words} words of body prose, {len(sents)} sentences")
    print(f"sentence length  mean {statistics.mean(lens):.1f}  median {statistics.median(lens)}  "
          f"stdev {statistics.stdev(lens):.1f}")
    # Uniformity is the tell, not length. Human technical prose mixes 6-word sentences with 45-word
    # ones; generated prose clusters. A healthy spread has real mass at both ends.
    print(f"  under 12 words: {sum(1 for l in lens if l < 12) / len(lens) * 100:4.1f}%"
          f"   over 35 words: {sum(1 for l in lens if l > 35) / len(lens) * 100:4.1f}%")
    print()
    print(f"{'marker':<26}{'count':>7}{'per 10k words':>15}")
    for name, pat in MARKERS.items():
        flags = 0 if "banned" in name else re.I
        n = len(re.findall(pat, txt, flags))
        print(f"  {name:<24}{n:>7}{n / words * 10000:>15.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
