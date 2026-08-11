import re
from pathlib import Path

from PIL import Image, ImageDraw

under = Image.open("assets/senju-crest-underlay.png").convert("RGBA")
bg = Image.new("RGBA", under.size, (255, 255, 255, 255))
canvas = Image.alpha_composite(bg, under)
draw = ImageDraw.Draw(canvas)

svg = Path("assets/senju-crest-skills.svg").read_text(encoding="utf-8")
coords = re.findall(
    r'<svg x="([0-9.]+)" y="([0-9.]+)" width="(\d+)" height="\d+"',
    svg,
)
print("icons", len(coords), "size", under.size)
for xs, ys, ws in coords:
    x, y, w = float(xs), float(ys), float(ws)
    draw.rectangle([x, y, x + w, y + w], outline=(220, 40, 40), width=2)
    draw.rectangle([x + 2, y + 2, x + w - 2, y + w - 2], fill=(220, 60, 60, 160))

canvas.convert("RGB").save("assets/_preview_senju_from_render.jpg", quality=92)
print("saved assets/_preview_senju_from_render.jpg")
