#!/usr/bin/env python3
"""Compare each Serbian chapter in latex-sr/chapters/ with its English original in latex/chapters/.

Translation may change prose, never structure or numbers. For every chapter present in latex-sr/
the script compares:
  - the \\label list (as a sorted list, so a duplicated or renamed label shows);
  - the multiset of \\cite / \\ref / \\eqref keys and of generated-number macros (\\perf*, \\q*,
    \\omm*, \\hf*, \\rga*), because a macro is how a measured number reaches the text;
  - the ordered sequence of figure, table, lstlisting, tikzpicture and equation environments;
  - the count of \\section and \\subsection.
Comments are stripped first. Exit code is nonzero on any difference.

    py check_translation_parity.py
    py check_translation_parity.py 01-uvod 05-zakljucak
"""
import io
import re
import sys
from collections import Counter
from pathlib import Path

TEZA = Path(__file__).resolve().parent.parent
EN = TEZA / "latex" / "chapters"
SR = TEZA / "latex-sr" / "chapters"

COMMENT = re.compile(r"(?<!\\)%.*")
LABEL = re.compile(r"\\label\{([^}]*)\}")
KEYED = re.compile(r"\\(cite|ref|eqref)\{([^}]*)\}")
MACRO = re.compile(r"\\((?:perf|omm|rga)[A-Za-z]*|q[A-Z][A-Za-z]*|hf[A-Z][A-Za-z]*)(?![A-Za-z])")
ENV = re.compile(r"\\begin\{(figure\*?|table\*?|lstlisting|tikzpicture|equation\*?|align\*?)\}")
SECTION = re.compile(r"\\(section|subsection)\*?\{")


def read(path):
    text = io.open(path, encoding="utf-8").read()
    return "\n".join(COMMENT.sub("", line) for line in text.splitlines())


def signature(text):
    keyed = Counter()
    for kind, group in KEYED.findall(text):
        for k in group.split(","):
            if k.strip():
                keyed[f"\\{kind}{{{k.strip()}}}"] += 1
    return {
        "labels": sorted(LABEL.findall(text)),
        "keyed refs": keyed,
        "macros": Counter("\\" + m for m in MACRO.findall(text)),
        "environments": [e.rstrip("*") for e in ENV.findall(text)],
        "sections": Counter(SECTION.findall(text)),
    }


def diff(a, b):
    if isinstance(a, Counter):
        return {k: (a[k], b[k]) for k in sorted(set(a) | set(b)) if a[k] != b[k]}
    return None if a == b else (a, b)


def main(argv):
    wanted = set(argv)
    chapters = sorted(p.name for p in SR.glob("*.tex") if not wanted or p.stem in wanted)
    if not chapters:
        print("no Serbian chapters to compare")
        return 1
    problems = 0
    for name in chapters:
        if not (EN / name).exists():
            print(f"{name}: no English original in latex/chapters/")
            problems += 1
            continue
        en, sr = signature(read(EN / name)), signature(read(SR / name))
        bad = 0
        for key in en:
            d = diff(en[key], sr[key])
            if d:
                bad += 1
                print(f"{name}: {key} differ (EN vs SR): {d}")
        problems += bad
        print(f"{name}: {'OK' if not bad else str(bad) + ' difference(s)'} "
              f"({len(en['labels'])} labels, {sum(en['keyed refs'].values())} cite/ref, "
              f"{sum(en['macros'].values())} macros, {len(en['environments'])} environments)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
