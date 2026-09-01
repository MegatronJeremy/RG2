#!/usr/bin/env python3
"""Run every mechanical check on the thesis and report one verdict.

These checks were eight separate commands run by hand, which meant "is the thesis clean" depended on
remembering all of them. Each one here is objective (a build result, a count, a diff against
generated data), so none of them churns: a green run today stays green unless something actually
changes. Judgement calls (is this paragraph clear, is this claim too strong) are deliberately NOT
here, since those cannot be automated and re-litigating them is what makes a review loop endless.

    py check_thesis.py            # everything
    py check_thesis.py --fast     # skip the two pdflatex passes

Exit 0 = all gates pass. Exit 1 = at least one failed.
"""
import argparse
import io
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
LATEX = TOOLS.parent / "latex"
CHAPTERS = LATEX / "chapters"
GENERATORS = ["gen_perf_tables", "gen_quality_tables", "gen_shader_tables", "gen_perf_plots"]

results: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def check_build() -> None:
    """Two pdflatex passes (cross-references need the second), then read the log, not the console."""
    for i in (1, 2):
        code, out = run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], LATEX)
        if code != 0:
            # A PDF viewer holding main.pdf open makes pdflatex fail to write it, which looks
            # identical to a broken document from the exit code alone. It is the normal case while
            # the thesis is being read, so name it rather than sending the reader after a LaTeX
            # error that is not there.
            if "can't write on file" in out or "cannot write on file" in out:
                # The aborted run also leaves a half-written main.aux, which makes the NEXT build
                # fail on a bogus undefined control sequence pointing into the aux rather than the
                # source. Clear it here so the lock costs one message instead of a second hunt.
                for ext in (".aux", ".toc", ".lof", ".lot", ".out"):
                    (LATEX / f"main{ext}").unlink(missing_ok=True)
                record("pdflatex", False,
                       "main.pdf is LOCKED (close your PDF viewer). The document is fine; "
                       "stale aux files cleared, so just re-run")
            else:
                record(f"pdflatex pass {i}", False, f"exit {code}")
            return
    record("pdflatex (2 passes)", True, "exit 0")

    log = io.open(LATEX / "main.log", encoding="utf-8", errors="replace").read()
    errs = re.findall(r"(?m)^! .*", log)
    undef = re.findall(r"(?i)undefined (reference|citation)", log)
    over = re.findall(r"Overfull", log)
    record("no LaTeX errors", not errs, f"{len(errs)} found")
    record("no undefined refs/cites", not undef, f"{len(undef)} found")
    record("no overfull boxes", not over, f"{len(over)} found")


def check_citations() -> None:
    """Every \\bibitem cited and every \\cite defined. LaTeX warns about the second, never the first."""
    bib = set(re.findall(r"\\bibitem\{([^}]+)\}",
                         io.open(CHAPTERS / "99-literatura.tex", encoding="utf-8").read()))
    cited: set[str] = set()
    for f in list(CHAPTERS.glob("*.tex")) + [LATEX / "main.tex"]:
        for group in re.findall(r"\\cite\{([^}]*)\}", io.open(f, encoding="utf-8").read()):
            cited |= {c.strip() for c in group.split(",") if c.strip()}
    record("no uncited bibitems", not (bib - cited), ", ".join(sorted(bib - cited)) or "clean")
    record("no missing bibitems", not (cited - bib), ", ".join(sorted(cited - bib)) or "clean")


def check_captions() -> None:
    """A float with no short caption puts its whole paragraph in the List of Figures."""
    bare = 0
    for f in CHAPTERS.glob("*.tex"):
        bare += len(re.findall(r"\\caption\{", io.open(f, encoding="utf-8").read()))
    record("all captions have a short form", bare == 0, f"{bare} without")


def check_emdash() -> None:
    hits = []
    for f in list(CHAPTERS.glob("*.tex")) + [LATEX / "main.tex"]:
        n = io.open(f, encoding="utf-8").read().count("\u2014")
        if n:
            hits.append(f"{f.name}:{n}")
    record("no em-dashes", not hits, ", ".join(hits) or "clean")


def check_subscript(name: str, script: str, args: list[str] | None = None) -> None:
    code, out = run([sys.executable, script, *(args or [])], TOOLS)
    record(name, code == 0, out.strip().splitlines()[-1] if out.strip() else f"exit {code}")


def check_generators() -> None:
    for g in GENERATORS:
        code, _ = run([sys.executable, f"{g}.py", "--check"], TOOLS)
        record(f"{g} in sync", code == 0, "" if code == 0 else "STALE: regenerate")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="skip the two pdflatex passes")
    args = ap.parse_args()

    if not args.fast:
        check_build()
    check_citations()
    check_captions()
    check_emdash()
    check_subscript("float labels all referenced", "check_float_refs.py")
    check_subscript("no stray control chars", "scan_control_chars.py")
    check_subscript("abbreviations sorted", "check_abbrev_order.py")
    check_generators()

    width = max(len(n) for n, _, _ in results)
    for name, ok, detail in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} gates pass")
    if failed:
        print("FAILED: " + ", ".join(failed))
        return 1

    # Advisory, never gated: legitimate serial-list semicolons exist, so a count is information
    # rather than a verdict, and gating it would force bad rewrites of correct lists.
    code, out = run([sys.executable, "scan_semicolons.py"], TOOLS)
    tail = out.strip().splitlines()[-1] if out.strip() else ""
    print(f"(advisory) {tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
