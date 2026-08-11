#!/usr/bin/env python3
"""Build the Senju crest using skill icons as the shape itself.

Authentic crest = Naruto Senju vajra (金剛杵), upright:
vertical shaft + center cross + nested prongs top/bottom.

Reference: Wikimedia File:Symbole_du_clan_senju.svg (rotated upright).
"""

from __future__ import annotations

import math
import re
import urllib.request
from pathlib import Path

from PIL import Image

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
OUT = ROOT / "assets" / "senju-crest-skills.svg"
CACHE = ROOT / "assets" / ".skillicons-cache"
MASK_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/"
    "6/66/Symbole_du_clan_senju.svg/1280px-Symbole_du_clan_senju.svg.png"
)
MASK_PATH = ROOT / "assets" / "_ref_senju_mask.png"
REF_PREVIEW = ROOT / "assets" / "senju-crest-reference.jpg"

# Compact canvas so 40 icons read as a continuous crest
W, H = 520, 920
ICON = 44
CX, CY = W / 2, H / 2


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


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def sample_line(x0: float, y0: float, x1: float, y1: float, n: int) -> list[tuple[float, float]]:
    if n <= 0:
        return []
    if n == 1:
        return [((x0 + x1) / 2, (y0 + y1) / 2)]
    return [(lerp(x0, x1, i / (n - 1)), lerp(y0, y1, i / (n - 1))) for i in range(n)]


def sample_arc(
    cx: float, cy: float, rx: float, ry: float, a0: float, a1: float, n: int
) -> list[tuple[float, float]]:
    pts = []
    for i in range(n):
        t = i / max(n - 1, 1)
        a = math.radians(lerp(a0, a1, t))
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts


def senju_slots() -> list[tuple[float, float]]:
    """40 evenly spaced points forming the upright Senju vajra."""
    slots: list[tuple[float, float]] = []

    # Continuous vertical shaft tip-to-tip (10)
    slots += sample_line(CX, H * 0.04, CX, H * 0.96, 10)

    # Horizontal cross arms (4) excluding hub already on shaft
    slots += sample_line(W * 0.18, CY, W * 0.38, CY, 2)
    slots += sample_line(W * 0.62, CY, W * 0.82, CY, 2)

    # Top outer prong (opens up) — 7
    slots += sample_arc(CX, H * 0.36, W * 0.32, H * 0.20, 195, 345, 7)
    # Top inner prong — 5
    slots += sample_arc(CX, H * 0.38, W * 0.20, H * 0.125, 200, 340, 5)

    # Bottom outer prong (opens down) — 7
    slots += sample_arc(CX, H * 0.64, W * 0.32, H * 0.20, 15, 165, 7)
    # Bottom inner prong — 5
    slots += sample_arc(CX, H * 0.62, W * 0.20, H * 0.125, 20, 160, 5)

    # total = 10+4+7+5+7+5 = 38 → add outer tip flares
    slots += [
        (W * 0.10, CY),
        (W * 0.90, CY),
    ]

    cleaned: list[tuple[float, float]] = []
    min_d2 = (ICON * 0.72) ** 2
    for p in slots:
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= min_d2 for q in cleaned):
            cleaned.append(p)

    # pad if dedupe removed some
    extra = sample_line(CX, H * 0.10, CX, H * 0.90, 20)
    for p in extra:
        if len(cleaned) >= 40:
            break
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= min_d2 * 0.65 for q in cleaned):
            cleaned.append(p)

    return cleaned[:40]


def save_reference() -> None:
    if not MASK_PATH.exists():
        req = urllib.request.Request(MASK_URL, headers=UA)
        MASK_PATH.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    im = Image.open(MASK_PATH).convert("RGBA").transpose(Image.Transpose.ROTATE_90)
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    Image.alpha_composite(bg, im).convert("RGB").save(REF_PREVIEW, quality=95)


def main() -> None:
    save_reference()
    print(f"wrote crest reference: {REF_PREVIEW}")

    print(f"fetching {len(ICONS)} skill icons...")
    inners: dict[str, str] = {}
    for i, name in enumerate(ICONS):
        inners[name] = fetch_icon(name)
        print(f"  [{i + 1}/{len(ICONS)}] {name}")

    slots = senju_slots()
    print(f"placed {len(slots)} icons into upright Senju crest paths")

    half = ICON / 2
    parts = [
        f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="100%" height="100%" fill="transparent"/>
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
