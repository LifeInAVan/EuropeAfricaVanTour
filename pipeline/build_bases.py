#!/usr/bin/env python3
"""The van's route base to base -> cache/base_legs.json, which export.py uses for the drives and the route line.

The van moves only between bases (data/bases.json), passing the base's "on the way" places; day trips from a
base are on foot, by bike or by train and are not van drives. Each road part is fetched from OSRM with the
same cache as fetch_roads.py (cache/roads/). A base reached by ferry ("ferry_in") gets road to the port, the
sea line from data/route.json, and road from the arrival port; on-the-way places go before or after the
sailing as in cache/plan.json.
Each leg: mode, from, to (place ids, or the base id where the base is not a place), km, min, day, base, geom.
Run after plan.py, export.py and fetch_roads.py; then run export.py again.
"""
import json, os
from datetime import date
from collections import defaultdict
from fetch_roads import osrm, simplify, log, HERE, ROOT

route = json.load(open(os.path.join(ROOT, "data", "route.json"), encoding="utf-8"))
trip = json.load(open(os.path.join(ROOT, "data", "trip.json"), encoding="utf-8"))
plan = json.load(open(os.path.join(HERE, "cache", "plan.json"), encoding="utf-8"))
bases = json.load(open(os.path.join(ROOT, "data", "bases.json"), encoding="utf-8"))["bases"]
START = date.fromisoformat(trip["start_date"])
def day(s): return (date.fromisoformat(s) - START).days

by_title = {p["title"]: p for p in trip["points"] if p["kind"] == "highlight"}
stops = [p for p in trip["points"] if p["kind"] == "stop"]
pre_ferry = {h["title"]: h["pre_ferry"] for seg in plan for h in seg["highlights"]}
ferries = {f["name"]: f for f in route["ferries"].values()}

def point_id(title, on):
    """The trip point for a title: a highlight, or the main stop of that name nearest in time."""
    if title in by_title: return by_title[title]["id"]
    same = [s for s in stops if s["name"] == title]
    return min(same, key=lambda s: abs(s["day"] - day(on)))["id"] if same else None

legs, unroutable = [], []
def road(a, b, d, base):
    """Road from waypoint a to b, each (id, [lon, lat])."""
    r = osrm(a[1], b[1]) if a[1] != b[1] else dict(geom=[a[1], b[1]], m=0, s=0)
    if r is None: unroutable.append((a[0], b[0])); r = dict(geom=[a[1], b[1]], m=None, s=None)
    legs.append({"mode": "road", "from": a[0], "to": b[0], "km": round(r["m"] / 1000, 1) if r["m"] is not None else None,
                 "min": round(r["s"] / 60) if r["s"] is not None else None, "day": d, "base": base, "geom": simplify(r["geom"])})

for prev, b in zip(bases, bases[1:]):
    here = (point_id(prev["center_place"], prev["arrive"]) or prev["id"], [prev["lon"], prev["lat"]])
    goal = (point_id(b["center_place"], b["arrive"]) or b["id"], [b["lon"], b["lat"]])
    way = [(point_id(o["title"], o["date"]), [o["lon"], o["lat"]], o["date"]) for o in b["on_the_way"]]
    left = day(prev["leave"])
    if b["ferry_in"]:
        f = ferries[b["ferry_in"]]
        pre = [w for w, o in zip(way, b["on_the_way"]) if pre_ferry.get(o["title"], True)]
        post = [w for w in way if w not in pre]
        cur = here
        for w in pre: road(cur, w[:2], day(w[2]), b["id"]); cur = w[:2]
        sail = max([left] + [day(w[2]) for w in pre])
        road(cur, (None, f["from"]), sail, b["id"])
        legs.append({"mode": "sea", "from": None, "to": None, "km": None, "min": None, "day": sail, "base": b["id"], "ferry": f["name"],
                     "geom": [[round(x, 4), round(y, 4)] for x, y in [f["from"], *f.get("via", []), f["to"]]]})
        cur = (None, f["to"])
        for w in post: road(cur, w[:2], day(w[2]), b["id"]); cur = w[:2]
    else:
        cur = here
        for w in way: road(cur, w[:2], day(w[2]), b["id"]); cur = w[:2]
    road(cur, goal, day(b["arrive"]), b["id"])
    log(prev["name"], ">", b["name"], f"{sum(l['km'] or 0 for l in legs if l['base'] == b['id']):,.0f} km")

json.dump(legs, open(os.path.join(HERE, "cache", "base_legs.json"), "w", encoding="utf-8", newline="\n"), separators=(",", ":"))
per_day = defaultdict(float)
for l in legs:
    if l["mode"] == "road": per_day[l["day"]] += l["km"] or 0
km = sum(per_day.values())
log(f"DONE. {len(legs)} legs, {km:,.0f} km by road ({km / 1.609344:,.0f} miles), {len([d for d, k in per_day.items() if k > 0])} days with driving;"
    f" no road found for: {unroutable}")
