#!/usr/bin/env python3
"""Arrange skill icons along the exact Senju crest in _ref_senju_render.png."""

from __future__ import annotations

import base64
import io
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ICONS = [
    "python",
    "pytorch",
    "tensorflow",
    "scikitlearn",
    "fastapi",
    "anaconda",
    "opencv",
    "docker",
    "kubernetes",
    "azure",
    "aws",
    "gcp",
    "terraform",
    "githubactions",
    "github",
    "prometheus",
    "html",
    "css",
    "javascript",
    "typescript",
    "react",
    "nextjs",
    "nodejs",
    "expressjs",
    "nestjs",
    "graphql",
    "mongodb",
    "postgresql",
    "redis",
    "prisma",
    "tailwindcss",
    "figma",
    "flutter",
    "dart",
    "kotlin",
    "androidstudio",
    "java",
    "firebase",
    "swift",
    "apple",
]

UA = {"User-Agent": "Mozilla/5.0"}
ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "assets" / "_ref_senju_render.png"
OUT = ROOT / "assets" / "senju-crest-skills.svg"
CACHE = ROOT / "assets" / ".skillicons-cache"
UNDERLAY = ROOT / "assets" / "senju-crest-underlay.png"

ICON = 60
PAD = 28


def fetch_icon(name: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE / f"{name}.svg"
    if cache_file.exists():
        raw = cache_file.read_text(encoding="utf-8")
    else:
        url = f"https://skillicons.dev/icons?i={name}"
        req = urllib.request.Request(url, headers=UA)
        last_err: Exception | None = None
        raw = ""
        for _ in range(3):
            try:
                raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
                break
            except Exception as exc:  # noqa: BLE001
                last_err = exc
        else:
            raise RuntimeError(f"failed to fetch {name}: {last_err}")
        cache_file.write_text(raw, encoding="utf-8")

    match = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S | re.I)
    if not match:
        raise RuntimeError(f"bad svg for {name}")
    inner = match.group(1)
    prefix = re.sub(r"[^a-z0-9]+", "", name.lower()) + "_"
    inner = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}{m.group(1)}"', inner)
    inner = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{prefix}{m.group(1)})", inner)
    inner = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{prefix}{m.group(1)}"', inner)
    return inner


def prepare_mask() -> tuple[Image.Image, Image.Image, int, int]:
    """Crop crest from render, return (rgba_crest, binary_mask, W, H)."""
    src = Image.open(REF).convert("RGB")
    gray = src.convert("L")
    # ink = dark pixels
    bw = gray.point(lambda v: 255 if v < 140 else 0)
    # tight bbox of ink
    bbox = bw.getbbox()
    if not bbox:
        raise RuntimeError("no crest ink found in reference render")
    l, t, r, b = bbox
    # pad around crest
    l = max(0, l - PAD)
    t = max(0, t - PAD)
    r = min(src.width, r + PAD)
    b = min(src.height, b + PAD)

    cropped_rgb = src.crop((l, t, r, b))
    cropped_bw = bw.crop((l, t, r, b))

    # Scale up so icons have room along strokes
    scale = 2.2
    W = int(cropped_rgb.width * scale)
    H = int(cropped_rgb.height * scale)
    crest_rgb = cropped_rgb.resize((W, H), Image.Resampling.LANCZOS)
    mask = cropped_bw.resize((W, H), Image.Resampling.NEAREST)
    # thicken strokes so larger icon centers stay on the crest
    mask = mask.filter(ImageFilter.MaxFilter(13))

    # Transparent underlay: black crest on transparent
    rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = crest_rgb.convert("L")
    for y in range(H):
        for x in range(W):
            if g.getpixel((x, y)) < 140:
                rgba.putpixel((x, y), (15, 15, 15, 230))
    rgba.save(UNDERLAY)
    return rgba, mask, W, H


def collect_points(mask: Image.Image) -> list[tuple[int, int]]:
    pix = mask.load()
    w, h = mask.size
    pts: list[tuple[int, int]] = []
    step = 3
    for y in range(0, h, step):
        for x in range(0, w, step):
            if pix[x, y] > 0:
                pts.append((x, y))
    return pts


def place_icons(points: list[tuple[int, int]], count: int, w: int, h: int) -> list[tuple[float, float]]:
    """Evenly distribute icons along crest ink via farthest-point sampling."""
    if not points:
        raise RuntimeError("empty mask")

    cx, cy = w / 2, h / 2

    def nearest(x: float, y: float) -> tuple[float, float]:
        px, py = min(points, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)
        return float(px), float(py)

    # Seed with crest landmarks so silhouette stays readable, then densify evenly.
    seeds = [
        (cx, cy),
        (w * 0.05, cy),
        (w * 0.95, cy),
        (cx, h * 0.18),
        (cx, h * 0.82),
        (w * 0.16, h * 0.26),
        (w * 0.16, h * 0.74),
        (w * 0.84, h * 0.26),
        (w * 0.84, h * 0.74),
        (w * 0.26, h * 0.34),
        (w * 0.26, h * 0.66),
        (w * 0.74, h * 0.34),
        (w * 0.74, h * 0.66),
    ]

    picked: list[tuple[float, float]] = []
    min_seed_d2 = (ICON * 0.85) ** 2
    for ax, ay in seeds:
        p = nearest(ax, ay)
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= min_seed_d2 for q in picked):
            picked.append(p)

    # Candidate pool (subsample for speed)
    stride = max(1, len(points) // 2500)
    candidates = [points[i] for i in range(0, len(points), stride)]
    if len(candidates) < count * 4:
        candidates = points[:]

    # Farthest-point sampling until we have `count` icons
    while len(picked) < count:
        best = None
        best_d = -1.0
        for x, y in candidates:
            d = min((x - qx) ** 2 + (y - qy) ** 2 for qx, qy in picked)
            if d > best_d:
                best_d = d
                best = (float(x), float(y))
        if best is None:
            break
        picked.append(best)

    if len(picked) < count:
        raise RuntimeError(f"only placed {len(picked)}/{count}")
    return picked[:count]


def main() -> None:
    print(f"using reference shape: {REF}")
    rgba, mask, W, H = prepare_mask()
    print(f"canvas {W}x{H}")
    points = collect_points(mask)
    print(f"ink samples: {len(points)}")

    print(f"fetching {len(ICONS)} skill icons...")
    inners: dict[str, str] = {}
    for i, name in enumerate(ICONS):
        inners[name] = fetch_icon(name)
        print(f"  [{i + 1}/{len(ICONS)}] {name}")

    slots = place_icons(points, len(ICONS), W, H)
    print(f"placed {len(slots)} icons along reference crest")

    # Embed underlay as faint guide + icons on top
    buf = io.BytesIO()
    rgba.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    half = ICON / 2
    parts = [
        f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="100%" height="100%" fill="transparent"/>
  <image href="data:image/png;base64,{b64}" x="0" y="0" width="{W}" height="{H}" opacity="0.88"/>
"""
    ]
    for name, (x, y) in zip(ICONS, slots):
        parts.append(
            f"""  <svg x="{x - half:.1f}" y="{y - half:.1f}" width="{ICON}" height="{ICON}" viewBox="0 0 256 256">
{inners[name]}
  </svg>
"""
        )
    parts.append("</svg>\n")
    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
