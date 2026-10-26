#!/usr/bin/env python3
"""data/trip.json for the website: chapters, points (stops and highlights) as day numbers, festivals.
Reads data/route.json, data/chapters.json, data/festivals.json and cache/plan.json + cache/hl_info.json.
Point IDs are made from the place name and stay the same when dates change."""
import json, os, re, unicodedata, urllib.parse
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
def load(*p): return json.load(open(os.path.join(*p), encoding="utf-8"))
route = load(ROOT, "data", "route.json")
chapters = load(ROOT, "data", "chapters.json")["chapters"]
festivals = load(ROOT, "data", "festivals.json")
plan = load(HERE, "cache", "plan.json")
info = load(HERE, "cache", "hl_info.json")
stops = {s["id"]: s for s in route["stops"]}
legs = {l["id"]: l for l in route["legs"]}
START = date.fromisoformat(route["stops"][0]["date"])
TYPE = {"B": "beach", "N": "nature", "C": "culture", "H": "history", "P": "peaceful"}
NOPAGE = {"Kravica Waterfall", "Combarro", "Piódão", "Costa Nova do Prado", "Benagil Cave", "Legzira", "Portuguese City of Mazagan",
          "Amphitheatre of Tarragona", "Château de Grignan", "Haut-Kœnigsbourg Castle", "Reichsburg Cochem",
          "Moritzburg Castle (Saxony)", "Āraiši Lake Fortress", "Fuente Dé"}   # same list as make_doc.py

def day(s): return (date.fromisoformat(s) - START).days
def chapter(d): return next(c["id"] for c in chapters if c["start_day"] <= d <= c["end_day"])
def slug(t):
    t = unicodedata.normalize("NFKD", t.replace("ł", "l").replace("Ł", "L").replace("đ", "d").replace("Đ", "D")
                              .replace("ß", "ss").replace("æ", "ae").replace("ø", "o").replace("œ", "oe"))
    return re.sub(r"[^a-z0-9]+", "-", t.encode("ascii", "ignore").decode().lower()).strip("-")
def osm(lat, lon): return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=14/{lat}/{lon}"

points, used = [], set()
def add(p):
    base = p["id"]; n = 2
    while p["id"] in used: p["id"] = f"{base}-{n}"; n += 1
    used.add(p["id"]); points.append(p)

def add_stop(s):
    d = day(s["date"])
    add(dict(id=s["id"], kind="stop", name=s["name"], caption=s["caption"], day=d, chapter=chapter(d),
             leg=s["leg"], lat=s["lat"], lon=s["lon"], link=osm(s["lat"], s["lon"])))

for seg in plan:
    add_stop(stops[seg["from"]])
    for h in seg["highlights"]:
        t = h["title"]; d = day(h["date"])
        page = not (t in NOPAGE or info.get(t, {}).get("wikipedia_unchecked"))
        add(dict(id=slug(t.split(" (")[0]), kind="highlight", name=h["name"], title=t, caption=h["caption"],
                 type=TYPE[h["type"]], day=d, chapter=chapter(d), leg=stops[seg["from"]]["leg"],
                 lat=round(h["lat"], 5), lon=round(h["lon"], 5),
                 wikipedia=h["name"] if page else None,
                 link="https://en.wikipedia.org/wiki/" + urllib.parse.quote(h["name"].replace(" ", "_")) if page
                      else osm(round(h["lat"], 5), round(h["lon"], 5))))
add_stop(stops[plan[-1]["to"]])
cp = os.path.join(HERE, "cache", "countries.json")                  # from fetch_countries.py
countries = json.load(open(cp, encoding="utf-8")) if os.path.exists(cp) else {}
for p in points: p["country"] = countries.get(p["id"]) or None
points = [{k: v for k, v in p.items() if v is not None} for p in points]

trip = dict(title=route["title"], subtitle=route["subtitle"], start_date=START.isoformat(),
            days=max(c["end_day"] for c in chapters), chapters=chapters,
            legs=list(legs.values()), points=points, ferries=route["ferries"], festivals=festivals)
json.dump(trip, open(os.path.join(ROOT, "data", "trip.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# route line for the map: road and sea parts, split where the chapter changes. Each vertex takes the
# chapter of the nearest place on its leg (the route is drawn through those places in order).
feats = []
for seg in plan:
    a, b = stops[seg["from"]], stops[seg["to"]]
    marks = [(a["lon"], a["lat"], day(a["date"]))] + [(h["lon"], h["lat"], day(h["date"])) for h in seg["highlights"]] \
            + [(b["lon"], b["lat"], day(b["date"]) - 1)]
    near = lambda x, y: chapter(min(marks, key=lambda m: (m[0] - x) ** 2 + (m[1] - y) ** 2)[2])
    for part in seg["parts"]:
        run, cur = [], None
        for x, y in part["geom"]:
            c = near(x, y)
            if cur is not None and c != cur:
                run.append([x, y])
                feats.append(dict(type="Feature", properties=dict(mode=part["mode"], chapter=cur, leg=a["leg"]),
                                  geometry=dict(type="LineString", coordinates=run)))
                run = []
            run.append([x, y]); cur = c
        if len(run) > 1:
            feats.append(dict(type="Feature", properties=dict(mode=part["mode"], chapter=cur, leg=a["leg"]),
                              geometry=dict(type="LineString", coordinates=run)))
json.dump(dict(type="FeatureCollection", features=feats),
          open(os.path.join(ROOT, "data", "route-line.json"), "w", encoding="utf-8", newline="\n"), separators=(",", ":"))
count = {c["id"]:sum(1 for p in points if p["chapter"] == c["id"]) for c in chapters}
print("written data/trip.json:", len(points), "points;", "per chapter:", count)
