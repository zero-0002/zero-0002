#!/usr/bin/env python3
"""Increase skill icon size in Senju crest SVGs, keeping centers fixed."""

from __future__ import annotations

import re
from pathlib import Path

NEW_SIZE = 60
FILES = [
    Path("assets/senju-crest-skills.svg"),
    Path("assets/senju-crest-skills-dark.svg"),
]


def scale_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'<svg x="([0-9.]+)" y="([0-9.]+)" width="(\d+)" height="(\d+)" viewBox="0 0 256 256">'
    )

    def repl(match: re.Match[str]) -> str:
        x = float(match.group(1))
        y = float(match.group(2))
        old = float(match.group(3))
        cx = x + old / 2
        cy = y + old / 2
        nx = cx - NEW_SIZE / 2
        ny = cy - NEW_SIZE / 2
        return (
            f'<svg x="{nx:.1f}" y="{ny:.1f}" width="{NEW_SIZE}" '
            f'height="{NEW_SIZE}" viewBox="0 0 256 256">'
        )

    new_text, n = pattern.subn(repl, text)
    path.write_text(new_text, encoding="utf-8")
    print(f"{path}: updated {n} icons -> {NEW_SIZE}px")


def main() -> None:
    for path in FILES:
        if path.exists():
            scale_file(path)


if __name__ == "__main__":
    main()
