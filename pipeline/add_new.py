#!/usr/bin/env python3
"""Coordinates (Nominatim) + photos (Openverse) for highlights not yet resolved/photographed."""
import json, os, io, time, hashlib, urllib.request, urllib.parse
from PIL import Image
from highlights_src import H
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
UA = {"User-Agent": "PersonalTripMontage/1.0 (family video project; https://github.com/LifeInAVan/EuropeAfricaVanTour)"}
info = json.load(open(os.path.join(HERE, "cache", "hl_info.json"), encoding="utf-8"))
cp = os.path.join(ROOT, "assets", "_hl", "credits.json"); cred = json.load(open(cp, encoding="utf-8"))
def log(*a): print(*a, flush=True)
def get(u, raw=False):
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
                return r.read() if raw else json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(65); continue
            raise
    raise RuntimeError("rate limited")
path = lambda t: os.path.join(ROOT, "assets", "_hl", hashlib.md5(t.encode()).hexdigest()[:12] + ".jpg")
titles = [e[0] for v in H.values() for e in v if isinstance(e, tuple) and e[0] != "~DATE~"]

GEO = {"Łazienki Park": "Łazienki Królewskie", "Pomeranian Dukes' Castle": "Zamek Książąt Pomorskich",
 "Oliwa Cathedral": "Archikatedra Oliwska", "Lidzbark Warmiński Castle": "Zamek w Lidzbarku Warmińskim",
 "Krutynia": "Krutyń", "Maison Carrée": "Maison Carrée, Nîmes", "Cours Mirabeau": "Cours Mirabeau, Aix-en-Provence",
 "Plateau de Valensole": "Valensole", "Roman Theatre of Orange": "Théâtre antique d'Orange",
 "Bastille (Grenoble)": "Fort de la Bastille, Grenoble", "Grande Chartreuse": "Monastère de la Grande Chartreuse",
 "Palais de l'Isle": "Palais de l'Isle, Annecy", "Oeschinen Lake": "Oeschinensee", "Chapel Bridge": "Kapellbrücke",
 "Saarschleife": "Saarschleife, Mettlach", "Speyer Cathedral": "Dom zu Speyer", "Erfurt Cathedral": "Erfurter Dom",
 "St. Thomas Church, Leipzig": "Thomaskirche, Leipzig", "Zwinger": "Zwinger, Dresden",
 "All Saints' Church, Wittenberg": "Schlosskirche, Wittenberg", "Santa Claus Village": "Santa Claus Village, Rovaniemi",
 "Sodankylä Old Church": "Sodankylän vanha kirkko", "Sajos": "Sajos, Inari", "Tana (river)": "Tana bru",
 "Alta Canyon": "Sautso", "Segla": "Segla, Senja", "Bleik": "Bleik, Andøy", "Vågan Church": "Vågan kirke",
 "Haukland Beach": "Hauklandstranda", "Seven Sisters (mountains)": "De syv søstre, Alstahaug",
 "Petter Dass Museum": "Petter Dass-museet", "Flåm Line": "Flåm stasjon", "Vemork": "Vemork, Tinn",
 "Cave of Nerja": "Cueva de Nerja", "Albufera (Valencia)": "L'Albufera, València",
 "Alcázar of Seville": "Real Alcázar de Sevilla", "Besalú": "Besalú", "Tankavaara": "Tankavaara, Sodankylä"}
