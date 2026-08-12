#!/usr/bin/env python3
"""Make Senju crest underlay theme-aware: black in light mode, light grey in dark mode."""

from __future__ import annotations

import base64
import io
import re
from pathlib import Path

from PIL import Image

SVG_PATH = Path("assets/senju-crest-skills.svg")


def main() -> None:
    text = SVG_PATH.read_text(encoding="utf-8")
    match = re.search(
        r'<image href="data:image/png;base64,([^"]+)"([^/]*)/>',
        text,
    )
    if not match:
        raise SystemExit("underlay image not found")

    b64_black = match.group(1)
    attrs = match.group(2)
    img = Image.open(io.BytesIO(base64.b64decode(b64_black))).convert("RGBA")
    print(f"underlay {img.size}")

    grey = Image.new("RGBA", img.size, (0, 0, 0, 0))
    src = img.load()
    dst = grey.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = src[x, y]
            if a > 20:
                dst[x, y] = (200, 200, 200, min(255, int(a * 0.95)))

    buf = io.BytesIO()
    grey.save(buf, format="PNG")
    b64_grey = base64.b64encode(buf.getvalue()).decode("ascii")

    style = """  <style>
    .crest-light { opacity: 0.88; }
    .crest-dark { opacity: 0; }
    @media (prefers-color-scheme: dark) {
      .crest-light { opacity: 0; }
      .crest-dark { opacity: 0.9; }
    }
  </style>
"""
    black_img = (
        f'  <image class="crest-light" href="data:image/png;base64,{b64_black}"{attrs}/>'
    )
    grey_img = (
        f'  <image class="crest-dark" href="data:image/png;base64,{b64_grey}"{attrs}/>'
    )
    replacement = style + black_img + "\n" + grey_img
    new_text = text[: match.start()] + replacement + text[match.end() :]
    SVG_PATH.write_text(new_text, encoding="utf-8")
    print(f"updated {SVG_PATH} ({SVG_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
