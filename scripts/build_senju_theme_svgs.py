#!/usr/bin/env python3
"""Build light/dark Senju crest SVGs for GitHub prefers-color-scheme."""

from __future__ import annotations

import base64
import io
import re
from pathlib import Path

from PIL import Image

SRC = Path("assets/senju-crest-skills.svg")
OUT_LIGHT = Path("assets/senju-crest-skills.svg")
OUT_DARK = Path("assets/senju-crest-skills-dark.svg")


def main() -> None:
    text = SRC.read_text(encoding="utf-8")

    # Prefer the black crest image if dual already present
    images = re.findall(
        r'<image[^>]*href="data:image/png;base64,([^"]+)"[^/]*/>',
        text,
    )
    if not images:
        raise SystemExit("no underlay images found")

    # First image should be black crest (crest-light) if themed; else the only one
    b64_black = images[0]
    if len(images) > 1:
        # after theme script: crest-light then crest-dark
        classes = re.findall(r'<image class="([^"]+)"', text)
        for cls, b64 in zip(classes, images):
            if cls == "crest-light":
                b64_black = b64
            elif cls == "crest-dark":
                pass

    img = Image.open(io.BytesIO(base64.b64decode(b64_black))).convert("RGBA")
    grey = Image.new("RGBA", img.size, (0, 0, 0, 0))
    src_px = img.load()
    dst_px = grey.load()
    for y in range(img.height):
        for x in range(img.width):
            _r, _g, _b, a = src_px[x, y]
            if a > 20:
                dst_px[x, y] = (200, 200, 200, min(255, int(a * 0.95)))
    buf = io.BytesIO()
    grey.save(buf, format="PNG")
    b64_grey = base64.b64encode(buf.getvalue()).decode("ascii")

    # Strip existing style + crest images, keep icons
    body = re.sub(r"\s*<style>[\s\S]*?</style>\s*", "\n", text)
    body = re.sub(
        r'\s*<image[^>]*href="data:image/png;base64,[^"]+"[^/]*/>\s*',
        "\n",
        body,
        count=2,
    )

    # Insert after transparent rect
    light_underlay = (
        f'  <image href="data:image/png;base64,{b64_black}" '
        f'x="0" y="0" width="1324" height="556" opacity="0.88"/>\n'
    )
    dark_underlay = (
        f'  <image href="data:image/png;base64,{b64_grey}" '
        f'x="0" y="0" width="1324" height="556" opacity="0.9"/>\n'
    )

    def inject(src: str, underlay: str) -> str:
        return re.sub(
            r'(<rect width="100%" height="100%" fill="transparent"/>\s*)',
            r"\1" + underlay,
            src,
            count=1,
        )

    light = inject(body, light_underlay)
    dark = inject(body, dark_underlay)
    OUT_LIGHT.write_text(light, encoding="utf-8")
    OUT_DARK.write_text(dark, encoding="utf-8")
    print(f"wrote {OUT_LIGHT} ({OUT_LIGHT.stat().st_size} bytes)")
    print(f"wrote {OUT_DARK} ({OUT_DARK.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
