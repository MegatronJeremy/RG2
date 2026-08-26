#!/usr/bin/env python3
"""Word count per \\section, so a trim targets the largest blocks instead of shaving everywhere.

    py section_sizes.py [chapter.tex ...]
"""
import glob
import io
import re
import sys
from pathlib import Path

LATEX = Path(__file__).resolve().parent.parent / "latex"

WORD = re.compile(r"[A-Za-z]{2,}")
SEC = re.compile(r"^\\(chapter|section|subsection)\{(.*?)\}", re.M)


def main():
    files = sys.argv[1:] or sorted(glob.glob(str(LATEX / "chapters" / "*.tex")))
    rows = []
    for f in files:
        s = re.sub(r"(?m)^%.*$", "", io.open(f, encoding="utf-8").read())
        marks = [(m.start(), m.group(1), m.group(2)) for m in SEC.finditer(s)]
        marks.append((len(s), "end", ""))
        for i in range(len(marks) - 1):
            start, kind, title = marks[i]
            body = s[start:marks[i + 1][0]]
            rows.append((len(WORD.findall(body)), kind, Path(f).name, title))
    rows.sort(reverse=True)
    for w, kind, fn, title in rows[:26]:
        print("%5d  %-11s %-24s %s" % (w, kind, fn, title[:52]))
    print("\ntotal %d words" % sum(r[0] for r in rows if r[1] != "chapter"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
