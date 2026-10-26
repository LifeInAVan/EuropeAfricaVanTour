// The place panel: photos with credits, date, caption, typical weather, link and a local map.
import { Map as MapLibre, Marker } from "maplibre-gl";
import { dateOf, fmtYear, loadExtras, weatherIndex, type Credit, type Point, type Trip } from "./data";

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
    const { trip } = this.o;
    const list = this.o.siblings(p);
    const i = list.indexOf(p);
    const d = dateOf(trip.start_date, p.day);
    document.body.classList.add("panel-open");
    this.el.hidden = false;
    this.el.innerHTML = `
      <div class="panel-bar">
        <button class="close" data-act="close" aria-label="Back to the list">← ${esc(this.o.backLabel())}</button>
        <span class="nav">
          <button data-act="prev" ${i <= 0 ? "disabled" : ""} aria-label="Previous place">‹</button>
          <span>${i >= 0 ? `${i + 1} / ${list.length}` : ""}</span>
          <button data-act="next" ${i < 0 || i === list.length - 1 ? "disabled" : ""} aria-label="Next place">›</button>
        </span>
      </div>
      <div class="slides"></div>
      <div class="panel-body">
        <h2>${esc(p.name)}</h2>
        <p class="meta">Day ${p.day} · ${fmtYear(d)} · ${esc(this.o.typeLabel(p))}</p>
        <p class="caption">${esc(p.caption)}</p>
        <p class="weather muted">Loading typical weather…</p>
        <p><a class="more" href="${esc(p.link)}" target="_blank" rel="noopener">${p.link.includes("wikipedia.org") ? "More on Wikipedia" : "Show on OpenStreetMap"} ↗</a></p>
        <div id="local-map" aria-label="Local map"></div>
      </div>`;
    this.el.scrollTop = 0;
    this.renderSlides(null);
    this.showLocal(p);
    const { credits, weather } = await loadExtras();
    if (this.point !== p) return; // another place was opened meanwhile
    this.renderSlides(credits);
    const w = weather.points[p.id];
    const k = weatherIndex(d);
    const at = w && w.elev >= 1500 ? ` at ${w.elev.toLocaleString("en-GB")} m` : "";
    this.el.querySelector(".weather")!.innerHTML = w
      ? `<b>Typical for ${d.toLocaleDateString("en-GB", { day: "numeric", month: "short" })}${at}:</b> ${w.hi[k]}°C by day, ${w.lo[k]}°C at night, rain on ${w.rain[k]} day${w.rain[k] === 1 ? "" : "s"} in 10.
         <span class="note">Typical weather from ${weather.years} records, not a forecast.</span>`
      : "No weather data for this place.";
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
    if (act === "prev" || act === "next") {
      const list = this.o.siblings(this.point);
      const q = list[list.indexOf(this.point) + (act === "next" ? 1 : -1)];
      if (q) this.o.onMove(q.id);
    }
  }

  private showLocal(p: Point) {
    const box = document.getElementById("local-map")!;
    // a fresh map each time: the panel's content (and so the container) is rebuilt per place
    this.local?.remove();
    this.local = new MapLibre({
      container: box, style: "https://tiles.openfreemap.org/styles/liberty",
      center: [p.lon, p.lat], zoom: p.kind === "stop" ? 10 : 12, attributionControl: { compact: true },
      cooperativeGestures: true,
    });
    this.local.on("load", () => {
      this.local?.addSource("route", { type: "geojson", data: this.o.route });
      this.local?.addLayer({ id: "route", type: "line", source: "route", paint: { "line-color": "#c2412d", "line-width": 3, "line-opacity": 0.8 } });
    });
    new Marker({ color: "#c2412d" }).setLngLat([p.lon, p.lat]).addTo(this.local);
  }
}
