#!/usr/bin/env python3
"""Page count of the filled form, measured by Word.

The form caps itself at one to two pages, and that limit has to be checked in the application the
faculty will open it in. LibreOffice lays the same file out shorter (it reported 2 where Word reports
3), so a LibreOffice check can pass a document that arrives over the limit.

    py check_pages.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC = HERE / "Obrazlozenje_teme_Vuk_Djordjevic.docx"

PS = r"""
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$d = $w.Documents.Open('{path}')
Write-Output ('pages=' + $d.ComputeStatistics(2))
$d.Close(0); $w.Quit()
"""


def main():
    if not DOC.exists():
        sys.exit(f"FAIL: {DOC.name} not found; run fill_prijava.py first")
    # Word will not open the file if it is already open elsewhere, so measure a copy.
    tmp = Path(tempfile.gettempdir()) / "prijava_pagecheck.docx"
    shutil.copy(DOC, tmp)
    r = subprocess.run(["powershell", "-NoProfile", "-Command", PS.format(path=tmp)],
                       capture_output=True, text=True)
    line = next((l for l in r.stdout.splitlines() if l.startswith("pages=")), None)
    if not line:
        sys.exit(f"FAIL: could not read page count from Word\n{r.stdout}\n{r.stderr}")
    n = int(line.split("=")[1])
    print(f"{n} page(s) in Word", "OK" if n <= 2 else "OVER THE 1-2 PAGE LIMIT")
    return 0 if n <= 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())
