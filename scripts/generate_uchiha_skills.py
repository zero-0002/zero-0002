#!/usr/bin/env python3
"""Shape skill icons into the Uchiha clan crest (uchiwa fan).

Classic crest (Naruto):
  - circular fan body
  - red upper section / white lower section divided by a curved seam
  - rectangular handle at the bottom
"""

from __future__ import annotations

import math
import re
import urllib.request
from pathlib import Path

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
OUT = ROOT / "assets" / "uchiha-crest-skills.svg"
CACHE = ROOT / "assets" / ".skillicons-cache"

W, H = 620, 740
ICON = 42
CX = W / 2
# Fan circle
FAN_CX, FAN_CY = CX, H * 0.40
FAN_R = W * 0.36
# Curved red/white divider (downward bow through the fan)
DIV_Y = FAN_CY + FAN_R * 0.08
DIV_BOW = FAN_R * 0.22


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
    cx: float, cy: float, r: float, a0: float, a1: float, n: int
) -> list[tuple[float, float]]:
    pts = []
    for i in range(n):
        t = i / max(n - 1, 1)
        a = math.radians(lerp(a0, a1, t))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def divider_y_at(x: float) -> float:
    """Y of the red/white curved seam at a given x."""
    # Bow downward: y = DIV_Y + bow * (1 - ((x-cx)/r)^2)
    t = (x - FAN_CX) / FAN_R
    t = max(-1.0, min(1.0, t))
    return DIV_Y + DIV_BOW * (1 - t * t)


def in_fan_circle(x: float, y: float) -> bool:
    return (x - FAN_CX) ** 2 + (y - FAN_CY) ** 2 <= FAN_R**2


def in_handle(x: float, y: float) -> bool:
    hw = W * 0.075
    return abs(x - CX) <= hw and (FAN_CY + FAN_R * 0.85) <= y <= H * 0.93


def in_crest(x: float, y: float) -> bool:
    return in_fan_circle(x, y) or in_handle(x, y)


