#!/usr/bin/env python3
"""Build an email-sized copy of the thesis for sending a draft out.

main.pdf is ~42 MB because latex/figures/ is 45 MB of lossless PNG, several of them wider than any
page needs. That is over the attachment limit of most mail systems, which is a silly reason not to
send a draft. This builds into a scratch directory with downsampled figures and leaves the committed
ones untouched, so the submission artifact is never the compressed one by accident.

    py draft_build.py [--max-width 1400] [--quality 82]

Writes latex/Vuk-Djordjevic-2024-3102-master-rad.pdf, named for the inbox it lands in rather than
the build. Gitignored: it is a working artifact, not the thesis.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

LATEX = Path(__file__).resolve().parent.parent / "latex"
WORK = LATEX / "_draft"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-width", type=int, default=1400,
                    help="downsample any figure wider than this; 1400 still exceeds what a 170 mm "
                         "text column resolves on paper")
    ap.add_argument("--quality", type=int, default=82, help="JPEG quality for photographic figures")
    args = ap.parse_args()

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)

    # Everything the build reads, except figures, which are rewritten below.
    for item in LATEX.iterdir():
        if item.name in ("figures", "_draft", "_sheets") or item.suffix == ".pdf":
            continue
        (shutil.copytree if item.is_dir() else shutil.copy2)(item, WORK / item.name)

    src, dst = LATEX / "figures", WORK / "figures"
    dst.mkdir()
    before = after = 0
    for f in sorted(src.iterdir()):
        before += f.stat().st_size
        if f.suffix.lower() != ".png":
            shutil.copy2(f, dst / f.name)
            after += f.stat().st_size
            continue
        im = Image.open(f).convert("RGB")
        if im.width > args.max_width:
            h = round(im.height * args.max_width / im.width)
            im = im.resize((args.max_width, h), Image.LANCZOS)
        # JPEG rather than optimised PNG: these are photographic renders, where lossless coding is
        # most of the size and buys nothing a reader of a draft will see. pdflatex embeds JPEG
        # directly, so the include just has to name the new extension (rewritten below).
        out = (dst / f.name).with_suffix(".jpg")
        im.save(out, "JPEG", quality=args.quality, optimize=True, progressive=True)
        after += out.stat().st_size
    print(f"figures {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB")

    # Point every include at the .jpg written above. Scratch copy only; the committed sources keep
    # referencing the lossless originals.
    for tex in list(WORK.rglob("*.tex")):
        s = tex.read_text(encoding="utf-8")
        if ".png}" not in s:
            continue
        tex.write_text(s.replace(".png}", ".jpg}"), encoding="utf-8")

    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
                           cwd=WORK, capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        if r.returncode != 0:
            tail = "\n".join(l for l in (r.stdout or "").splitlines() if l.startswith("! "))
            print(f"FAIL: pdflatex exit {r.returncode}\n{tail}")
            return 1

    # Named for the person receiving it, not for the build: this lands in a mentor's inbox and then
    # in a folder beside other students' files, where "main-draft.pdf" identifies nothing. Index
    # number rather than a date, since that is what the faculty tracks a student by; the slash in
    # 2024/3102 is not legal in a filename, hence the dash. ASCII only, because the diacritics in
    # Djordjevic do not survive every mail client and filesystem intact.
    out = LATEX / "Vuk-Djordjevic-2024-3102-master-rad.pdf"
    shutil.copy2(WORK / "main.pdf", out)
    shutil.rmtree(WORK)
    mb = out.stat().st_size / 1e6
    print(f"wrote {out.name}  ({mb:.1f} MB)")
    print(f"  in {LATEX}")
    if mb > 20:
        print("still large for email; try --max-width 1000")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
