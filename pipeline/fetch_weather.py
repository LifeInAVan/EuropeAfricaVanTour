#!/usr/bin/env python3
"""Typical weather for every point in data/trip.json, by day of the year -> data/weather.json.

Source: NASA POWER daily data (MERRA-2, about 50 km grid), 2011-2025, free and without a key.
Each point's temperatures are corrected for the difference between its own height (Open-Meteo
elevation) and the average height of its grid cell, at 6.5 °C per 1000 m.
For each calendar day the values are averaged over a 15-day window across the 15 years:
typical daytime high and night low (°C) and rain days in 10 (days with at least 1 mm).
Raw downloads are kept in cache/weather/ (not committed); the script resumes where it stopped.
"""
import json, os, time, urllib.request, urllib.parse
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
RAW = os.path.join(HERE, "cache", "weather"); os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "PersonalTripMontage/1.0 (family trip website; https://github.com/LifeInAVan/EuropeAfricaVanTour)"}
YEARS, HALF, LAPSE, RAIN_MM = (2011, 2025), 7, 6.5 / 1000, 1.0

trip = json.load(open(os.path.join(ROOT, "data", "trip.json"), encoding="utf-8"))
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)
def get(url):
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r: return json.load(r)
        except Exception as e:
            log("retry", k + 1, e); time.sleep(20 * (k + 1))
    raise RuntimeError("gave up on " + url)

# ---- 1. heights of the points (Open-Meteo elevation, 100 per request) ----
ep = os.path.join(RAW, "_elevation.json")
elev = json.load(open(ep, encoding="utf-8")) if os.path.exists(ep) else {}
todo = [p for p in trip["points"] if p["id"] not in elev]
for i in range(0, len(todo), 100):
    batch = todo[i:i + 100]
    r = get("https://api.open-meteo.com/v1/elevation?" + urllib.parse.urlencode(dict(
        latitude=",".join(str(p["lat"]) for p in batch), longitude=",".join(str(p["lon"]) for p in batch))))
    elev.update({p["id"]: e for p, e in zip(batch, r["elevation"])})
    json.dump(elev, open(ep, "w", encoding="utf-8", newline="\n")); time.sleep(1)

# ---- 2. daily history per point (NASA POWER) ----
for n, p in enumerate(trip["points"], 1):
    f = os.path.join(RAW, p["id"] + ".json")
    if os.path.exists(f): continue
    r = get("https://power.larc.nasa.gov/api/temporal/daily/point?" + urllib.parse.urlencode(dict(
        parameters="T2M_MAX,T2M_MIN,PRECTOTCORR", community="RE", longitude=p["lon"], latitude=p["lat"],
        start=f"{YEARS[0]}0101", end=f"{YEARS[1]}1231", format="JSON")))
    v = r["properties"]["parameter"]
    json.dump(dict(grid_elev=r["geometry"]["coordinates"][2], hi=v["T2M_MAX"], lo=v["T2M_MIN"], rain=v["PRECTOTCORR"]),
              open(f, "w", encoding="utf-8", newline="\n"))
    log(f"{n}/{len(trip['points'])}", p["id"]); time.sleep(1)

# ---- 3. typical values for each calendar day (366, as in a leap year) ----
import numpy as np
FIRST = date(YEARS[0], 1, 1)
DATES = [(FIRST + timedelta(i)).strftime("%Y%m%d") for i in range((date(YEARS[1], 12, 31) - FIRST).days + 1)]
WINDOWS = []                                                            # day positions averaged for each calendar day
for d in (date(2028, 1, 1) + timedelta(k) for k in range(366)):
    idx = []
    for y in range(YEARS[0], YEARS[1] + 1):
        try: centre = date(y, d.month, d.day)
        except ValueError: centre = date(y, 2, 28)                      # 29 Feb in a non-leap year
        idx += [i for i in ((centre - FIRST).days + k for k in range(-HALF, HALF + 1)) if 0 <= i < len(DATES)]
    WINDOWS.append(np.array(idx))

def series(s):                                                          # missing days (-999) become NaN
    a = np.array([s.get(k, np.nan) for k in DATES], dtype=float)
    return np.where(a <= -900, np.nan, a)
out = {}
for p in trip["points"]:
    raw = json.load(open(os.path.join(RAW, p["id"] + ".json"), encoding="utf-8"))
    corr = (raw["grid_elev"] - elev[p["id"]]) * LAPSE
    hi, lo, rain = series(raw["hi"]), series(raw["lo"]), series(raw["rain"])
    out[p["id"]] = dict(elev=round(elev[p["id"]]), grid_elev=round(raw["grid_elev"]),
                        hi=[round(float(np.nanmean(hi[w])) + corr) for w in WINDOWS],
                        lo=[round(float(np.nanmean(lo[w])) + corr) for w in WINDOWS],
                        rain=[round(10 * float(np.nanmean(rain[w] >= RAIN_MM))) for w in WINDOWS])
doc = dict(source="NASA POWER daily (MERRA-2), corrected for height; elevations from Open-Meteo",
           years=f"{YEARS[0]}-{YEARS[1]}",
           note="Typical weather, not a forecast. Index 0 = 1 January, 59 = 29 February, 365 = 31 December. "
                "hi/lo: typical daytime high and night low in °C; rain: days in 10 with at least 1 mm.",
           points=out)
json.dump(doc, open(os.path.join(ROOT, "data", "weather.json"), "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, separators=(",", ":"))
log("written data/weather.json:", len(out), "points")
