#!/usr/bin/env python3
"""Country of every point in data/trip.json, from OpenStreetMap (Nominatim reverse lookup).
One request a second, as Nominatim asks. Writes cache/countries.json (point id -> country name in
English); export.py adds it to the trip data. Resumes where it stopped."""
import json, os, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
OUT = os.path.join(HERE, "cache", "countries.json")
UA = {"User-Agent": "PersonalTripMontage/1.0 (family trip website; https://github.com/LifeInAVan/EuropeAfricaVanTour)"}

trip = json.load(open(os.path.join(ROOT, "data", "trip.json"), encoding="utf-8"))
done = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
for n, p in enumerate(trip["points"], 1):
    if p["id"] in done: continue
    url = "https://nominatim.openstreetmap.org/reverse?" + urllib.parse.urlencode(
        dict(format="jsonv2", lat=p["lat"], lon=p["lon"], zoom=5, **{"accept-language": "en"}))
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                a = json.load(r).get("address", {})
            break
        except Exception as e:
            print("retry", p["id"], e, flush=True); time.sleep(10 * (k + 1))
    else:
        continue
    done[p["id"]] = a.get("country", "")
    json.dump(done, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    print(f"{n}/{len(trip['points'])}", p["id"], done[p["id"]], flush=True)
    time.sleep(1.1)
# OpenStreetMap labels these two "Sahrawi Arab Democratic Republic", but both lie north of 27°40' N,
# inside Morocco's internationally recognised border, and the trip plan treats them as Morocco.
FIX = {"tarfaya": "Morocco", "khenifiss-national-park": "Morocco"}
done.update({k: v for k, v in FIX.items() if k in done})
json.dump(done, open(OUT, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("missing:", [p["id"] for p in trip["points"] if not done.get(p["id"])])
