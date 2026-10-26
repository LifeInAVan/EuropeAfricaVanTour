// The place page (design handoff): slideshow with credits, tags, day and date, caption, Wikipedia
// description, typical weather, local map with links, other places the same day, previous/next.
import { Map as MapLibre, Marker } from "maplibre-gl";
import { siteStyle, MAP } from "./mapstyle";
import { dateOf, loadExtras, weatherIndex, type Credit, type Point, type Trip } from "./data";

const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);

export interface PanelOptions {
  trip: Trip;
  photos: Record<string, string[]>;
  route: GeoJSON.FeatureCollection;
  typeLabel: (p: Point) => string;
  siblings: (p: Point) => Point[]; // the places listed with it, for previous / next
  backLabel: () => string;
  onClose: () => void;
  onMove: (id: string) => void; // previous / next place
}

export class Panel {
  private el = document.getElementById("panel")!;
  private local: MapLibre | null = null;
  private slide = 0;
  private point: Point | null = null;
  private creditsCache: Record<string, Credit> | null = null;
  constructor(private o: PanelOptions) {
    this.el.addEventListener("click", (e) => this.click(e));
    document.addEventListener("keydown", (e) => {
      if (!this.point) return;
      if (e.key === "Escape") this.o.onClose();
      if (e.key === "ArrowRight") this.go(1);
      if (e.key === "ArrowLeft") this.go(-1);
    });
    let x0: number | null = null; // swipe between photos
    this.el.addEventListener("pointerdown", (e) => { if ((e.target as HTMLElement).closest(".frame")) x0 = e.clientX; });
    this.el.addEventListener("pointerup", (e) => {
      if (x0 !== null && Math.abs(e.clientX - x0) > 40) this.go(e.clientX < x0 ? 1 : -1);
      x0 = null;
    });
  }

  get openId() { return this.point?.id ?? null; }

  async open(p: Point) {
    const first = this.point?.id !== p.id;
    this.point = p;
    if (first) this.slide = 0;
    const { trip, photos } = this.o;
    const list = this.o.siblings(p);
    const i = list.indexOf(p), prev = i > 0 ? list[i - 1] : null, next = i >= 0 ? list[i + 1] ?? null : null;
    const d = dateOf(trip.start_date, p.day);
    const long = d.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
    const sameDay = trip.points.filter((q) => q.day === p.day && q.id !== p.id);
    const chevL = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>';
    const chevR = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>';
    const ext = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/></svg>';
    const osm = `https://www.openstreetmap.org/?mlat=${p.lat}&mlon=${p.lon}#map=14/${p.lat}/${p.lon}`;
    document.body.classList.add("panel-open");
    this.el.hidden = false;
    this.el.innerHTML = `
      <div class="place-bar">
        <button type="button" class="back" data-act="close">${chevL}${esc(this.o.backLabel())}</button>
        <div class="place-nav">
          ${prev ? `<button type="button" data-act="prev">${chevL}<span>${esc(prev.name)}</span></button>` : ""}
          ${i >= 0 ? `<span class="of">${i + 1} of ${list.length}</span>` : ""}
          ${next ? `<button type="button" data-act="next"><span>${esc(next.name)}</span>${chevR}</button>` : ""}
        </div>
      </div>
      <div class="place-main">
        <div class="place-media">
          <button type="button" class="back-over" data-act="close" aria-label="Back to ${esc(this.o.backLabel())}">${chevL}</button>
          <div class="slides"></div>
        </div>
        <div class="place-info">
          <p class="tags"><span class="tag type">${esc(this.o.typeLabel(p))}</span>${p.country ? `<span class="tag">${esc(p.country)}</span>` : ""}</p>
          <h1>${esc(p.name)}</h1>
          <p class="when">Day ${p.day + 1} · ${long}</p>
          <p class="caption">${esc(p.caption)}.</p>
          <div class="desc"></div>
          <div class="wx"><p class="wx-h">Typical weather on ${d.toLocaleDateString("en-GB", { day: "numeric", month: "long" })}</p><p class="muted">Loading…</p></div>
          <div class="local">
            <div id="local-map" role="region" aria-label="Local map of ${esc(p.name)}"></div>
            <div class="local-links">
              ${p.link.includes("wikipedia.org") ? `<a href="${esc(p.link)}" target="_blank" rel="noopener">More on Wikipedia${ext}</a>` : ""}
              <a href="${esc(osm)}" target="_blank" rel="noopener">Open in OpenStreetMap${ext}</a>
            </div>
          </div>
          ${sameDay.length ? `<div class="same"><p class="wx-h">Same day</p>${sameDay.map((q) => {
            const t = photos[q.id]?.[0]?.replace(/\.jpg$/, "-s.jpg");
            return `<button type="button" class="same-card" data-act="goto" data-id="${q.id}">
              <span class="same-img" style="${t ? `background-image:url('${t}')` : ""}"></span>
              <span class="same-txt"><strong>${esc(q.name)}</strong><span>${esc(q.caption)}</span></span></button>`;
          }).join("")}</div>` : ""}
          <div class="place-foot">
            ${prev ? `<button type="button" data-act="prev"><span>‹ Previous</span><strong>${esc(prev.name)}</strong></button>` : "<span></span>"}
            ${next ? `<button type="button" data-act="next" class="nx"><span>Next ›</span><strong>${esc(next.name)}</strong></button>` : ""}
          </div>
        </div>
      </div>`;
    this.el.scrollTop = 0; window.scrollTo(0, 0);
    this.renderSlides(null);
    void this.showLocal(p);
    const { credits, weather, descriptions } = await loadExtras();
    if (this.point !== p) return; // another place was opened meanwhile
    this.renderSlides(credits);
    const desc = descriptions[p.id];
    if (desc) this.el.querySelector(".desc")!.innerHTML = `<p>${esc(desc.text)}</p>
      <p class="from">From <a href="${esc(desc.url)}" target="_blank" rel="noopener">Wikipedia: ${esc(desc.title)}</a> (CC BY-SA)</p>`;
    const w = weather.points[p.id], k = weatherIndex(d);
    const at = w && w.elev >= 1500 ? ` at ${w.elev.toLocaleString("en-GB")} m` : "";
    this.el.querySelector(".wx")!.innerHTML = w ? `
      <p class="wx-h">Typical weather on ${d.toLocaleDateString("en-GB", { day: "numeric", month: "long" })}${at}</p>
      <div class="wx-grid">
        <div><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#9A4F14" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5"/></svg><b>${w.hi[k]}°C</b><span>by day</span></div>
        <div><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1D3B53" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/></svg><b>${w.lo[k]}°C</b><span>at night</span></div>
        <div><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2E5D8C" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M7 15a4 4 0 0 1 .5-8A5.5 5.5 0 0 1 18 8a3.5 3.5 0 0 1 0 7H7z"/><path d="M9 18l-1 3M13 18l-1 3M17 18l-1 3"/></svg><b>${w.rain[k]} in 10</b><span>days with rain</span></div>
      </div>
      <p class="wx-note">From ${weather.years} records. Typical, not a forecast.</p>`
      : `<p class="muted">No weather data for this place.</p>`;
  }

