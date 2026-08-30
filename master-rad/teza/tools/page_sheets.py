#!/usr/bin/env python3
"""Render the built thesis into contact sheets for a visual sweep.

Reading 57 pages one image at a time is slow and easy to lose track of; four to a sheet keeps layout
problems (a figure stranded on its own page, a heading orphaned at a page foot, a table running into
the margin, a blank page) visible while still being legible.

Output goes to latex/_sheets/, which .gitignore covers: these are regenerable from main.pdf and go
stale on the next build, so they are never committed.

    py page_sheets.py [pages-per-sheet] [dpi]
"""
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

LATEX = Path(__file__).resolve().parent.parent / "latex"
PDF = LATEX / "main.pdf"
OUT = LATEX / "_sheets"


def main():
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    if not PDF.exists():
        sys.exit("FAIL: main.pdf not found; build first")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    tmp = OUT / "_p"
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(PDF), str(tmp)], check=True)

    pages = sorted(OUT.glob("_p-*.png"))
    if not pages:
        sys.exit("FAIL: pdftoppm produced nothing")

    cols = 2
    rows = (per + cols - 1) // cols
    for i in range(0, len(pages), per):
        chunk = [Image.open(p) for p in pages[i:i + per]]
        w, h = chunk[0].size
        sheet = Image.new("RGB", (w * cols + 12 * (cols + 1), h * rows + 12 * (rows + 1)), "white")
        for j, im in enumerate(chunk):
            x = 12 + (j % cols) * (w + 12)
            y = 12 + (j // cols) * (h + 12)
            sheet.paste(im, (x, y))
        first, last = i + 1, min(i + per, len(pages))
        sheet.save(OUT / f"s{i // per:02d}_p{first}-{last}.png")

    for p in pages:
        p.unlink()
    print(f"{len(pages)} pages -> {len(list(OUT.glob('s*.png')))} sheets in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
