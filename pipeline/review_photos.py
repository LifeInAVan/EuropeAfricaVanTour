#!/usr/bin/env python3
"""Local page for choosing each point's slideshow photos, one chapter at a time.

python pipeline/review_photos.py    then open http://localhost:8765
Click a photo to add or remove it; the star makes it the main photo. "Save chapter" writes
data/photo_picks.json. Points not yet saved show the suggested choice (top 5 by score).
"""
import json, os, http.server, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # repository root: data/, docs/, assets/
SLIDES = os.path.join(HERE, "cache", "slides")
PICKS = os.path.join(ROOT, "data", "photo_picks.json")
PORT, PER_POINT = 8765, 5

def load(p, default=None):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default

def suggested(c):
    files = [x["file"] for x in c["items"][:PER_POINT]]
    film = next((x["file"] for x in c["items"] if x["file"] == c.get("film_file")), None)
    if film: files = [film] + [f for f in files if f != film][:PER_POINT - 1]    # main photo first
    return dict(main=files[0] if files else None, picks=files, reviewed=False)

def chapter_data(n):
    trip = load(os.path.join(ROOT, "data", "trip.json"))
    cands = load(os.path.join(SLIDES, "candidates.json"), {})
    picks = load(PICKS, {})
    pts = []
    for p in trip["points"]:
        if p["chapter"] != n: continue
        c = cands.get(p["id"])
        pts.append(dict(id=p["id"], name=p["name"], caption=p["caption"], day=p["day"], kind=p["kind"],
                        link=p["link"], fetched=c is not None,
                        items=[{k: x.get(k) for k in ("file", "w", "h", "license", "artist", "source", "page", "score")}
                               for x in (c or {}).get("items", [])],
                        choice=picks.get(p["id"]) or (suggested(c) if c else None)))
    return dict(chapter=next(c for c in trip["chapters"] if c["id"] == n), start=trip["start_date"],
                chapters=[dict(id=c["id"], name=c["name"]) for c in trip["chapters"]], points=pts)

PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Photo review</title><style>
:root{--bg:#f6f5f2;--fg:#1c1c1a;--muted:#6b6a65;--line:#d9d6cf;--pick:#2F6B57;--main:#d39b1f;--card:#fff}
body{margin:0;font:15px/1.4 system-ui,sans-serif;background:var(--bg);color:var(--fg)}
header{position:sticky;top:0;z-index:2;background:var(--card);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
header h1{font-size:17px;margin:0 8px 0 0} select,button{font:inherit;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card)}
button.primary{background:var(--pick);color:#fff;border-color:var(--pick)} #status{color:var(--muted)}
main{padding:8px 16px 60px} .pt{background:var(--card);border:1px solid var(--line);border-radius:8px;margin:12px 0;padding:10px 12px}
.pt h2{font-size:16px;margin:0} .pt .meta{color:var(--muted);font-size:13px;margin:2px 0 8px} .pt .meta a{color:inherit}
.row{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px} .ph{position:relative;flex:0 0 auto;cursor:pointer;border:3px solid transparent;border-radius:6px;opacity:.45}
.ph img{display:block;height:130px;border-radius:3px} .ph.on{border-color:var(--pick);opacity:1} .ph.main{border-color:var(--main)}
.ph .n{position:absolute;top:4px;left:4px;background:var(--pick);color:#fff;border-radius:10px;padding:0 7px;font-size:12px}
.ph.main .n{background:var(--main)} .ph .star{position:absolute;top:2px;right:4px;font-size:22px;color:#fff;text-shadow:0 0 3px #000;background:none;border:0;padding:0;cursor:pointer}
.ph.main .star{color:var(--main)} .ph .cr{font-size:11px;color:var(--muted);max-width:190px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tag{font-size:12px;border-radius:4px;padding:1px 6px;margin-left:6px} .tag.done{background:#dcebe4;color:var(--pick)} .tag.todo{background:#f3e6c8;color:#7a5a10}
.empty{color:var(--muted);font-style:italic}
</style></head><body>
<header><h1>Photo review</h1><select id="ch"></select><button id="save" class="primary">Save chapter</button><span id="status"></span>
<span style="margin-left:auto;color:var(--muted);font-size:13px">Click a photo to add or remove it · ★ = main photo · aim for 3–5</span></header>
<main id="list"></main>
<script>
const $ = s => document.querySelector(s); let data, dirty = false;
const fmt = d => { const t = new Date(data.start); t.setDate(t.getDate() + d); return t.toLocaleDateString("en-GB", {weekday:"short", day:"numeric", month:"short", year:"numeric"}); };
async function load(n) {
  data = await (await fetch("/api/chapter/" + n)).json(); dirty = false;
  $("#ch").innerHTML = data.chapters.map(c => `<option value="${c.id}" ${c.id == n ? "selected" : ""}>${c.id}. ${c.name}</option>`).join("");
  render(); history.replaceState(null, "", "#" + n);
}
function render() {
  const done = data.points.filter(p => p.choice && p.choice.reviewed).length;
  $("#status").textContent = `${data.points.length} points · ${done} saved` + (dirty ? " · unsaved changes" : "");
  $("#list").innerHTML = data.points.map((p, i) => {
    const ch = p.choice || {picks: [], main: null};
    const tag = !p.fetched ? '<span class="tag todo">still fetching</span>' : ch.reviewed ? '<span class="tag done">saved</span>' : '<span class="tag todo">suggested</span>';
    const row = p.items.length ? p.items.map((x, j) => {
      const k = ch.picks.indexOf(x.file), on = k >= 0, main = ch.main === x.file;
      return `<div class="ph ${on ? "on" : ""} ${main ? "main" : ""}" data-p="${i}" data-f="${j}" title="${x.file}\n${x.artist} · ${x.license} · ${x.source} · ${x.w}×${x.h}">
        <img src="/prev/${p.id}/${j}.jpg" loading="lazy" alt="">${on ? `<span class="n">${k + 1}</span>` : ""}
        <button class="star" data-p="${i}" data-f="${j}" title="Make main photo">★</button><div class="cr">${x.artist} · ${x.license}</div></div>`;
    }).join("") : '<div class="empty">No photos found yet.</div>';
    return `<section class="pt"><h2>${p.name}${tag}</h2><div class="meta">${fmt(p.day)} · ${p.kind} · ${p.caption} · <a href="${p.link}" target="_blank">more</a></div><div class="row">${row}</div></section>`;
  }).join("");
}
$("#list").addEventListener("click", e => {
  const el = e.target.closest("[data-f]"); if (!el) return;
  const p = data.points[el.dataset.p], file = p.items[el.dataset.f].file;
  p.choice = p.choice || {picks: [], main: null};
  const c = p.choice, k = c.picks.indexOf(file);
  if (e.target.classList.contains("star")) { c.main = file; if (k >= 0) c.picks.splice(k, 1); c.picks.unshift(file); }
  else if (k >= 0) { c.picks.splice(k, 1); if (c.main === file) c.main = c.picks[0] || null; }
  else { c.picks.push(file); if (!c.main) c.main = file; }
  dirty = true; render();
});
$("#ch").onchange = e => { if (!dirty || confirm("Discard unsaved changes?")) load(e.target.value); };
$("#save").onclick = async () => {
  const body = {}; data.points.forEach(p => { if (p.choice) body[p.id] = {main: p.choice.main, picks: p.choice.picks}; });
  const r = await fetch("/api/save", {method: "POST", body: JSON.stringify(body)});
  $("#status").textContent = r.ok ? "Saved." : "Save failed."; if (r.ok) load(data.chapter.id);
};
window.onbeforeunload = () => dirty ? true : undefined;
load(+location.hash.slice(1) || 1);
</script></body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def send(self, body, kind="application/json", code=200):
        self.send_response(code); self.send_header("Content-Type", kind); self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        path = urllib.parse.unquote(self.path.split("?")[0])
        if path == "/": return self.send(PAGE.encode(), "text/html; charset=utf-8")
        if path.startswith("/api/chapter/"):
            return self.send(json.dumps(chapter_data(int(path.rsplit("/", 1)[1])), ensure_ascii=False).encode())
        if path.startswith("/prev/"):
            f = os.path.normpath(os.path.join(SLIDES, path.lstrip("/")))
            if f.startswith(os.path.join(SLIDES, "prev")) and os.path.isfile(f):
                return self.send(open(f, "rb").read(), "image/jpeg")
        self.send(b"not found", "text/plain", 404)
    def do_POST(self):
        if self.path != "/api/save": return self.send(b"not found", "text/plain", 404)
        new = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        picks = load(PICKS, {})
        for pid, c in new.items(): picks[pid] = dict(main=c["main"], picks=c["picks"], reviewed=True)
        json.dump(dict(sorted(picks.items())), open(PICKS, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
        self.send(b'{"ok":true}')
    def log_message(self, *a): pass

if __name__ == "__main__":
    print(f"Photo review on http://localhost:{PORT}  (Ctrl+C to stop)", flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
