import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

UA = {"User-Agent": "Mozilla/5.0"}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=40).read()


# Official-style Senju crest (Wikimedia commons SVG render)
png = get(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Symbole_du_clan_senju.svg/1280px-Symbole_du_clan_senju.svg.png"
)
Path("assets/_ref_senju_mask.png").write_bytes(png)

# Make a preview on white so we can visually inspect
im = Image.open("assets/_ref_senju_mask.png").convert("RGBA")
bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
preview = Image.alpha_composite(bg, im)
preview.convert("RGB").save("assets/_ref_senju_preview.jpg", quality=95)
print("mask", im.size, "saved preview")

# Also try klipartz download endpoints commonly used
html = get("https://www.klipartz.com/en/sticker-png-qhdvu").decode("utf-8", "ignore")
# look for image CDN links
cands = re.findall(r"https?://[^\"']+qhdvu[^\"']+\.png", html)
cands += re.findall(r"https?://[^\"']+/png-clipart[^\"']+\.png", html)
cands += re.findall(r'data-src=\"(https?://[^\"]+)\"', html)
print("klipartz cands", cands[:10])
for i, u in enumerate(cands[:5]):
    try:
        data = get(u)
        Path(f"assets/_ref_klip_{i}.png").write_bytes(data)
        print("saved klip", i, len(data), u[:100])
    except Exception as e:
        print("klip fail", i, e)
