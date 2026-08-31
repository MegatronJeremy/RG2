#!/usr/bin/env python3
"""Build a line-numbered review copy of the thesis, without touching main.tex.

Reviewing a 63-page PDF and writing "the paragraph about the denoiser on page 31 is too strong" is
ambiguous: there are several, and page numbers move on the next build. With line numbers a note is
"p31 L412", which points at one line and survives edits elsewhere in the document.

The review copy is built from a temporary copy of main.tex with the lineno package injected, so
main.pdf (the submission artifact) is never touched and main.tex never carries review scaffolding
that could be committed by accident.

    py review_build.py            # -> latex/main-review.pdf

Output is gitignored: it is a working artifact, regenerable from the sources at any time.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

LATEX = Path(__file__).resolve().parent.parent / "latex"
SRC = LATEX / "main.tex"
STEM = "main-review"

# modulo=false numbers every line, not every fifth: a note can then name any line, and the cost is
# only ink in a copy nobody submits.
INJECT = r"""
\usepackage[mathlines, displaymath]{lineno}
\renewcommand\thelinenumber{\arabic{linenumber}}
\setlength\linenumbersep{1.2em}
\linenumbers
"""


def main() -> int:
    if not SRC.exists():
        sys.exit(f"FAIL: {SRC} not found")

    text = SRC.read_text(encoding="utf-8")
    if "\\begin{document}" not in text:
        sys.exit("FAIL: no \\begin{document} in main.tex")
    text = text.replace("\\begin{document}", INJECT + "\n\\begin{document}", 1)

    tmp = LATEX / f"{STEM}.tex"
    tmp.write_text(text, encoding="utf-8")

    try:
        for _ in range(2):  # twice, for the TOC and cross-references
            r = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{STEM}.tex"],
                cwd=LATEX, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode != 0:
                tail = "\n".join(l for l in (r.stdout or "").splitlines() if l.startswith("! "))
                sys.exit(f"FAIL: pdflatex exit {r.returncode}\n{tail}")
    finally:
        for ext in (".tex", ".aux", ".log", ".out", ".toc", ".lof", ".lot"):
            (LATEX / f"{STEM}{ext}").unlink(missing_ok=True)

    pdf = LATEX / f"{STEM}.pdf"
    if not pdf.exists():
        sys.exit("FAIL: no PDF produced")
    print(f"wrote {pdf}  ({pdf.stat().st_size // 1024} KB)")
    print("Line numbers run continuously through the document, so 'L735' alone identifies a line.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
