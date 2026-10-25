#!/usr/bin/env python3
"""Slideshow candidates for every point in data/trip.json, with small previews for the review page.

Sources, in order: the film's feature photo and the Wikidata image of the place's Wikipedia article;
the place's Commons category; Commons photos taken near the point; Openverse only if those find too few.
Keeps JPEGs at least 1200 px wide under licences that allow changes (no ND, no GFDL-only), skips maps,
drawings, logos and old scans, and ranks the rest (featured/quality images, size, wide format).

Writes cache/slides/candidates.json and cache/slides/prev/<point>/<n>.jpg (330 px). Resumes where it stopped.
python pipeline/fetch_slides.py              all points
python pipeline/fetch_slides.py --chapter 1  one chapter
"""
import json, os, re, sys, time, math, urllib.request, urllib.parse, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
OUT = os.path.join(HERE, "cache", "slides"); os.makedirs(OUT, exist_ok=True)
CAND = os.path.join(OUT, "candidates.json")
UA = {"User-Agent": "PersonalTripMontage/1.0 (family trip website; https://github.com/LifeInAVan/EuropeAfricaVanTour)"}
COMMONS = "https://commons.wikimedia.org/w/api.php?"
KEEP, MIN_W, PREV_W = 10, 1200, 330
SKIP = re.compile(r"\b(map|karte|mapa|carte|plan|plano|diagram|logo|coat.of.arms|wappen|herb|escudo|flag|stamp|"
                  r"sign|signboard|ticket|drawing|engraving|painting|lithograph|postcard|scan|book|page|poster|"
                  r"aerial.view.\d{4}|19[0-7]\d|18\d\d|squirrel|sparrow|pigeons?|ducks?|insect|butterfly|"
                  r"food|dish|menu|tram|bus|cars?|vehicle|portrait|conference|meeting|speech|protest|"
                  r"demonstration|press|politician|minister|president|medal|coin|award|concert|performance|"
                  r"actor|actress|singer|mineral|crystal|specimen|museum.exhibit|fish|snake|lizard|frog|toad|"
                  r"birds?|mushroom|fungus|beetle|spider|moth|caterpillar|dragonfly|perch|natrix)\b", re.I)
QUALITY = {"Featured pictures on Wikimedia Commons": 5, "Quality images": 3, "Valued images sorted by promotion date": 2}

trip = json.load(open(os.path.join(ROOT, "data", "trip.json"), encoding="utf-8"))
info = json.load(open(os.path.join(HERE, "cache", "hl_info.json"), encoding="utf-8"))
cands = json.load(open(CAND, encoding="utf-8")) if os.path.exists(CAND) else {}
def save(): json.dump(cands, open(CAND, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)

def http(url, raw=False):
    for k in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read(); return data if raw else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503): time.sleep(30 * (k + 1)); continue
            raise
        except (urllib.error.URLError, TimeoutError): time.sleep(10 * (k + 1))
    raise RuntimeError("gave up on " + url)

def api(base, **p):
    """Read-only queries, one at a time with a pause; errors other than 'busy' are raised."""
    p.update(format="json", formatversion=2)
    for k in range(6):
        time.sleep(0.5); r = http(base + urllib.parse.urlencode(p))
        err = r.get("error", {}).get("code")
        if not err: return r
        if err not in ("maxlag", "ratelimited", "internal_api_error_DBQueryTimeoutError"): raise RuntimeError(err)
        time.sleep(10 * (k + 1))
    raise RuntimeError("servers busy")

def text(html): return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()

def files_info(**gen):
    """Commons files (from a generator or titles) with size, licence, author and quality categories."""
    r = api(COMMONS, action="query", prop="imageinfo|categories|coordinates", iiprop="url|size|mime|extmetadata",
            coprimary="all", colimit="max",
            iiurlwidth=PREV_W, iiextmetadatafilter="Artist|LicenseShortName|LicenseUrl|DateTimeOriginal|ImageDescription",
            clcategories="|".join("Category:" + c for c in QUALITY), cllimit="max", **gen)
    out = []
    for p in sorted(r.get("query", {}).get("pages", []), key=lambda p: p.get("index", 0)):   # back into rank order
        ii = (p.get("imageinfo") or [None])[0]
        if not ii: continue
        md = {k: v.get("value") for k, v in ii.get("extmetadata", {}).items()}
        out.append(dict(file=p["title"][5:], w=ii["width"], h=ii["height"], mime=ii["mime"], page=ii["descriptionurl"],
                        prev=ii.get("thumburl"), license=md.get("LicenseShortName", ""), license_url=md.get("LicenseUrl"),
                        artist=text(md.get("Artist"))[:80] or "unknown",
                        desc=text(md.get("ImageDescription"))[:160],
                        at=[(c["lat"], c["lon"]) for c in p.get("coordinates", [])],
                        quality=sum(QUALITY.get(c["title"][9:], 0) for c in p.get("categories", []))))
    return out

def allowed(lic):
    l = lic.upper()
    if not l or "ND" in l.split() or "NC" in l or "FAIR" in l: return False
    return l.startswith(("CC", "PUBLIC DOMAIN", "PD")) or "FAL" in l or l == "ATTRIBUTION"

def usable(c):
    return (c["mime"] == "image/jpeg" and c["w"] >= MIN_W and allowed(c["license"])
            and not SKIP.search(c["file"].replace("_", " ")) and not SKIP.search(c["desc"]))

def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))

def near(c, p):
    """Photos with a recorded location must be taken near the point (parks and mountains are bigger)."""
    limit = 30 if p.get("type") == "nature" or p["kind"] == "stop" else 12
    return not c.get("at") or min(km(a, (p["lat"], p["lon"])) for a in c["at"]) <= limit