for t in titles:
    v = info.get(t, {})
    if v.get("coords") and not v.get("missing"): continue
    try:
        r = get("https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + urllib.parse.quote(GEO.get(t, t)))
        time.sleep(1.2)
        if r:
            info[t] = dict(v, resolved=v.get("resolved", t), missing=False, checked=True, coord_source="OpenStreetMap",
                           coords=(float(r[0]["lon"]), float(r[0]["lat"])), wikipedia_unchecked=t not in info or v.get("missing", False))
            log("coords ok", t)
        else: log("coords none", t)
    except Exception as e: log("coords fail", t, e)
json.dump(info, open(os.path.join(HERE, "cache", "hl_info.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

REJECTED = {"Tihany Abbey", "Fuente Dé", "Akka", "Stintino", "Siida", "Sanssouci", "Wartburg", "University of Coimbra"}
PQ = {"Bastille (Grenoble)": "Grenoble Bastille cable car", "Chapel Bridge": "Chapel Bridge Lucerne",
 "Zwinger": "Zwinger Dresden", "Segla": "Segla Senja", "Bleik": "Bleik beach Andøya", "Sajos": "Sajos Inari",
 "Tana (river)": "Tana river Finnmark", "Vemork": "Vemork Rjukan", "Flåm Line": "Flåm railway",
 "Seven Sisters (mountains)": "Seven Sisters mountains Alstahaug", "Hamnøy": "Hamnøy Lofoten",
 "Haukland Beach": "Haukland beach Lofoten", "Santa Claus Village": "Santa Claus Village Rovaniemi",
 "Alta Canyon": "Sautso canyon Alta", "Fjellheisen": "Fjellheisen Tromsø", "Munkholmen": "Munkholmen Trondheim",
 "Plateau de Valensole": "Valensole lavender", "Lac de Sainte-Croix": "Lac de Sainte-Croix Verdon",
 "Krutynia": "Krutynia river kayak", "Trzęsacz": "Trzęsacz church ruin", "Sopot": "Sopot pier",
 "Cave of Nerja": "Cueva de Nerja", "Albufera (Valencia)": "Albufera Valencia lagoon", "Mojácar": "Mojacar village",
 "Guadix": "Guadix cave houses", "Morella, Castellón": "Morella Castellon", "Besalú": "Besalu bridge",
 "Cap de Creus": "Cap de Creus lighthouse", "Cádiz": "Cadiz cathedral", "Baelo Claudia": "Baelo Claudia Bolonia",
 "Doñana National Park": "Doñana marshes", "Setenil de las Bodegas": "Setenil de las Bodegas",
 "Girona Cathedral": "Girona cathedral", "Sitges": "Sitges beach", "Guadalest": "Guadalest",
 "Roman Theatre of Cartagena": "Cartagena roman theatre", "Alcázar of Seville": "Alcazar Seville",
 "Mosque–Cathedral of Córdoba": "Mezquita Cordoba", "Caminito del Rey": "Caminito del Rey"}
PREF = ["cc0", "pdm", "by", "by-sa", "by-nc", "by-nc-sa"]
calls = 0; new_photos = []
for t in titles:
    if os.path.exists(path(t)) or t in REJECTED or not info.get(t, {}).get("coords"): continue
    if calls >= 150: log("openverse budget"); break
    q = PQ.get(t, t.split(" (")[0])
    try:
        r = get("https://api.openverse.org/v1/images/?page_size=20&mature=false&license=" + ",".join(PREF) + "&q=" + urllib.parse.quote(q))
        calls += 1; time.sleep(3.3)
    except Exception as e: log("ov fail", t, e); continue
    res = [x for x in r.get("results", []) if x.get("url") and "wikimedia" not in x["url"] and (x.get("width") or 1) >= (x.get("height") or 0)]
    for x in res[:4]:
        try:
            data = get(x["url"], raw=True)
            im = Image.open(io.BytesIO(data)).convert("RGB"); im.thumbnail((1600, 1600)); im.save(path(t), quality=88)
            l = x["license"]
            cred[t] = {"artist": (x.get("creator") or "unknown")[:50],
                       "license": "CC0" if l == "cc0" else "Public domain" if l == "pdm" else f"CC {l.upper()} {x.get('license_version') or ''}".strip(),
                       "source": "Openverse", "url": x.get("foreign_landing_url")}
            json.dump(cred, open(cp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
            new_photos.append(t); log("photo ok", t); break
        except Exception: continue
    else: log("photo none", t)
json.dump(new_photos, open(os.path.join(HERE, "cache", "new_photos.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False)
log("new photos:", len(new_photos)); log("DONE")
