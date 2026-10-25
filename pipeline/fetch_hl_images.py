#!/usr/bin/env python3
"""Download a Commons photo per highlight + author/licence. Skips non-Commons (non-free) images."""
import json, os, re, time, urllib.request, urllib.parse, hashlib
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
OUT = os.path.join(ROOT, "assets", "_hl"); os.makedirs(OUT, exist_ok=True)
info = json.load(open(os.path.join(HERE, "cache", "hl_info.json"), encoding="utf-8"))
UA = {"User-Agent": "PersonalTripMontage/1.0 (family video project; https://github.com/LifeInAVan/EuropeAfricaVanTour)"}
def get(url, tries=10, raw=False):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read() if raw else json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(20 * (k + 1)); continue
            raise
    raise RuntimeError("rate limit persisted")
def slug(t): return hashlib.md5(t.encode()).hexdigest()[:12]

cred_path = os.path.join(OUT, "credits.json")
cred = json.load(open(cred_path, encoding="utf-8")) if os.path.exists(cred_path) else {}
items = [(t, v) for t, v in info.items() if v.get("thumb") and v.get("file")]
# 1) licence metadata from Commons (only Commons-hosted files are free to reuse)
files = sorted({"File:" + v["file"] for t, v in items if t not in cred})
for s in range(0, len(files), 40):
    m = get("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=extmetadata"
            "&format=json&titles=" + urllib.parse.quote("|".join(files[s:s+40])))
    pages = m["query"]["pages"].values()
    norm = {n["to"]: n["from"] for n in m["query"].get("normalized", [])}
    for p in pages:
        if "imageinfo" not in p: continue          # not on Commons -> skip (likely non-free)
        md = p["imageinfo"][0]["extmetadata"]
        art = re.sub(r"\s+", " ", re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "unknown"))).strip()
        mt = re.search(r"taken by ([^.]+)", art); art = (mt.group(1) if mt else art)[:50]
        lic = md.get("LicenseShortName", {}).get("value", "")
        fn = p["title"].replace("File:", "")
        for t, v in items:
            if v["file"].replace("_", " ") == fn: cred[t] = {"artist": art, "license": lic, "file": v["file"]}
    json.dump(cred, open(cred_path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print("meta", s, flush=True); time.sleep(4)
# 2) images
n_ok = 0
for t, v in items:
    if t not in cred: continue
    p = os.path.join(OUT, slug(t) + ".jpg")
    ok = False
    if os.path.exists(p):
        try: Image.open(p).verify(); ok = True
        except Exception: os.remove(p)
    if not ok:
        try:
            data = get(v["thumb"], raw=True)
            open(p, "wb").write(data); Image.open(p).verify(); ok = True
        except Exception as e:
            if os.path.exists(p): os.remove(p)
            print("fail", t, str(e)[:50], flush=True)
        time.sleep(2.0)
    n_ok += ok
print("images:", n_ok, "of", len(items), "| credited:", len(cred)); print("DONE")
