import re
import urllib.request
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0"}
assets = Path("assets")
assets.mkdir(exist_ok=True)


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=40).read()


# Wikimedia rendered SVG
for name, url in [
    (
        "assets/_ref_senju_commons.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Symbole_du_clan_senju.svg/1000px-Symbole_du_clan_senju.svg.png",
    ),
    (
        "assets/_ref_senju_fanon.svg",
        "https://static.wikia.nocookie.net/narutofanon/images/8/8d/Senju_Symbol.svg/revision/latest?cb=20170202214343",
    ),
]:
    try:
        data = get(url)
        Path(name).write_bytes(data)
        print("saved", name, len(data))
    except Exception as e:
        print("fail", name, e)

# Sportskeeda article images
html = get(
    "https://www.sportskeeda.com/anime/naruto-s-10-coolest-clan-symbols-meanings"
).decode("utf-8", "ignore")
imgs = re.findall(r"https://staticg\.sportskeeda\.com/[^\"']+\.(?:png|jpg|jpeg|webp)", html)
print("found", len(imgs), "sk images")
for i, u in enumerate(imgs[:12]):
    try:
        data = get(u)
        Path(f"assets/_ref_sk_{i}.jpg").write_bytes(data)
        print("sk", i, len(data), u.split("/")[-1][:80])
    except Exception as e:
        print("sk fail", i, e)

# CBR article
try:
    html = get(
        "https://www.cbr.com/naruto-clan-symbols-meanings-uchiha-senju-uzumaki-hyuga/"
    ).decode("utf-8", "ignore")
    imgs = re.findall(r"https://[^\"']+\.(?:png|jpg|jpeg|webp)", html)
    senjuish = [u for u in imgs if re.search(r"senju|clan|symbol|vajra", u, re.I)]
    print("cbr candidates", len(senjuish))
    for i, u in enumerate(senjuish[:8]):
        try:
            data = get(u)
            Path(f"assets/_ref_cbr_{i}.jpg").write_bytes(data)
            print("cbr", i, len(data), u[:120])
        except Exception as e:
            print("cbr fail", i, e)
except Exception as e:
    print("cbr page fail", e)
