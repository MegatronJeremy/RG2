#!/usr/bin/env python3
"""Diff citations and labels against git HEAD, and find uncited bibliography entries.

`thebibliography` silently prints an entry nobody cites, so a trimming pass can orphan a reference
without any LaTeX warning. The undefined-reference check catches the opposite direction only.

    py check_refs.py
"""
import io
import re
import subprocess
from pathlib import Path

LATEX = Path(__file__).resolve().parent.parent / "latex"
REPO = Path(__file__).resolve().parents[3]
CITE = re.compile(r"\\cite\{([^}]*)\}")
LABEL = re.compile(r"\\label\{([^}]*)\}")
BIBITEM = re.compile(r"\\bibitem\{([^}]*)\}")


def keys(pattern, text):
    return {k.strip() for group in pattern.findall(text) for k in group.split(",") if k.strip()}


def main():
    files = sorted(LATEX.glob("chapters/*.tex")) + [LATEX / "main.tex"]
    cur = "".join(io.open(f, encoding="utf-8").read() for f in files)

    old_parts = []
    for f in files:
        rel = f.relative_to(REPO).as_posix()
        r = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, text=True, cwd=REPO)
        if r.returncode == 0:
            old_parts.append(r.stdout)
    old = "".join(old_parts)

    cc, oc = keys(CITE, cur), keys(CITE, old)
    cl, ol = keys(LABEL, cur), keys(LABEL, old)
    bib = keys(BIBITEM, io.open(LATEX / "chapters/99-literatura.tex", encoding="utf-8").read())

    problems = 0
    for name, s in [("cites dropped since HEAD", oc - cc), ("labels dropped since HEAD", ol - cl),
                    ("UNCITED bibitems", bib - cc), ("cited with no bibitem", cc - bib)]:
        if s:
            print(f"{name}: {sorted(s)}")
            problems += len(s)
    print(f"cites added: {sorted(cc - oc)}") if cc - oc else None
    print(f"{len(cc)} cites, {len(cl)} labels, {len(bib)} bibitems, {problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
