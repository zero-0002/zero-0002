import re
from pathlib import Path

from PIL import Image, ImageDraw

svg = Path("assets/senju-crest-skills.svg").read_text(encoding="utf-8")
m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
W, H = int(m.group(1)), int(m.group(2))
canvas = Image.new("RGB", (W, H), (255, 255, 255))
draw = ImageDraw.Draw(canvas)

coords = re.findall(
    r'<svg x="([0-9.]+)" y="([0-9.]+)" width="(\d+)" height="\d+"',
    svg,
)
print("icons", len(coords), "canvas", W, H)
for xs, ys, ws in coords:
    x, y, w = float(xs), float(ys), float(ws)
    draw.rectangle([x, y, x + w, y + w], outline=(200, 30, 30), width=2)
    draw.rectangle([x + 3, y + 3, x + w - 3, y + w - 3], fill=(220, 60, 60))

canvas.save("assets/_preview_senju_layout.jpg", quality=92)
print("saved assets/_preview_senju_layout.jpg")
