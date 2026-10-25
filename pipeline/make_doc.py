#!/usr/bin/env python3
"""Day-by-day highlights table (markdown) from plan.json + route.json."""
import json, os, urllib.parse
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
route = json.load(open(os.path.join(ROOT, "data", "route.json"), encoding="utf-8"))
plan = json.load(open(os.path.join(HERE, "cache", "plan.json"), encoding="utf-8"))
stops = {s["id"]: s for s in route["stops"]}
legname = {l["id"]: l["name"] for l in route["legs"]}
TYPE = {"B": "Beach", "N": "Nature", "C": "Culture", "H": "History", "P": "Peaceful"}
info = json.load(open(os.path.join(HERE, "cache", "hl_info.json"), encoding="utf-8"))
NOPAGE = {"Kravica Waterfall","Combarro","Piódão","Costa Nova do Prado","Benagil Cave","Legzira","Portuguese City of Mazagan",
          "Amphitheatre of Tarragona","Château de Grignan","Haut-Kœnigsbourg Castle","Reichsburg Cochem","Moritzburg Castle (Saxony)","Āraiši Lake Fortress","Fuente Dé","Combarro"}
def wp(t):
    if t in NOPAGE or info.get(t, {}).get("wikipedia_unchecked"):
        lon, lat = info[t]["coords"]
        return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=14/{lat}/{lon}"
    return "https://en.wikipedia.org/wiki/" + urllib.parse.quote(t.replace(" ", "_"))
def d(s): return date.fromisoformat(s).strftime("%a %d %b %Y")

out = ["# Day-by-day highlights", "",
       "At least one highlight per touring day (two on most days in France, Germany, Poland and the Arctic), in driving order. **Bold rows** are the main stops (overnight bases). "
       "Each place links to its source: the Wikipedia article (description and location) or, where there is no article, "
       "its OpenStreetMap location. The route is drawn through these coordinates.", "",
       "Not daily: Morocco winter base (3 Jan–7 Feb 2028, excursions roughly weekly, rest days at the coast; Toubkal 9–12 Feb) and home time in Pärnu (25 Jun–11 Jul 2028, Laulupidu 30 Jun–9 Jul).", ""]
counts = {}
cur_leg = None
for seg in plan:
    a = stops[seg["from"]]
    if a["leg"] != cur_leg:
        cur_leg = a["leg"]
        out += ["", f"## {legname[cur_leg]}", "", "| Date | Place | Type | Why go |", "|---|---|---|---|"]
    out.append(f"| **{d(a['date'])}** | **{a['name']}** | Main stop | {a['caption']} |")
    for h in seg["highlights"]:
        counts[h["type"]] = counts.get(h["type"], 0) + 1
        out.append(f"| {d(h['date'])} | [{h['title'].split(' (')[0].replace(', Portugal','').replace(', Morocco','').replace(', Vaucluse','')}]({wp(h['title']) if (h['title'] in NOPAGE or info.get(h['title'],{}).get('wikipedia_unchecked')) else wp(h['name'])}) | {TYPE[h['type']]} | {h['caption']} |")
last = stops[plan[-1]["to"]]
out.append(f"| **{d(last['date'])}** | **{last['name']}** | Main stop | {last['caption']} |")
n = sum(counts.values())
out[5:5] = ["", f"**{n} highlights** — " + ", ".join(f"{TYPE[k]} {v}" for k, v in sorted(counts.items(), key=lambda x: -x[1])), ""]
open(os.path.join(ROOT, "docs", "daily-highlights.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("written daily-highlights.md:", n, "highlights")
