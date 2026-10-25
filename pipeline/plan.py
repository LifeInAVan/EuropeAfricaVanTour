#!/usr/bin/env python3
"""Build plan.json: per stop-to-stop segment, the road/sea parts (lon/lat geometry routed
through every highlight) and the dated highlights. Needs hl_info.json from verify_hl.py."""
import json, math, os, urllib.request, urllib.error, time, hashlib
from datetime import date, timedelta
from highlights_src import H

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
route = json.load(open(os.path.join(ROOT, "data", "route.json"), encoding="utf-8"))
stops = route["stops"]; FERRIES = route.get("ferries", {})
info = json.load(open(os.path.join(HERE, "cache", "hl_info.json"), encoding="utf-8"))
cache_path = os.path.join(HERE, "cache", "road_cache.json")
cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}

def osrm(coords):
    """Road geometry through coords; if a waypoint is unroutable, drop it and retry."""
    try:
        return _osrm(coords)
    except RuntimeError:
        out, last = [], coords[0]
        for c in coords[1:]:
            try:
                g = _osrm([last, c]); out += g if not out else g[1:]; last = c
            except RuntimeError:
                print("  skipped unroutable waypoint", c, flush=True)
        return out

def _osrm(coords):
    out = []
    for s in range(0, len(coords) - 1, 24):
        chunk = coords[s:s + 25]
        key = "wp:" + hashlib.md5(json.dumps(chunk).encode()).hexdigest()
        if key not in cache:
            url = ("https://router.project-osrm.org/route/v1/driving/" +
                   ";".join(f"{x},{y}" for x, y in chunk) + "?overview=simplified&geometries=geojson&continue_straight=false")
            for k in range(6):
                try:
                    with urllib.request.urlopen(url, timeout=60) as r:
                        cache[key] = [(round(x, 3), round(y, 3)) for x, y in json.load(r)["routes"][0]["geometry"]["coordinates"]]
                    break
                except urllib.error.HTTPError as e:
                    err = e
                    if e.code == 400: break          # unroutable: no retry
                    time.sleep(3 * (k + 1))
                except Exception as e:
                    time.sleep(3 * (k + 1)); err = e
            if key not in cache:
                raise RuntimeError(f"OSRM failed: {err}")
            json.dump(cache, open(cache_path, "w", encoding="utf-8", newline="\n"), separators=(",", ":"))
            time.sleep(0.5)
        out += cache[key] if not out else cache[key][1:]
    return out

def spread(items, start, end):
    """Assign one date per item across [start, end) days, in order."""
    k = (end - start).days
    n = len(items)
    if n == 0: return []
    if k <= 0: return [start] * n
    return [start + timedelta(days=int(j * k / n)) for j in range(n)]

plan = []; dropped = []
for i in range(len(stops) - 1):
    a, b = stops[i], stops[i + 1]
    key = f"{a['id']}>{b['id']}"
    raw = H.get(key, [])
    d0, d1 = date.fromisoformat(a["date"]), date.fromisoformat(b["date"])
    # split into date groups and ferry groups
    groups, cur, marker = [], [], None
    part_idx = 0; hls = []
    for e in raw:
        if e == "~FERRY~":
            part_idx = 1; continue
        if isinstance(e, tuple) and e[0] == "~DATE~":
            groups.append((cur, marker)); cur = []; marker = date.fromisoformat(e[1]); continue
        t, cap, typ = e
        inf = info.get(t, {})
        if inf.get("missing") or not inf.get("coords"):
            dropped.append(t); continue
        cur.append({"title": t, "name": inf["resolved"], "caption": cap, "type": typ,
                    "lon": inf["coords"][0], "lat": inf["coords"][1], "pre_ferry": part_idx == 0})
    groups.append((cur, marker))
    # dates: group 0 spans (d0+1 .. first marker or d1); later groups span (marker .. next marker or d1)
    starts = [d0 + timedelta(days=1)] + [m for _, m in groups[1:]]
    for gi, (items, _) in enumerate(groups):
        end = starts[gi + 1] if gi + 1 < len(starts) else d1
        for it, dt in zip(items, spread(items, starts[gi], end)):
            it["date"] = dt.isoformat(); hls.append(it)
    A, B = (a["lon"], a["lat"]), (b["lon"], b["lat"])
    fr = FERRIES.get(key)
    parts = []
    def road(p, q, via):
        pts = [p] + [(h["lon"], h["lat"]) for h in via] + [q]
        if len(pts) == 2 and math.dist(p, q) < 0.05: return None
        return {"mode": "road", "geom": [p] + osrm(pts) + [q], "hl": [h["title"] for h in via]}
    if fr:
        pre = [h for h in hls if h["pre_ferry"]]; post = [h for h in hls if not h["pre_ferry"]]
        p1 = road(A, tuple(fr["from"]), pre)
        sea = {"mode": "sea", "name": fr["name"], "hl": [],
               "geom": [tuple(fr["from"])] + [tuple(v) for v in fr.get("via", [])] + [tuple(fr["to"])]}
        p2 = road(tuple(fr["to"]), B, post)
        parts = [p for p in (p1, sea, p2) if p]
    else:
        parts = [road(A, B, hls)]
    plan.append({"from": a["id"], "to": b["id"], "parts": parts, "highlights": hls})
    print(f"{key}: {len(hls)} highlights over {(d1-d0).days-1} days", flush=True)

json.dump(plan, open(os.path.join(HERE, "cache", "plan.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False)
print("dropped (no coordinates):", dropped)
print("total highlights:", sum(len(p["highlights"]) for p in plan))
