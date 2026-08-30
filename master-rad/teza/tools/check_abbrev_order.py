#!/usr/bin/env python3
"""Check that the abbreviations list is alphabetical.

The list was authored in Serbian and translated in place, so entries keep the slot their Serbian term
sorted into: "zauzetost" sorted last and its English replacement "occupancy" inherited that position.
Sorting is the whole point of the list, so it is worth checking rather than eyeballing.

    py check_abbrev_order.py [--fix]
"""
import io
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "latex" / "chapters" / "00-skracenice.tex"
ITEM = re.compile(r"\\item\[(.*?)\]", re.S)


def sort_key(label):
    """Compare on letters only, case-insensitively, with LaTeX accent macros stripped."""
    s = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", label)   # \v{c} -> c
    s = re.sub(r"\\[`'\"^~=.]", "", s)                     # \` and friends
    return re.sub(r"[^a-z]", "", s.lower())


def main():
    text = io.open(SRC, encoding="utf-8").read()
    entries = ITEM.findall(text)
    keys = [sort_key(e) for e in entries]
    bad = [(i, entries[i]) for i in range(1, len(entries)) if keys[i] < keys[i - 1]]
    for i, e in bad:
        print(f"out of order at {i}: {e!r} follows {entries[i - 1]!r}")
    print(f"{len(entries)} entries, {len(bad)} out of order")

    if bad and "--fix" in sys.argv:
        # split into the leading text and the \item blocks, reorder the blocks, put them back
        first = text.index("\\item[")
        head, body = text[:first], text[first:]
        end = body.rindex("\\end{description}")
        items_txt, tail = body[:end], body[end:]
        blocks = re.split(r"(?=\\item\[)", items_txt)
        blocks = [b for b in blocks if b.strip()]
        blocks.sort(key=lambda b: sort_key(ITEM.search(b).group(1)))
        io.open(SRC, "w", encoding="utf-8").write(head + "".join(blocks) + tail)
        print("reordered")
        return 0
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
