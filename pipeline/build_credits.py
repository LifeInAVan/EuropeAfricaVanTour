#!/usr/bin/env python3
"""data/credits.json: one entry per photo under assets/, keyed by its path.
Place photos take their credit from assets/_hl/credits.json, assets/_sights/credits.json and
assets/web/credits.json (slideshows);
photos in the stop folders, _title and _end are our own."""
import json, os, glob, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
A = os.path.join(ROOT, "assets")
OWN = dict(artist="Peter and Dianne Ferry", license="All rights reserved", source="Own photo")

hl = json.load(open(os.path.join(A, "_hl", "credits.json"), encoding="utf-8"))
sights = json.load(open(os.path.join(A, "_sights", "credits.json"), encoding="utf-8"))
out, missing = {}, []
for t, c in hl.items():
    out["assets/_hl/" + hashlib.md5(t.encode()).hexdigest()[:12] + ".jpg"] = dict(
        place=t, artist=c.get("artist"), license=c.get("license"), source=c.get("source"), url=c.get("url"))
for sid, c in sights.items():
    out["assets/_sights/%s.jpg" % sid] = dict(
        place=c.get("title"), stop=sid, artist=c.get("artist"), license=c.get("license"),
        source=c.get("source", "Wikimedia Commons"), url=c.get("url"), file=c.get("file"))
for p in sorted(glob.glob(os.path.join(A, "*", "*.jpg"))):
    rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
    folder = rel.split("/")[1]
    if folder in ("_hl", "_sights"):
        if rel not in out: missing.append(rel)
        continue
    out[rel] = dict(OWN, stop=None if folder.startswith("_") else folder)
web = os.path.join(A, "web", "credits.json")                 # slideshow photos, from make_web_photos.py
if os.path.exists(web): out.update(json.load(open(web, encoding="utf-8")))
out = {k: {f: v for f, v in e.items() if v is not None} for k, e in sorted(out.items())}
json.dump(out, open(os.path.join(ROOT, "data", "credits.json"), "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
print("written data/credits.json:", len(out), "photos")
if missing: print("no credit for:", ", ".join(missing))
