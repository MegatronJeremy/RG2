#!/usr/bin/env python3
"""Find stray control characters in the LaTeX source.

A shell heredoc can turn an escape like \\v or \\t in a replacement string into the literal control
character it names, which lands in the file invisibly. LaTeX may still compile: a VT or FF is silently
absorbed, so the build stays green while the source has lost a command. Only a byte-level scan finds
these, which is why this exists rather than relying on the build.

Tab, newline and carriage return are legitimate (the repo is checked out CRLF on Windows); everything
else in C0, plus DEL and the C1 range, is not.

    py scan_control_chars.py
"""
import glob
import io
import sys
import unicodedata
from pathlib import Path

LATEX = Path(__file__).resolve().parent.parent / "latex"
ALLOWED = {0x09, 0x0A, 0x0D}


def main():
    files = sorted(glob.glob(str(LATEX / "chapters" / "*.tex"))) + [str(LATEX / "main.tex")]
    bad = 0
    for f in files:
        s = io.open(f, encoding="utf-8", newline="").read()
        for i, ch in enumerate(s):
            o = ord(ch)
            if (o < 0x20 and o not in ALLOWED) or o == 0x7F or 0x80 <= o <= 0x9F:
                line = s[:i].count("\n") + 1
                ctx = s[max(0, i - 30):i + 12].replace("\n", "\\n")
                name = unicodedata.name(ch, f"U+{o:04X}")
                print(f"{Path(f).name}:{line}  {hex(o)} ({name})  ...{ctx}...")
                bad += 1
    print(f"{bad} stray control character(s)" if bad else "clean: no stray control characters")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
