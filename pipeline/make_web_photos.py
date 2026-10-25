#!/usr/bin/env python3
"""Web copies of the chosen slideshow photos, from data/photo_picks.json.

For each point: assets/web/<point>/<n>.jpg (1200 px on the long side) and <n>-s.jpg (400 px thumbnail);
0 is the main photo. No metadata is kept. Writes data/photos.json (photos per point, main first) and
assets/web/credits.json, which build_credits.py adds to data/credits.json.
python pipeline/make_web_photos.py               saved (reviewed) points only
python pipeline/make_web_photos.py --chapter 1   one chapter
"""
import json, os, io, sys, time, hashlib, glob, urllib.parse
from PIL import Image, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_slides import http, log

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
WEB = os.path.join(ROOT, "assets", "web")
BIG, SMALL = 1200, 400
def load(p, default=None): return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default
def dump(o, p): json.dump(o, open(p, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

trip = load(os.path.join(ROOT, "data", "trip.json"))
cands = load(os.path.join(HERE, "cache", "slides", "candidates.json"), {})
picks = load(os.path.join(ROOT, "data", "photo_picks.json"), {})
photos = load(os.path.join(ROOT, "data", "photos.json"), {})
credits = load(os.path.join(WEB, "credits.json"), {})

def source_url(c):
    """A 1280 px copy from Wikimedia (a standard thumbnail size), else the original."""
    if c["file"].startswith("ov:"): return c["full"]
    name = c["file"].replace(" ", "_"); h = hashlib.md5(name.encode()).hexdigest()
    q = urllib.parse.quote(name)
    if c["w"] <= 1280: return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}"
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/1280px-{q}"

def save(im, path, size):
    im = im.copy(); im.thumbnail((size, size), Image.LANCZOS)
    im.save(path, "JPEG", quality=80 if size > SMALL else 75, optimize=True, progressive=True)

ch = int(sys.argv[sys.argv.index("--chapter") + 1]) if "--chapter" in sys.argv else None
for p in trip["points"]:
    pick = picks.get(p["id"])
    if ch not in (None, p["chapter"]) or not pick or not pick.get("reviewed"): continue
    items = {c["file"]: c for c in cands.get(p["id"], {}).get("items", [])}
    order = [pick["main"]] + [f for f in pick["picks"] if f != pick["main"]] if pick.get("main") else pick["picks"]
    d = os.path.join(WEB, p["id"]); os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, "*.jpg")): os.remove(f)          # choices may have changed
    for k in [k for k in credits if k.startswith(f"assets/web/{p['id']}/")]: del credits[k]
    paths = []
    for n, f in enumerate(order):
        c = items.get(f)
        if not c: log("not in candidates", p["id"], f); continue
        try: im = ImageOps.exif_transpose(Image.open(io.BytesIO(http(source_url(c), raw=True)))).convert("RGB")
        except Exception as e: log("download failed", p["id"], f, e); continue
        rel = f"assets/web/{p['id']}/{len(paths)}.jpg"
        save(im, os.path.join(ROOT, rel), BIG); save(im, os.path.join(ROOT, rel[:-4] + "-s.jpg"), SMALL)
        credits[rel] = dict(place=p["name"], artist=c["artist"], license=c["license"], license_url=c.get("license_url"),
                            source="Wikimedia Commons" if not f.startswith("ov:") else "Openverse", url=c["page"], file=f)
        paths.append(rel); time.sleep(0.5)
    photos[p["id"]] = paths
    log(p["id"], len(paths), "photos")
dump(dict(sorted(photos.items())), os.path.join(ROOT, "data", "photos.json"))
dump(dict(sorted(credits.items())), os.path.join(WEB, "credits.json"))
log("DONE.", sum(map(len, photos.values())), "photos for", len(photos), "points")
