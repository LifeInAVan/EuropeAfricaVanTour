#!/usr/bin/env python3
"""Map position of each festival place in festival_rules.py, from OpenStreetMap (Nominatim, one request a
second) -> cache/festival_places.json, keyed by the search text. Resumes: places already found are kept.
Prints each festival's distance from the nearest place on the route, so wrong look-ups stand out."""
import json, os, math, time, urllib.request, urllib.parse
from festival_rules import R

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "cache", "festival_places.json")
UA = {"User-Agent": "PersonalTripMontage/1.0 (family trip website; https://github.com/LifeInAVan/EuropeAfricaVanTour)"}
done = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
# Set by hand where OpenStreetMap finds a namesake elsewhere (checked 27 Oct 2026)
FIX = {"Tafraout, Morocco": [29.7226, -8.9752], "Taliouine, Morocco": [30.531, -7.923], "Rissani, Morocco": [31.2817, -4.2641]}
done.update(FIX)
json.dump(done, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))

queries = {q.split("@")[0].strip() for _, place in R.values() if not place.startswith("country:") for q in place.split(" / ")}
for q in sorted(queries - set(done)):
    url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + urllib.parse.quote(q)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: hit = json.load(r)
    done[q] = [round(float(hit[0]["lat"]), 4), round(float(hit[0]["lon"]), 4)] if hit else None
    print("found" if hit else "NOT FOUND", q, done[q], flush=True)
    json.dump(done, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    time.sleep(1.1)

trip = json.load(open(os.path.join(ROOT, "data", "trip.json"), encoding="utf-8"))
pts = [(p["lat"], p["lon"]) for p in trip["points"]]
for (ch, ev), (_, place) in R.items():
    if place.startswith("country:"): continue
    for q in place.split(" / "):
        q = q.split("@")[0].strip(); c = done.get(q)
        d = min(km(c, p) for p in pts) if c else None
        if d is None or d > 60: print(f"check: chapter {ch} {ev} – {q}: {'not found' if d is None else f'{d:.0f} km from the route'}")