  close() {
    this.point = null;
    this.el.hidden = true;
    this.el.innerHTML = "";
    document.body.classList.remove("panel-open");
    this.local?.remove(); // the map's container was removed with the panel content
    this.local = null;
  }

  private renderSlides(credits: Record<string, Credit> | null) {
    const p = this.point!;
    const ph = this.o.photos[p.id] ?? [];
    const box = this.el.querySelector(".slides")!;
    if (!ph.length) { box.innerHTML = `<div class="frame empty">No photos chosen for this place yet.</div>`; return; }
    const src = ph[this.slide];
    const c = credits?.[src];
    const credit = c
      ? `Photo: ${c.url ? `<a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.artist ?? "unknown")}</a>` : esc(c.artist ?? "unknown")}
         · ${c.license_url ? `<a href="${esc(c.license_url)}" target="_blank" rel="noopener">${esc(c.license ?? "")}</a>` : esc(c.license ?? "")}
         · ${esc(c.source ?? "")}`
      : "&nbsp;";
    box.innerHTML = `
      <div class="frame">
        <img src="${src}" alt="${esc(p.name)}, photo ${this.slide + 1} of ${ph.length}">
        ${ph.length > 1 ? `<button class="arrow l" data-act="photo-prev" aria-label="Previous photo">‹</button>
        <button class="arrow r" data-act="photo-next" aria-label="Next photo">›</button>
        <span class="count">${this.slide + 1} / ${ph.length}</span>` : ""}
      </div>
      <p class="credit">${credit}</p>
      ${ph.length > 1 ? `<div class="thumbs">${ph.map((s, j) => `<button data-act="photo" data-i="${j}" aria-label="Photo ${j + 1}" ${j === this.slide ? 'aria-current="true"' : ""}>
        <img src="${s.replace(/\.jpg$/, "-s.jpg")}" alt="" loading="lazy"></button>`).join("")}</div>` : ""}`;
    this.creditsCache = credits;
  }

  private go(step: number) {
    const n = (this.o.photos[this.point!.id] ?? []).length;
    if (n < 2) return;
    this.slide = (this.slide + step + n) % n;
    this.renderSlides(this.creditsCache);
  }

  private click(e: MouseEvent) {
    const b = (e.target as HTMLElement).closest<HTMLElement>("[data-act]");
    if (!b || !this.point) return;
    const act = b.dataset.act;
    if (act === "close") this.o.onClose();
    if (act === "photo-prev") this.go(-1);
    if (act === "photo-next") this.go(1);
    if (act === "photo") { this.slide = Number(b.dataset.i); this.renderSlides(this.creditsCache); }
    if (act === "goto" && b.dataset.id) this.o.onMove(b.dataset.id);
    if (act === "prev" || act === "next") {
      const list = this.o.siblings(this.point);
      const q = list[list.indexOf(this.point) + (act === "next" ? 1 : -1)];
      if (q) this.o.onMove(q.id);
    }
  }

  private async showLocal(p: Point) {
    const style = await siteStyle(true);
    const box = document.getElementById("local-map");
    if (!box || this.point !== p) return; // another place was opened meanwhile
    // a fresh map each time: the panel's content (and so the container) is rebuilt per place
    this.local?.remove();
    this.local = new MapLibre({
      container: box, style,
      center: [p.lon, p.lat], zoom: p.kind === "stop" ? 11 : 12, attributionControl: { compact: true },
      cooperativeGestures: true,
    });
    this.local.on("load", () => {
      this.local?.addSource("route", { type: "geojson", data: this.o.route });
      this.local?.addLayer({ id: "route", type: "line", source: "route", paint: { "line-color": ["case", ["<=", ["get", "chapter"], 8], MAP.ochre, MAP.blue], "line-width": 3.6, "line-opacity": 0.9 } });
    });
    new Marker({ color: MAP.blue }).setLngLat([p.lon, p.lat]).addTo(this.local);
  }
}
