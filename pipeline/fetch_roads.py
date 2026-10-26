#!/usr/bin/env python3
"""Full road route for every leg between consecutive places, for the website -> cache/legs.json.

For each road part of cache/plan.json, OSRM (router.project-osrm.org, one request a second) is asked
for the full road line between each pair of consecutive places: stop, highlights in driving order,
next stop or ferry port. Each leg keeps its distance (km) and driving time (minutes), and its line
simplified to about 40 m. Ferry crossings are kept as their sea lines from plan.json.
Raw OSRM answers are cached in cache/roads/ (not committed); the script resumes where it stopped.
The film keeps using plan.json and road_cache.json, which this does not change.
python pipeline/fetch_roads.py              all legs
python pipeline/fetch_roads.py --segments 2 only the first 2 stop-to-stop segments (a trial)
"""
import json, os, sys, time, hashlib, math, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
RAW = os.path.join(HERE, "cache", "roads"); os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "PersonalTripMontage/1.0 (family trip website; https://github.com/LifeInAVan/EuropeAfricaVanTour)"}
TOL = 0.0004                          # simplification tolerance in degrees, about 40 m

plan = json.load(open(os.path.join(HERE, "cache", "plan.json"), encoding="utf-8"))
trip = json.load(open(os.path.join(ROOT, "data", "trip.json"), encoding="utf-8"))
by_title = {p.get("title", p["name"]): p for p in trip["points"] if p["kind"] == "highlight"}
stops = {p["id"]: p for p in trip["points"] if p["kind"] == "stop"}
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)

def osrm(a, b):
    """Full road line, metres and seconds from a to b (lon, lat); None if OSRM finds no road."""
    key = hashlib.md5(json.dumps([a, b]).encode()).hexdigest()
    f = os.path.join(RAW, key + ".json")
    if os.path.exists(f): return json.load(open(f, encoding="utf-8"))
    url = (f"https://router.project-osrm.org/route/v1/driving/{a[0]},{a[1]};{b[0]},{b[1]}"
           "?overview=full&geometries=geojson&continue_straight=false")
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                rt = json.load(r)["routes"][0]
            out = dict(geom=rt["geometry"]["coordinates"], m=rt["distance"], s=rt["duration"])
            break
        except urllib.error.HTTPError as e:
            if e.code == 400: out = None; break                       # no road between them
            log("retry", k + 1, e); time.sleep(5 * (k + 1))
        except Exception as e:
            log("retry", k + 1, e); time.sleep(5 * (k + 1))
    else:
        raise RuntimeError(f"OSRM failed for {a} -> {b}")
    json.dump(out, open(f, "w", encoding="utf-8", newline="\n"))
    time.sleep(1.1)
    return out

def simplify(pts, tol=TOL):
    """Douglas-Peucker, iterative."""
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        (x1, y1), (x2, y2) = pts[i][:2], pts[j][:2]
        dx, dy = x2 - x1, y2 - y1; n = math.hypot(dx, dy) or 1e-12
        best, idx = 0, None
        for k in range(i + 1, j):
            d = abs(dy * pts[k][0] - dx * pts[k][1] + x2 * y1 - y2 * x1) / n
            if d > best: best, idx = d, k
        if idx is not None and best > tol:
            keep[idx] = True; stack += [(i, idx), (idx, j)]
    return [[round(x, 5), round(y, 5)] for (x, y), k in zip((p[:2] for p in pts), keep) if k]

limit = int(sys.argv[sys.argv.index("--segments") + 1]) if "--segments" in sys.argv else len(plan)
legs, unroutable = [], []
for n, seg in enumerate(plan[:limit], 1):
    here = seg["from"]                                                  # id of the last place reached
    for part in seg["parts"]:
        if part["mode"] == "sea":
            legs.append(dict(mode="sea", **{"from": here}, to=None, km=None, min=None,
                             geom=[[round(x, 4), round(y, 4)] for x, y in part["geom"]]))
            continue
        way = [(here, part["geom"][0])] + [(by_title[t]["id"], [by_title[t]["lon"], by_title[t]["lat"]]) for t in part["hl"]]
        end_id = seg["to"] if part is seg["parts"][-1] else None       # otherwise the road ends at a ferry port
        way.append((end_id, part["geom"][-1]))
        for (fa, a), (fb, b) in zip(way, way[1:]):
            r = osrm(a, b)
            if r is None:
                unroutable.append((fa, fb)); r = dict(geom=[a, b], m=None, s=None)
            legs.append({"mode": "road", "from": fa, "to": fb, "km": round(r["m"] / 1000, 1) if r["m"] is not None else None,
                         "min": round(r["s"] / 60) if r["s"] is not None else None, "geom": simplify(r["geom"])})
        here = end_id if end_id else here
    log(f"{n}/{limit}", seg["from"], ">", seg["to"], "legs so far:", len(legs))

json.dump(legs, open(os.path.join(HERE, "cache", "legs.json"), "w", encoding="utf-8", newline="\n"), separators=(",", ":"))
km = sum(l["km"] or 0 for l in legs); pts = sum(len(l["geom"]) for l in legs)
log(f"DONE. {len(legs)} legs, {km:,.0f} km by road, {pts:,} map points; no road found for: {unroutable}")
