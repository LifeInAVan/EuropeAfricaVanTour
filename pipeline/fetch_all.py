#!/usr/bin/env python3
"""Fill gaps: coordinates (Nominatim), photo + credit per highlight (Wikimedia thumbs, else Openverse)."""
import json, os, re, time, hashlib, urllib.request, urllib.parse, io
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
UA = {"User-Agent": "PersonalTripMontage/1.0 (family video project; https://github.com/LifeInAVan/EuropeAfricaVanTour)"}
info = json.load(open(os.path.join(HERE, "cache", "hl_info.json"), encoding="utf-8"))
HLDIR = os.path.join(ROOT, "assets", "_hl"); os.makedirs(HLDIR, exist_ok=True)
cred_path = os.path.join(HLDIR, "credits.json")
cred = json.load(open(cred_path, encoding="utf-8")) if os.path.exists(cred_path) else {}
def log(*a): print(*a, flush=True)
def http(url, raw=False, tries=8, wait=30):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read() if raw else json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(wait); continue
            raise
    raise RuntimeError("rate limited")
def slug(t): return hashlib.md5(t.encode()).hexdigest()[:12]
def save_img(data, path):
    im = Image.open(io.BytesIO(data)).convert("RGB"); im.thumbnail((1600, 1600)); im.save(path, quality=88)

# ---- 1. coordinates for unresolved places (Nominatim, 1 req/s) ----
Q = {"Kravica Waterfall": "Kravica waterfall", "Benagil Cave": "Benagil cave", "Legzira": "Legzira",
     "Portuguese City of Mazagan": "Cité portugaise El Jadida", "Amphitheatre of Tarragona": "Amfiteatre de Tarragona",
     "Haut-Kœnigsbourg Castle": "Château du Haut-Koenigsbourg", "Reichsburg Cochem": "Reichsburg Cochem",
     "Moritzburg Castle (Saxony)": "Schloss Moritzburg", "Āraiši Lake Fortress": "Āraišu ezerpils",
     "Château de Grignan": "Château de Grignan", "Combarro": "Combarro, Poio", "Piódão": "Piódão",
     "Costa Nova do Prado": "Costa Nova, Ílhavo", "Stari Most": "Stari most, Mostar",
     "Mehmed Paša Sokolović Bridge": "Most Mehmed-paše Sokolovića, Višegrad",
     "Đurđevića Tara Bridge": "Đurđevića Tara most", "Stari Bar": "Stari Bar, Bar",
     "Alberobello": "Alberobello", "Bosa": "Bosa, Sardegna", "Stintino": "Stintino",
     "Laguardia": "Laguardia, Álava", "San Millán de la Cogolla": "Monasterio de Yuso",
     "Pinhão": "Pinhão, Alijó", "Comporta": "Comporta", "Taghazout": "Taghazout", "Akka": "Akka, Tata",
     "Ebro Delta": "Delta de l'Ebre", "Cadaqués": "Cadaqués", "Heidelberg Castle": "Heidelberger Schloss",
     "Old Riga": "Vecrīga", "Valaste waterfall": "Valaste juga", "Siida": "Siida, Inari"}