def score(c):
    wide = c["w"] / c["h"]
    return round(c["quality"] + math.log2(c["w"] / MIN_W) + (2 if 1.2 <= wide <= 2.2 else 0 if wide >= 1 else -2)
                 + c.get("bonus", 0), 2)

def wikidata(title):
    """Commons category and main image of a Wikipedia article, via Wikidata."""
    r = api("https://en.wikipedia.org/w/api.php?", action="query", prop="pageprops", ppprop="wikibase_item",
            redirects=1, titles=title)
    pages = r.get("query", {}).get("pages", [])
    qid = pages and pages[0].get("pageprops", {}).get("wikibase_item")
    if not qid: return None, None
    e = api("https://www.wikidata.org/w/api.php?", action="wbgetentities", ids=qid, props="claims|sitelinks",
            sitefilter="commonswiki").get("entities", {}).get(qid, {})
    claims = e.get("claims", {})
    val = lambda p: (claims.get(p) or [{}])[0].get("mainsnak", {}).get("datavalue", {}).get("value")
    link = e.get("sitelinks", {}).get("commonswiki", {}).get("title", "")
    return val("P373") or (link[9:] if link.startswith("Category:") else None), val("P18")

def openverse(q):
    r = http("https://api.openverse.org/v1/images/?page_size=20&mature=false&license=cc0,pdm,by,by-sa,by-nc,by-nc-sa&q="
             + urllib.parse.quote(q)); time.sleep(3.5)
    out = []
    for x in r.get("results", []):
        if x.get("source") == "wikimedia" or (x.get("width") or 0) < MIN_W: continue
        l, v = x["license"], x.get("license_version") or ""
        out.append(dict(file="ov:" + x["id"], w=x["width"], h=x["height"] or 1, mime="image/jpeg",
                        page=x.get("foreign_landing_url"), prev=x.get("thumbnail"), full=x.get("url"),
                        license="CC0" if l == "cc0" else "Public domain" if l == "pdm" else f"CC {l.upper()} {v}".strip(),
                        license_url=x.get("license_url"), artist=(x.get("creator") or "unknown")[:80], desc=x.get("title") or "",
                        quality=0, source="Openverse"))
    return out

ov_calls = 0
def candidates(p):
    global ov_calls
    found, seen = [], set()
    def take(lst, source, bonus=0):
        for rank, c in enumerate(lst):                          # search results come best match first
            if c["file"] in seen or not usable(c) or not near(c, p): continue
            seen.add(c["file"]); c.setdefault("source", source); c["bonus"] = bonus - rank / 25; found.append(c)
    film = info.get(p.get("title", ""), {}).get("file")
    article = p.get("wikipedia") or p.get("title") or p["name"]     # unchecked names are tried too; photos are reviewed
    cat, p18 = wikidata(article) if article else (None, None)
    first = [f for f in (film, p18) if f]
    if first: take(files_info(titles="|".join("File:" + f for f in first)), "Wikipedia", bonus=3)
    name = re.sub(r"\s*\(.*\)", "", article).replace(",", " ")      # rated photos that name the place
    take(files_info(generator="search", gsrsearch=f'{name} incategory:"Quality_images" filetype:bitmap',
                    gsrnamespace=6, gsrlimit=50), "Commons quality")
    if cat:                                                     # the category and its subcategories
        for q in (f'incategory:"{cat}" filetype:bitmap', f'deepcat:"{cat}" filetype:bitmap'):
            n = len(found)                                      # the place's own category first
            try: take(files_info(generator="search", gsrsearch=q, gsrnamespace=6, gsrlimit=100), "Commons category")
            except Exception as e: log("search failed", q, e)
            if len(found) - n >= 5: break
    if len(found) < KEEP:
        radius = 3000 if p["kind"] == "stop" else 1000
        take(files_info(generator="geosearch", ggscoord=f"{p['lat']}|{p['lon']}", ggsradius=radius,
                        ggsnamespace=6, ggslimit=100), "Commons nearby", bonus=-1)
    if len(found) < 3 and ov_calls < 190:
        ov_calls += 1; take(openverse(p.get("title", p["name"]).split(" (")[0]), "Openverse", bonus=-1)
    for c in found: c["score"] = score(c); c.pop("bonus", None); c.pop("mime", None); c.pop("at", None)
    found.sort(key=lambda c: -c["score"])
    return dict(category=cat, film_file=film, items=found[:KEEP])

def previews(pid, items):
    d = os.path.join(OUT, "prev", pid); os.makedirs(d, exist_ok=True)
    for i, c in enumerate(items):
        f = os.path.join(d, f"{i}.jpg")
        if os.path.exists(f) or not c.get("prev"): continue
        try: open(f, "wb").write(http(c["prev"], raw=True)); time.sleep(0.3)
        except Exception as e: log("preview failed", pid, i, e)

if __name__ == "__main__":
    ch = int(sys.argv[sys.argv.index("--chapter") + 1]) if "--chapter" in sys.argv else None
    todo = [p for p in trip["points"] if ch in (None, p["chapter"])]
    for n, p in enumerate(todo, 1):
        if p["id"] not in cands:
            try: cands[p["id"]] = candidates(p); save()
            except Exception as e: log("FAILED", p["id"], e); continue
        previews(p["id"], cands[p["id"]]["items"])
        log(f"{n}/{len(todo)}", p["id"], len(cands[p["id"]]["items"]), "candidates")
    short = [p["id"] for p in todo if len(cands.get(p["id"], {}).get("items", [])) < 3]
    log("DONE.", len(todo), "points;", "fewer than 3 candidates:", len(short), short)
