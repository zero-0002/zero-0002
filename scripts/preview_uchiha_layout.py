import re
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw

# Rasterize a simple preview: draw underlay approx + icon boxes from SVG positions
svg_text = Path("assets/uchiha-crest-skills.svg").read_text(encoding="utf-8")
m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_text)
W, H = int(m.group(1)), int(m.group(2))
canvas = Image.new("RGB", (W, H), (255, 255, 255))
draw = ImageDraw.Draw(canvas)

# Approximate underlay from known constants in generator
CX = W / 2
FAN_CX, FAN_CY = CX, H * 0.40
FAN_R = W * 0.36
# fan circle
bbox = [FAN_CX - FAN_R, FAN_CY - FAN_R, FAN_CX + FAN_R, FAN_CY + FAN_R]
draw.ellipse(bbox, fill=(245, 245, 245), outline=(20, 20, 20), width=6)
# red upper roughly
draw.pieslice(bbox, start=200, end=340, fill=(198, 40, 40))
# handle
hw = W * 0.075
handle_top = FAN_CY + FAN_R * 0.82
draw.rectangle(
    [CX - hw, handle_top, CX + hw, H * 0.93],
    fill=(245, 245, 245),
    outline=(20, 20, 20),
    width=6,
)

coords = re.findall(
    r'<svg x="([0-9.]+)" y="([0-9.]+)" width="(\d+)" height="\d+"',
    svg_text,
)
print("icons", len(coords))
for xs, ys, ws in coords:
    x, y, w = float(xs), float(ys), float(ws)
    draw.rectangle([x, y, x + w, y + w], outline=(30, 30, 30), width=2)
    draw.rectangle([x + 2, y + 2, x + w - 2, y + w - 2], fill=(60, 120, 200))

canvas.save("assets/_preview_uchiha_layout.jpg", quality=92)
print("saved preview")