for t, v in info.items():
    if v.get("coords"): continue
    q = Q.get(t, t)
    try:
        r = http("https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + urllib.parse.quote(q))
        time.sleep(1.2)
        if r:
            v["coords"] = (float(r[0]["lon"]), float(r[0]["lat"])); v["missing"] = False
            v.setdefault("resolved", t); v["coord_source"] = "OpenStreetMap"
            log("nominatim ok", t)
        else: log("nominatim none", t)
    except Exception as e: log("nominatim fail", t, e)
    info[t] = v
json.dump(info, open(os.path.join(HERE, "cache", "hl_info.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# ---- 2. licence metadata for Wikimedia-hosted photos (Commons, batched) ----
wm = {t: v for t, v in info.items() if v.get("thumb") and v.get("file") and t not in cred}
files = []  # metadata stage already done (Commons throttled)
for s in range(0, len(files), 40):
    try:
        m = http("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=extmetadata"
                 "&format=json&titles=" + urllib.parse.quote("|".join(files[s:s+40])), wait=60)
    except Exception as e:
        log("commons meta fail", e); break
    for p in m["query"]["pages"].values():
        if "imageinfo" not in p: continue   # not on Commons (likely non-free) -> use Openverse instead
        md = p["imageinfo"][0]["extmetadata"]
        art = re.sub(r"\s+", " ", re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "unknown"))).strip()
        mt = re.search(r"taken by ([^.]+)", art); art = (mt.group(1) if mt else art)[:50]
        lic = md.get("LicenseShortName", {}).get("value", "")
        fn = p["title"].replace("File:", "")
        for t, v in wm.items():
            if v["file"].replace("_", " ") == fn:
                cred[t] = {"artist": art, "license": lic, "source": "Wikimedia Commons", "url": v["thumb"]}
    json.dump(cred, open(cred_path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    log("commons meta batch", s // 40 + 1); time.sleep(5)

# ---- 3. download Wikimedia thumbs (upload host) ----
for t, c in list(cred.items()):
    p = os.path.join(HLDIR, slug(t) + ".jpg")
    if os.path.exists(p) or c.get("source") != "Wikimedia Commons": continue
    try: save_img(http(c["url"], raw=True), p)
    except Exception as e: log("wm dl fail", t, e); cred.pop(t, None)
    time.sleep(0.6)
json.dump(cred, open(cred_path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
log("wikimedia photos:", sum(1 for t in cred if os.path.exists(os.path.join(HLDIR, slug(t) + ".jpg"))))

# ---- 4. Openverse for the rest (20/min, 200/day anonymous) ----
PREF = ["cc0", "pdm", "by", "by-sa", "by-nc", "by-nc-sa"]       # no "nd": we crop the pictures
def openverse(query):
    r = http("https://api.openverse.org/v1/images/?page_size=20&mature=false&license=" + ",".join(PREF) +
             "&q=" + urllib.parse.quote(query), wait=65)
    res = [x for x in r.get("results", []) if x.get("url") and "wikimedia" not in (x.get("url") or "")
           and x.get("source") != "wikimedia"]
    def score(x):
        w, h = x.get("width") or 0, x.get("height") or 0
        return (PREF.index(x["license"]) if x["license"] in PREF else 9, 0 if w >= h else 1, -(w or 0))
    return sorted(res, key=score)
def lic_name(x):
    l = x["license"]; v = x.get("license_version") or ""
    return "CC0" if l == "cc0" else "Public domain" if l == "pdm" else f"CC {l.upper()} {v}".strip()

todo = [t for t in info if t not in cred and info[t].get("coords")]
sights = {"soca": "Soča river valley", "riviera": "Albanian Riviera beach", "rovaniemi": "Rovaniemi Lapland"}
calls = 0
for t in todo + list(sights):
    if calls >= 190: log("openverse daily budget reached"); break
    is_sight = t in sights
    q = sights[t] if is_sight else info[t].get("resolved", t).split(" (")[0]
    try:
        res = openverse(q); calls += 1; time.sleep(3.2)
    except Exception as e:
        log("openverse fail", t, e); continue
    for x in res[:4]:
        try:
            data = http(x["url"], raw=True, tries=1)
            path = (os.path.join(ROOT, "assets", "_sights", t + ".jpg") if is_sight
                    else os.path.join(HLDIR, slug(t) + ".jpg"))
            save_img(data, path)
            entry = {"artist": (x.get("creator") or "unknown")[:50], "license": lic_name(x),
                     "source": f"{x.get('provider', 'Openverse')} via Openverse", "url": x.get("foreign_landing_url")}
            if is_sight:
                sp = os.path.join(ROOT, "assets", "_sights", "credits.json")
                sc = json.load(open(sp, encoding="utf-8")); sc[t] = dict(entry, title=q, file="ov:" + x["id"])
                json.dump(sc, open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
            else:
                cred[t] = entry; json.dump(cred, open(cred_path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
            log("openverse ok", t, "|", entry["license"]); break
        except Exception:
            continue
    else:
        log("openverse none", t)
n = sum(1 for t in info if os.path.exists(os.path.join(HLDIR, slug(t) + ".jpg")))
log(f"highlight photos: {n} of {len(info)}"); log("DONE")
