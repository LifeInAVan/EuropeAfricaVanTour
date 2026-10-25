#!/usr/bin/env python3
"""Pärnu→Sahara montage renderer v3 (1080p default).
- road-atlas basemap (Natural Earth roads)
- route follows real roads (OSRM, cached in road_cache.json); ferries dashed
- the real van photo drives, pointing along the road
- sight postcard (Wikimedia) at each stop, credited
- personal photos drift across the top while travelling
Usage: python3 render2.py out.mp4 [WxH]
"""
import json, math, os, subprocess, sys, glob, random, urllib.request
from datetime import date
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "montage.mp4")
VW, VH = (1920, 1080) if len(sys.argv) < 3 else map(int, sys.argv[2].split("x"))
S = VH / 720.0
FPS = 24
MW = int(VW * 1.7)
LON0, LON1, LAT0, LAT1 = -13.0, 33.0, 26.5, 72.5
KX = math.cos(math.radians((LAT0 + LAT1) / 2))
MH = int(MW * (LAT1 - LAT0) / ((LON1 - LON0) * KX))
TRAVEL_SECONDS = 50          # total time spent driving/sailing
PAUSE = 34                   # frames per main stop
SEA = (214, 228, 232); LAND = (243, 240, 230); COAST = (170, 175, 160)
BORDER = (205, 198, 180); ROAD = (226, 196, 150); INK = (33, 45, 39); PAPER = (250, 249, 243)
random.seed(4)

F = "/usr/share/fonts/truetype/dejavu/"
def font(sz, bold=False):
    return ImageFont.truetype(F + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), max(8, int(sz * S)))

def pt(lon, lat):
    return ((lon - LON0) / (LON1 - LON0) * MW, (LAT1 - lat) / (LAT1 - LAT0) * MH)