def uchiha_slots(count: int) -> list[tuple[float, float]]:
    """Fill the Uchiha fan circle + handle with evenly spaced icons."""
    # Build candidate grid across full crest first
    step = ICON * 0.95
    candidates: list[tuple[float, float]] = []
    y = FAN_CY - FAN_R + ICON * 0.55
    row = 0
    while y <= H * 0.92:
        x_off = (step * 0.5) if row % 2 else 0.0
        x = FAN_CX - FAN_R + ICON * 0.55 + x_off
        while x <= FAN_CX + FAN_R - ICON * 0.35:
            if in_fan_circle(x, y) and (x - FAN_CX) ** 2 + (y - FAN_CY) ** 2 <= (
                FAN_R - ICON * 0.3
            ) ** 2:
                candidates.append((x, y))
            x += step
        y += step * 0.86
        row += 1

    # Handle candidates
    handle_pts = sample_line(CX, FAN_CY + FAN_R * 0.95, CX, H * 0.90, 5)
    for p in handle_pts:
        if in_handle(p[0], p[1]):
            candidates.append(p)

    if len(candidates) < count:
        # denser pass
        step = ICON * 0.72
        y = FAN_CY - FAN_R + ICON * 0.4
        row = 0
        denser: list[tuple[float, float]] = []
        while y <= H * 0.92:
            x_off = (step * 0.45) if row % 2 else 0.0
            x = FAN_CX - FAN_R + ICON * 0.4 + x_off
            while x <= FAN_CX + FAN_R:
                if in_crest(x, y):
                    denser.append((x, y))
                x += step
            y += step * 0.8
            row += 1
        candidates = denser

    # Stratify by region so top/bottom/handle all get icons
    upper = [p for p in candidates if in_fan_circle(*p) and p[1] < divider_y_at(p[0])]
    lower = [p for p in candidates if in_fan_circle(*p) and p[1] >= divider_y_at(p[0])]
    handle = [p for p in candidates if in_handle(*p)]

    n_handle = min(4, len(handle), max(3, count // 12))
    n_lower = min(len(lower), max(8, count // 3))
    n_upper = count - n_handle - n_lower
    if n_upper < 10:
        n_upper = max(10, count - n_handle - min(len(lower), 8))
        n_lower = count - n_handle - n_upper

    def take_even(pts: list[tuple[float, float]], n: int) -> list[tuple[float, float]]:
        if n <= 0 or not pts:
            return []
        pts = sorted(pts, key=lambda p: (p[1], p[0]))
        if len(pts) <= n:
            return pts[:]
        return [pts[round(i * (len(pts) - 1) / (n - 1))] for i in range(n)]

    picked = take_even(upper, n_upper) + take_even(lower, n_lower) + take_even(handle, n_handle)

    # Deduplicate near overlaps
    cleaned: list[tuple[float, float]] = []
    min_d2 = (ICON * 0.7) ** 2
    for p in picked:
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= min_d2 for q in cleaned):
            cleaned.append(p)

    # Top up from remaining candidates
    rest = [p for p in sorted(candidates, key=lambda p: (p[1], p[0])) if p not in cleaned]
    relax = min_d2
    while len(cleaned) < count and relax > (ICON * 0.35) ** 2:
        for p in rest:
            if len(cleaned) >= count:
                break
            if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= relax for q in cleaned):
                cleaned.append(p)
        relax *= 0.85

    if len(cleaned) < count:
        raise RuntimeError(f"only placed {len(cleaned)}/{count}")
    return cleaned[:count]


def crest_underlay() -> str:
    """Authentic-looking Uchiha fan: red top, white bottom, handle."""
    # Build clipped red upper via path: circle intersect above divider curve
    # Approximate with circle + white lower overlay + seam stroke
    left = FAN_CX - FAN_R
    right = FAN_CX + FAN_R
    top = FAN_CY - FAN_R
    # Divider curve control points
    c1x, c1y = FAN_CX - FAN_R * 0.35, DIV_Y + DIV_BOW * 1.15
    c2x, c2y = FAN_CX + FAN_R * 0.35, DIV_Y + DIV_BOW * 1.15
    seam = (
        f"M {left},{DIV_Y} "
        f"C {c1x},{c1y} {c2x},{c2y} {right},{DIV_Y}"
    )
    hw = W * 0.075
    handle_top = FAN_CY + FAN_R * 0.82
    handle_bot = H * 0.93
    return f"""  <!-- Uchiha uchiwa underlay -->
  <defs>
    <clipPath id="fanClip">
      <circle cx="{FAN_CX}" cy="{FAN_CY}" r="{FAN_R}"/>
    </clipPath>
  </defs>
  <g>
    <circle cx="{FAN_CX}" cy="{FAN_CY}" r="{FAN_R}" fill="#f5f5f5" stroke="#111" stroke-width="8"/>
    <g clip-path="url(#fanClip)">
      <path d="M {left},{top - 20} L {right},{top - 20} L {right},{DIV_Y + DIV_BOW + 40}
               C {c2x},{c2y + 40} {c1x},{c1y + 40} {left},{DIV_Y + DIV_BOW + 40} Z"
            fill="#C62828"/>
    </g>
    <path d="{seam}" fill="none" stroke="#111" stroke-width="10" stroke-linecap="round"/>
    <rect x="{CX - hw}" y="{handle_top}" width="{hw * 2}" height="{handle_bot - handle_top}"
          fill="#f5f5f5" stroke="#111" stroke-width="8" rx="6"/>
  </g>
"""


def main() -> None:
    print(f"fetching {len(ICONS)} skill icons...")
    inners: dict[str, str] = {}
    for i, name in enumerate(ICONS):
        inners[name] = fetch_icon(name)
        print(f"  [{i + 1}/{len(ICONS)}] {name}")

    slots = uchiha_slots(len(ICONS))
    print(f"placed {len(slots)} icons on Uchiha crest")

    half = ICON / 2
    parts = [
        f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="100%" height="100%" fill="transparent"/>
{crest_underlay()}"""
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
