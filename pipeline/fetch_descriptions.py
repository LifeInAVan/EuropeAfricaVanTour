#!/usr/bin/env python3
"""Short descriptions for the place pages -> data/descriptions.json, from the opening sentences of each
place's English Wikipedia article (REST summary). Wikipedia text is CC BY-SA: the site shows it with
"From Wikipedia" and a link to the article.

An article is used only if it is a normal article (not a list of meanings) and, where Wikipedia gives
coordinates, they are within 30 km of the place (stops and unchecked names must also have them).
At most two sentences or about 300 characters. Resumes where it stopped (cache/descriptions/).
"""
import json, os, re, time, math, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
RAW = os.path.join(HERE, "cache", "descriptions"); os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "PersonalTripMontage/1.0 (family trip website; https://github.com/LifeInAVan/EuropeAfricaVanTour)"}
trip = json.load(open(os.path.join(ROOT, "data", "trip.json"), encoding="utf-8"))

def summary(title):
    f = os.path.join(RAW, re.sub(r"[^\w-]+", "_", title)[:120] + ".json")
    if os.path.exists(f): return json.load(open(f, encoding="utf-8"))
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_"), safe="")
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: d = json.load(r)
    except urllib.error.HTTPError as e:
        d = {"type": "missing", "status": e.code}
    json.dump(d, open(f, "w", encoding="utf-8", newline="\n"), ensure_ascii=False)
    time.sleep(0.3)
    return d

def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))

def short(text, limit=300):
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text.strip())
    out = sentences[0]
    if len(sentences) > 1 and len(out) + len(sentences[1]) < limit: out += " " + sentences[1]
    return out

out, skipped = {}, []
for p in trip["points"]:
    checked = bool(p.get("wikipedia"))
    title = p.get("wikipedia") or p.get("title") or p["name"]
    d = summary(title)
    c = d.get("coordinates")
    ok = d.get("type") == "standard" and d.get("extract") and (
        (c and km((c["lat"], c["lon"]), (p["lat"], p["lon"])) <= 30) or (not c and checked))
    if not ok: skipped.append(p["id"]); continue
    out[p["id"]] = dict(text=short(d["extract"]), title=d.get("title", title), url=d["content_urls"]["desktop"]["page"])
json.dump(dict(note="Opening sentences of each place's English Wikipedia article (CC BY-SA 4.0); shown with a link.",
               places=out), open(os.path.join(ROOT, "data", "descriptions.json"), "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
print(f"written data/descriptions.json: {len(out)} of {len(trip['points'])} places; none for {len(skipped)}:", ", ".join(skipped))