def hexc(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

route = json.load(open(os.path.join(ROOT, "data", "route.json"), encoding="utf-8"))
legc = {l["id"]: hexc(l["color"]) for l in route["legs"]}
legname = {l["id"]: l["name"] for l in route["legs"]}
stops = route["stops"]
D = [date.fromisoformat(s["date"]) for s in stops]

# ---------- basemap: land, borders, roads ----------
base = Image.new("RGB", (MW, MH), SEA)
bd = ImageDraw.Draw(base)
for f in json.load(open(os.path.join(HERE, "cache", "basemap.json"), encoding="utf-8"))["features"]:
    for poly in f["geometry"]["coordinates"]:
        for i, ring in enumerate(poly):
            bd.polygon([pt(x, y) for x, y in ring], fill=LAND if i == 0 else SEA)
for f in json.load(open(os.path.join(HERE, "cache", "basemap.json"), encoding="utf-8"))["features"]:
    for poly in f["geometry"]["coordinates"]:
        bd.line([pt(x, y) for x, y in poly[0]], fill=BORDER, width=max(1, int(1.2 * S)))
for ln in json.load(open(os.path.join(HERE, "cache", "roads.json"), encoding="utf-8")):
    bd.line([pt(x, y) for x, y in ln], fill=ROAD, width=max(1, int(1.3 * S)))

# ---------- road geometry ----------
cache_path = os.path.join(HERE, "cache", "road_cache.json")
cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
def road(a, b, key=None):
    """a, b: (lon, lat). Road-following geometry from OSRM, cached."""
    k = key or f"{a[0]:.3f},{a[1]:.3f}>{b[0]:.3f},{b[1]:.3f}"
    if k not in cache:
        url = (f"https://router.project-osrm.org/route/v1/driving/{a[0]},{a[1]};"
               f"{b[0]},{b[1]}?overview=simplified&geometries=geojson")
        with urllib.request.urlopen(url, timeout=30) as r:
            cache[k] = [(round(x, 3), round(y, 3)) for x, y in json.load(r)["routes"][0]["geometry"]["coordinates"]]
        json.dump(cache, open(cache_path, "w", encoding="utf-8", newline="\n"), separators=(",", ":"))
    return cache[k]
FERRIES = route.get("ferries", {})

def resample(pts, step):
    """Return points spaced `step` px apart along a pixel polyline."""
    out = [pts[0]]; carry = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.dist((x0, y0), (x1, y1))
        if seg == 0: continue
        dpos = step - carry
        while dpos <= seg:
            t = dpos / seg; out.append((x0 + (x1-x0)*t, y0 + (y1-y0)*t)); dpos += step
        carry = seg - (dpos - step)
    out.append(pts[-1]); return out

def road_part(a, b, key=None):
    if math.dist(a, b) < 0.05: return None
    return {"mode": "road", "pix": [pt(*a)] + [pt(x, y) for x, y in road(a, b, key)] + [pt(*b)]}

PLAN = json.load(open(os.path.join(HERE, "cache", "plan.json"), encoding="utf-8"))
HL_FRAMES = 17               # frames held at each daily highlight
segs = []
for i, pl in enumerate(PLAN):
    hlmap = {h["title"]: h for h in pl["highlights"]}
    parts = []
    for p in pl["parts"]:
        q = {"mode": p["mode"], "name": p.get("name", ""), "pix": [pt(x, y) for x, y in p["geom"]],
             "hl": [hlmap[t] for t in p["hl"] if t in hlmap]}
        q["len"] = sum(math.dist(u, v) for u, v in zip(q["pix"], q["pix"][1:]))
        parts.append(q)
    segs.append({"i": i, "parts": parts})
total_len = sum(p["len"] for s in segs for p in s["parts"])
STEP = total_len / (TRAVEL_SECONDS * FPS)
for s in segs:
    for p in s["parts"]:
        p["path"] = resample(p["pix"], STEP * (0.6 if p["mode"] == "sea" else 1.0))  # ferries a touch slower
        # where along the path each highlight is passed (forward search keeps them in order)
        ev, lo = {}, 0
        for h in p["hl"]:
            hx, hy = pt(h["lon"], h["lat"])
            best = min(range(lo, len(p["path"])), key=lambda k: (p["path"][k][0]-hx)**2 + (p["path"][k][1]-hy)**2)
            best = max(best, lo + 1) if best < len(p["path"]) - 1 else len(p["path"]) - 2
            ev.setdefault(best, []).append(h); lo = best
        p["events"] = ev
P = [pt(s["lon"], s["lat"]) for s in stops]
if os.environ.get("TEST"): segs = segs[:int(os.environ["TEST"])]

# ---------- assets ----------
def load(p):
    return ImageOps.exif_transpose(Image.open(p)).convert("RGB")

VAN_SRC = Image.open(os.path.join(ROOT, "assets", "_van_profile.png")).convert("RGBA")  # faces left
vw = int(105 * S); VAN_L = VAN_SRC.resize((vw, int(vw * VAN_SRC.height / VAN_SRC.width)), Image.LANCZOS)
VAN_R = VAN_L.transpose(Image.FLIP_LEFT_RIGHT)

def van_frame(dx, dy, bob=0.0):
    """Van pointing along (dx,dy); tilt clamped so it never drives upside down."""
    right = dx >= 0
    ang = math.degrees(math.atan2(-dy, abs(dx) + 1e-6))  # +ve = climbing (north)
    ang = max(-18, min(18, ang)) + bob
    img = VAN_R if right else VAN_L
    return img.rotate(ang if right else -ang, expand=True, resample=Image.BICUBIC)

def ship_icon():
    """Flat map-symbol ferry (side view, bow right)."""
    w, h = int(78 * S), int(40 * S); u = w / 78.0
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    dark = (44, 62, 72, 255)
    d.polygon([(2*u, 22*u), (76*u, 22*u), (66*u, 36*u), (10*u, 36*u)], fill=dark)        # hull
    d.rectangle((16*u, 12*u, 58*u, 22*u), fill=(250, 249, 243, 255), outline=dark, width=max(1, int(1.5*u)))
    d.rectangle((24*u, 4*u, 48*u, 12*u), fill=(250, 249, 243, 255), outline=dark, width=max(1, int(1.5*u)))
    d.rectangle((50*u, 2*u, 56*u, 12*u), fill=(192, 134, 47, 255))                        # funnel
    for x in range(20, 56, 7):
        d.rectangle((x*u, 15*u, (x+3)*u, 18*u), fill=dark)
    return img
SHIP_R = ship_icon(); SHIP_L = SHIP_R.transpose(Image.FLIP_LEFT_RIGHT)

SIGHTS = os.path.join(ROOT, "assets", "_sights")
credits = json.load(open(os.path.join(SIGHTS, "credits.json"), encoding="utf-8")) if os.path.exists(os.path.join(SIGHTS, "credits.json")) else {}

def cover(img, w, h):
    sc = max(w / img.width, h / img.height)
    img = img.resize((int(img.width*sc)+1, int(img.height*sc)+1), Image.LANCZOS)
    x = (img.width - w)//2; y = (img.height - h)//2
    return img.crop((x, y, x+w, y+h))

def postcard(sid, name):
    p = os.path.join(SIGHTS, f"{sid}.jpg")
    own = None
    try: src = load(p)
    except Exception:
        own = sorted(glob.glob(os.path.join(ROOT, "assets", sid, "*.jpg")))
        if not own: return None
        src = load(own[0])
    w, h = int(470*S), int(330*S); m = int(10*S)
    card = Image.new("RGBA", (w + 2*m, h + 2*m + int(26*S)), (255, 255, 255, 255))
    card.paste(cover(src, w, h), (m, m))
    d = ImageDraw.Draw(card)
    c = credits.get(sid, {})
    cr = ("Our photo" if own else "Photo: " + (c.get("artist") or "Wikimedia Commons")
          + (f" · {c['license']}" if c.get("license") else ""))
    d.text((m, h + m + int(6*S)), cr[:80], font=font(10), fill=(120, 120, 110))
    return card.rotate(2.5, expand=True, resample=Image.BICUBIC)
postcards = {s["id"]: postcard(s["id"], s["name"]) for s in stops}

import hashlib
HLDIR = os.path.join(ROOT, "assets", "_hl")
hl_credits = json.load(open(os.path.join(HLDIR, "credits.json"), encoding="utf-8")) if os.path.exists(os.path.join(HLDIR, "credits.json")) else {}
TYPE = {"B": "BEACH", "N": "NATURE", "C": "CULTURE", "H": "HISTORY", "P": "PEACEFUL"}
def hl_card(h):
    p = os.path.join(HLDIR, hashlib.md5(h["title"].encode()).hexdigest()[:12] + ".jpg")
    try: src = load(p)
    except Exception: return None
    w, h_ = int(430*S), int(300*S); m = int(9*S)
    card = Image.new("RGBA", (w + 2*m, h_ + 2*m + int(24*S)), (255, 255, 255, 255))
    card.paste(cover(src, w, h_), (m, m))
    c = hl_credits.get(h["title"], {})
    ImageDraw.Draw(card).text((m, h_ + m + int(5*S)),
        ("Photo: " + c.get("artist", "Wikimedia Commons") + (f" · {c['license']}" if c.get("license") else ""))[:80],
        font=font(10), fill=(120, 120, 110))
    return card.rotate(random.uniform(-3, 3), expand=True, resample=Image.BICUBIC)

def personal_pool():
    skip = {"_sights", "_hl"}
    files = []
    for d in sorted(glob.glob(os.path.join(ROOT, "assets", "*"))):
        if not os.path.isdir(d) or os.path.basename(d) in skip: continue
        for e in ("jpg", "jpeg", "png", "JPG"):
            files += glob.glob(os.path.join(d, f"*.{e}"))
    random.shuffle(files); return files
def snapshot(p):
    w = int(175*S); m = int(8*S)
    img = load(p); img.thumbnail((w*2, w*2))
    ph = cover(img, w, int(w*1.0))
    card = Image.new("RGBA", (w + 2*m, w + m + int(34*S)), (255, 255, 255, 255))
    card.paste(ph, (m, m))
    return card.rotate(random.uniform(-9, 9), expand=True, resample=Image.BICUBIC)
SNAPS = [snapshot(p) for p in personal_pool()]

# ---------- drawing helpers ----------
def crop_at(cx, cy):
    x = min(max(cx - VW/2, 0), MW - VW); y = min(max(cy - VH/2, 0), MH - VH)
    return base.crop((int(x), int(y), int(x)+VW, int(y)+VH)).copy(), x, y

def chip(img, line1, line2, color):
    d = ImageDraw.Draw(img, "RGBA")
    f1, f2 = font(22, True), font(12, True)
    w = int(max(d.textlength(line1, f1), d.textlength(line2, f2)) + 48*S); h = int(72*S); m = int(30*S)
    x, y = VW - w - m, m
    d.rounded_rectangle((x, y, x+w, y+h), 10*S, fill=(250, 249, 243, 240))
    d.rectangle((x, y, x+int(7*S), y+h), fill=color + (255,))
    d.text((x+24*S, y+8*S), line1, font=f1, fill=INK)
    d.text((x+24*S, y+44*S), line2, font=f2, fill=color)

def card(img, name, caption, color, legnm):
    d = ImageDraw.Draw(img, "RGBA")
    cw, ch, m = int(470*S), int(104*S), int(30*S)
    x, y = m, VH - ch - m
    d.rounded_rectangle((x, y, x+cw, y+ch), 10*S, fill=(250, 249, 243, 240))
    d.rectangle((x, y, x+int(7*S), y+ch), fill=color + (255,))
    d.text((x+24*S, y+10*S), name, font=font(30, True), fill=INK)
    d.text((x+24*S, y+52*S), caption, font=font(19), fill=(76, 90, 82))
    d.text((x+24*S, y+ch-24*S), legnm.upper(), font=font(12, True), fill=color)

def fmt(dt): return dt.strftime("%d %b %Y").lstrip("0")
def disp(t):
    t = t.split(" (")[0]
    for suf in (", Portugal", ", Morocco", ", Vaucluse"):
        t = t.replace(suf, "")
    return t

# floating snapshots: top band, right -> left
floaters = []; next_spawn = 0; snap_i = 0
def update_floaters(frame, gf):
    global next_spawn, snap_i
    if SNAPS and gf >= next_spawn:
        sn = SNAPS[snap_i % len(SNAPS)]; snap_i += 1
        floaters.append({"img": sn, "x": VW + 10, "y": random.uniform(14*S, 60*S),
                         "v": (VW + sn.width) / (5.5 * FPS)})
        next_spawn = gf + int(4.5 * FPS)
    for fl in floaters:
        fl["x"] -= fl["v"]
        frame.paste(fl["img"], (int(fl["x"]), int(fl["y"])), fl["img"])
    floaters[:] = [f for f in floaters if f["x"] > -f["img"].width]

def title_card(t, sub, secs, bg=None, dark=False):
    img = Image.new("RGB", (VW, VH), (33, 45, 39) if dark else PAPER)
    if bg:
        p = cover(load(bg), VW, VH)
        img = Image.composite(Image.new("RGB", (VW, VH), (15, 20, 17)), p, Image.new("L", (VW, VH), 110))
    d = ImageDraw.Draw(img)
    fh, fs = font(64, True), font(24)
    d.text(((VW - d.textlength(t, fh))/2, VH/2 - 100*S), t, font=fh, fill=PAPER)
    d.text(((VW - d.textlength(sub, fs))/2, VH/2 + 20*S), sub, font=fs, fill=(230, 200, 120))
    for _ in range(int(secs * FPS)): emit(img)

def credits_card(secs):
    img = Image.new("RGB", (VW, VH), (33, 45, 39)); d = ImageDraw.Draw(img)
    d.text((60*S, 40*S), "Picture credits", font=font(26, True), fill=PAPER)
    d.text((60*S, 78*S), "Location photos from Wikimedia Commons under their stated licences. "
           "Map: Natural Earth. Roads routed with OSRM / © OpenStreetMap contributors.", font=font(11), fill=(200, 200, 190))
    import re as _re
    seen, lines = set(), []
    for k, v in credits.items():
        if k not in stops_by_id or v.get("file") in seen: continue
        if not os.path.exists(os.path.join(SIGHTS, f"{k}.jpg")): continue
        seen.add(v.get("file"))
        art = v.get("artist", "unknown")
        m_ = _re.search(r"taken by ([^.]+)", art)
        art = (m_.group(1) if m_ else art).strip()
        place = v.get("title", stops_by_id[k]["name"]).split(",")[0].replace(" (Norway)", "")
        lines.append(f"{place}: {art} ({v.get('license', 'see Commons')})")
    for t, v in hl_credits.items():
        if v.get("file") in seen: continue
        if not os.path.exists(os.path.join(HLDIR, hashlib.md5(t.encode()).hexdigest()[:12] + ".jpg")): continue
        seen.add(v.get("file"))
        lines.append(f"{t.split(' (')[0].split(',')[0]}: {v.get('artist','unknown')} ({v.get('license','see Commons')})")
    COLS, ROWS = 3, 30
    per = COLS * ROWS
    pages = [lines[p:p+per] for p in range(0, len(lines), per)] or [[]]
    colw = (VW - 120*S) / COLS; lh = (VH - 150*S) / ROWS
    for pg, chunk in enumerate(pages):
        im = img.copy(); dd = ImageDraw.Draw(im)
        dd.text((VW - 160*S, 44*S), f"{pg+1} / {len(pages)}", font=font(12), fill=(200, 200, 190))
        for n, ln in enumerate(chunk):
            c, r = divmod(n, ROWS)
            dd.text((60*S + c*colw, 115*S + r*lh), ln[:58], font=font(9.5), fill=(225, 222, 210))
        for _ in range(int(secs * FPS)): emit(im)
stops_by_id = {s["id"]: s for s in stops}

# ---------- encode ----------
ff = subprocess.Popen(
    ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT],
    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def emit(img): ff.stdin.write(img.tobytes())

title_card(route["title"], route["subtitle"], 3, bg=os.path.join(ROOT, "assets", "_title", "van.jpg"))

md = ImageDraw.Draw(base)
cx, cy = P[0]; gf = 0
last_dir = (1.0, 0.0)

def stop_pause(i, frames):
    global cx, cy
    s = stops[i]; cxy = P[i]; col = legc[s["leg"]]
    pc = postcards.get(s["id"])
    for f in range(frames):
        # aim the camera right of the stop so the stop sits left-of-centre, clear of the postcard
        tx = cxy[0] + (0.20 * VW if pc is not None else 0)
        cx += (tx-cx)*0.12; cy += (cxy[1]-cy)*0.12
        frame, ox, oy = crop_at(cx, cy)
        vf = van_frame(*last_dir)
        frame.paste(vf, (int(cxy[0]-ox-vf.width/2), int(cxy[1]-oy-vf.height*0.85)), vf)
        if pc is not None:
            # slide in from the right over the first 8 frames
            k = min(1.0, (f+1)/8)
            px = int(VW - (pc.width + 40*S) * k); py = int(VH - pc.height - 40*S)
            frame.paste(pc, (px, py), pc)
        card(frame, s["name"], s["caption"], col, legname[s["leg"]])
        chip(frame, fmt(D[i]), legname[s["leg"]].upper(), col)
        emit(frame)

for sg in segs:
    i = sg["i"]
    stop_pause(i, PAUSE)
    md.ellipse((P[i][0]-6*S, P[i][1]-6*S, P[i][0]+6*S, P[i][1]+6*S), fill=PAPER, outline=INK, width=int(3*S))
    col = legc[stops[i+1]["leg"]]
    cur_date = D[i]
    for part in sg["parts"]:
        path = part["path"]; n = len(path); sea = part["mode"] == "sea"
        label2 = f"FERRY · {part['name']}" if sea else legname[stops[i+1]["leg"]].upper()
        for k in range(1, n):
            for h in part["events"].get(k, []):
                hx, hy = path[k]
                md.ellipse((hx-3.5*S, hy-3.5*S, hx+3.5*S, hy+3.5*S), fill=col, outline=INK, width=max(1, int(1.5*S)))
                cur_date = date.fromisoformat(h["date"])
                pcard = hl_card(h)
                for f in range(HL_FRAMES):
                    tx = hx + (0.20 * VW if pcard is not None else 0)
                    cx += (tx-cx)*0.15; cy += (hy-cy)*0.15
                    frame, ox, oy = crop_at(cx, cy)
                    vf = van_frame(*last_dir)
                    frame.paste(vf, (int(hx-ox-vf.width/2), int(hy-oy-vf.height*0.85)), vf)
                    if pcard is not None:
                        kk = min(1.0, (f+1)/6)
                        frame.paste(pcard, (int(VW - (pcard.width + 40*S) * kk), int(VH - pcard.height - 40*S)), pcard)
                    card(frame, disp(h["title"]), h["caption"], col,
                         TYPE.get(h["type"], "") + " · " + legname[stops[i+1]["leg"]])
                    update_floaters(frame, gf)
                    chip(frame, fmt(cur_date), label2, col)
                    emit(frame); gf += 1
            a, b = path[k-1], path[k]
            if sea:
                if (k // 4) % 2 == 0: md.line([a, b], fill=col, width=int(3*S))
            else:
                md.line([a, b], fill=col, width=int(5*S))
            la = path[min(n-1, k+6)]; lb = path[max(0, k-6)]   # smoothed heading
            dx, dy = la[0]-lb[0], la[1]-lb[1]
            if abs(dx) + abs(dy) > 0.5: last_dir = (dx, dy)
            cx += (b[0]-cx)*0.10; cy += (b[1]-cy)*0.10
            frame, ox, oy = crop_at(cx, cy)
            if sea:
                sh = SHIP_R if last_dir[0] >= 0 else SHIP_L
                bob = math.sin(gf * 0.3) * 2 * S
                frame.paste(sh, (int(b[0]-ox-sh.width/2), int(b[1]-oy-sh.height*0.75+bob)), sh)
            else:
                vf = van_frame(*last_dir)
                frame.paste(vf, (int(b[0]-ox-vf.width/2), int(b[1]-oy-vf.height*0.85)), vf)
            update_floaters(frame, gf)
            chip(frame, fmt(cur_date), label2, col)
            emit(frame); gf += 1

stop_pause(segs[-1]["i"]+1, PAUSE*2)
title_card("Pärnu → Sahara → Nordkapp", "Peter · Dianne · Kalev · one old van", 4,
           bg=os.path.join(ROOT, "assets", "_end", "dianne.jpg"))
credits_card(3.5)
ff.stdin.close(); ff.wait()
print("written", OUT)
