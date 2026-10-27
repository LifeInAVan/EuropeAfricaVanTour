// The chapter page (design handoff): chapter bar, side panel with the places grouped by day, and round
// photo markers on the map that group when they overlap on screen.
import { Marker, LngLatBounds, type Map as MapLibre } from "maplibre-gl";
import { dateOf, fmtDate, type Base, type Chapter, type Photos, type Point, type Site, type Trip, type Weather } from "./data";
import { baseBars } from "./bases";
import { countriesInOrder, coverOf, partName, span } from "./home";

const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);
const thumb = (photos: Photos, id: string) => photos[id]?.[0]?.replace(/\.jpg$/, "-s.jpg");

export const chapterDates = (trip: Trip, c: Chapter) => span(trip.start_date, c.start_day, c.end_day);

/** Previous/next, a chapter menu, and a 16-part bar sized by the length of each chapter. */
/** Where the van handle sits on the bar for a trip day, as a share (0-100) of the bar. */
export const barShare = (trip: Trip, day: number) => ((day + 0.5) / (trip.days + 1)) * 100;
export const dayLabel = (trip: Trip, day: number) => `Day ${day + 1} · ${dateOf(trip.start_date, day).toLocaleDateString("en-GB", { day: "numeric", month: "short" })}`;

export function chapterBar(trip: Trip, site: Site, current: number, vanDay: number, bases: Base[] = []) {
  const cs = trip.chapters, total = trip.days + 1;
  // chapters and any break between them (the winter break), in day order, each sized by its days
  const parts = [...cs.map((c) => ({ c, start_day: c.start_day, end_day: c.end_day, name: "" })),
    ...(trip.breaks ?? []).map((b) => ({ c: null, ...b }))].sort((a, b) => a.start_day - b.start_day);
  const prev = cs.find((c) => c.id === current - 1), next = cs.find((c) => c.id === current + 1);
  const start = dateOf(trip.start_date, 0), end = dateOf(trip.start_date, trip.days);
  const at = (id: number) => { // middle of a chapter's segment, as a share of the bar
    const c = cs.find((x) => x.id === id)!;
    return ((c.start_day + (c.end_day - c.start_day + 1) / 2) / total) * 100;
  };
  const month = (d: Date) => d.toLocaleDateString("en-GB", { month: "short" });
  const labels = [
    `<span style="left:0">${month(start)} · ${esc(trip.points[0].name)}</span>`,
    ...(site.bar_labels ?? []).map((l) => `<span class="mid" style="left:${at(l.chapter)}%">${esc(l.text)}</span>`),
    `<span style="right:0">${month(end)} · home</span>`,
  ];
  return `<div class="chbar">
    <div class="chbar-nav">
      <button type="button" class="round" data-c="${prev?.id ?? ""}" ${prev ? `aria-label="Previous chapter: ${esc(prev.name)}"` : 'disabled aria-label="Previous chapter"'}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
      <label class="chsel"><span class="vh">Chapter</span>
        <select id="chapter-select">${cs.map((c) => `<option value="${c.id}" ${c.id === current ? "selected" : ""}>Chapter ${c.id} of ${cs.length}: ${esc(c.name)}</option>`).join("")}</select></label>
      <button type="button" class="round" data-c="${next?.id ?? ""}" ${next ? `aria-label="Next chapter: ${esc(next.name)}"` : 'disabled aria-label="Next chapter"'}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
    </div>
    <div class="chbar-track">
      <div class="segs" style="grid-template-columns:${parts.map((x) => `${x.end_day - x.start_day + 1}fr`).join(" ")}">
        ${parts.map(({ c, name }) => c ? `<a href="#c=${c.id}" class="seg${c.id === current ? " on" : ""}${c.id <= 8 ? " one" : " two"}" title="Chapter ${c.id}: ${esc(c.name)}" aria-label="Chapter ${c.id}: ${esc(c.name)}"${c.id === current ? ' aria-current="page"' : ""}></a>`
          : `<span class="seg gap" title="${esc(name)}"></span>`).join("")}
      </div>
      ${bases.length ? baseBars(trip, bases) : ""}
      <div class="seg-labels">${labels.join("")}<span class="drag-hint">Drag the van to move through the trip</span></div>
      <div class="van-handle" role="slider" tabindex="0" aria-label="Day of the trip: drag the van, or use the arrow keys"
        aria-valuemin="1" aria-valuemax="${trip.days + 1}" aria-valuenow="${vanDay + 1}" aria-valuetext="${dayLabel(trip, vanDay)}"
        style="left:${barShare(trip, vanDay)}%"><img src="./van.png" alt="" draggable="false"><span class="van-tip">${dayLabel(trip, vanDay)}</span></div>
    </div>
  </div>`;
}

const TYPES = ["stop", "history", "culture", "nature", "peaceful", "beach"] as const;
const LABEL: Record<string, string> = { stop: "Main stops", history: "History", culture: "Culture", nature: "Nature", peaceful: "Peaceful", beach: "Beach" };
const ONE: Record<string, string> = { stop: "Main stop", history: "History", culture: "Culture", nature: "Nature", peaceful: "Peaceful", beach: "Beach" };

export interface PanelArgs {
  trip: Trip; photos: Photos; chapter: Chapter; shown: Point[]; types: Set<string>; weather: Weather | null; selected: string | null;
  at: number; // the day the van is on
  kindOf: (p: Point) => string; hiOf: (p: Point) => number | undefined; driveRow: (a: Point, b: Point) => string;
  drive: string; // "1,776 km · 36 h 50 min driving"
  restNote?: string; // for a chapter with no new places: where the van stays
}

// Festival results (on route / near miss, "our pass") are hand-written for the route before change list 2
// (27 Oct 2026), so they are hidden until phase 6 works them out from the dates.
const SHOW_FESTIVALS = false;

/** Cover, title, facts, festivals on our dates, filter pills, then the places grouped by day. */
export function chapterPanel(a: PanelArgs) {
  const { trip, photos, chapter: c, shown } = a;
  const all = trip.points.filter((p) => p.chapter === c.id);
  const cover = coverOf(c, photos);
  const temps = a.weather ? all.map(a.hiOf).filter((t): t is number => t !== undefined) : [];
  const fest = SHOW_FESTIVALS ? (trip.festivals ?? []).filter((f) => f.chapter === c.id && f.status === "on") : [];
  const present = TYPES.filter((t) => all.some((p) => a.kindOf(p) === t));
  const byDay = new Map<number, Point[]>();
  for (const p of shown) byDay.set(p.day, [...(byDay.get(p.day) ?? []), p]);
  const withDrives = !a.types.size;
  let prev: Point | null = null;
  const atDay = [...byDay.keys()].filter((d) => d <= a.at).pop() ?? [...byDay.keys()][0]; // the day shown for the van's day
  const days = [...byDay.entries()].map(([day, pts]) => `<li class="day${day === atDay ? " at" : ""}" data-day="${day}">
      <p class="day-h">Day ${day + 1} · ${fmtDate(dateOf(trip.start_date, day))}</p>
      <ol class="day-items">${pts.map((p) => {
        const n = all.indexOf(p) + 1, drive = withDrives && prev ? a.driveRow(prev, p) : "";
        prev = p;
        const t = thumb(photos, p.id);
        return `${drive}<li class="pt ${p.kind}${p.id === a.selected ? " selected" : ""}" data-p="${p.id}" tabindex="0">
          <span class="ph-round">${t ? `<img src="${t}" alt="" loading="lazy">` : ""}<span class="n" style="background:#1B2430">${n}</span></span>
          <span class="txt"><span class="name">${esc(p.name)}</span>
            <span class="meta">${ONE[a.kindOf(p)]}${p.country ? ` · ${esc(p.country)}` : ""}</span>
            <span class="cap">${esc(p.caption)}</span></span></li>`;
      }).join("")}</ol></li>`).join("");
  return `
    <button type="button" class="sheet-handle" aria-label="Show more or less of the list"><span></span></button>
    <div class="ch-cover" style="${cover ? `background-image:url('${cover}')` : ""}"></div>
    <div class="ch-head">
      <p class="kicker">Chapter ${c.id} · ${esc(partName(c.part).replace(/ \(\d{4}\)$/, ""))}</p>
      <h1>${esc(c.name)}</h1>
      <p class="ch-facts"><strong>${chapterDates(trip, c)}</strong> · ${c.end_day - c.start_day + 1} days · ${all.length} places${a.drive ? ` · ${a.drive}` : ""}<br>
        <span class="muted">${countriesInOrder(all).map(esc).join(" → ")}</span></p>
      <div class="ch-chips">
        ${temps.length ? `<span class="chip-info"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9A4F14" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5"/></svg>Typically ${Math.min(...temps)}–${Math.max(...temps)}°C by day</span>` : ""}
        ${SHOW_FESTIVALS ? `<span class="chip-info"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1D3B53" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>${fest.length} festival${fest.length === 1 ? "" : "s"} on our dates</span>` : ""}
      </div>
      ${fest.length ? (() => { // the first three; any more behind "N more"
        const li = (f: (typeof fest)[number]) => `<li><strong>${esc(f.event)}, ${esc(f.place)}</strong><span>${esc(f.our_pass)}</span></li>`;
        return `<ul class="fest">${fest.slice(0, 3).map(li).join("")}${fest.length > 3
          ? `<li class="more-fest"><details><summary>${fest.length - 3} more</summary><ul>${fest.slice(3).map(li).join("")}</ul></details></li>` : ""}</ul>`;
      })() : ""}
      ${all.length ? `<div class="pills" role="group" aria-label="Show">
        <button type="button" class="pill" data-t="" aria-pressed="${!a.types.size}">All ${all.length}</button>
        ${present.map((t) => `<button type="button" class="pill" data-t="${t}" aria-pressed="${a.types.has(t)}">${LABEL[t]}</button>`).join("")}
      </div>` : ""}
    </div>
    <ol class="days">${days || `<li class="empty-list">${all.length ? "No places of this type in this chapter." : `No new places in this chapter. ${a.restNote ?? ""}`}</li>`}</ol>`;
}

/** Round photo markers; markers that would overlap on screen become one marker with a count. */
export class PhotoMarkers {
  private markers: Marker[] = [];
  private pts: Point[] = [];
  private numbers = new Map<string, number>();
  private onMove = () => this.draw();
  constructor(private map: MapLibre, private photos: Photos, private onOpen: (id: string) => void, private onHover: (id: string | null) => void) {}

  show(pts: Point[], numbers: Map<string, number>) {
    this.pts = pts; this.numbers = numbers;
    this.map.off("moveend", this.onMove); this.map.on("moveend", this.onMove);
    this.draw();
  }
  clear() {
    this.map.off("moveend", this.onMove);
    this.markers.forEach((m) => m.remove()); this.markers = []; this.pts = [];
  }
  /** Highlight the marker (or group) holding this place. */
  mark(id: string | null, cls: "hover" | "sel") {
    for (const m of this.markers) {
      const wrap = m.getElement();
      wrap.firstElementChild?.classList.toggle(cls, !!id && (wrap.dataset.ids ?? "").split(",").includes(id));
      wrap.style.zIndex = wrap.firstElementChild?.matches(".hover, .sel") ? "3" : "";
    }
  }
  private draw() {
    this.markers.forEach((m) => m.remove()); this.markers = [];
    const R = 46, used = new Set<string>(), groups: Point[][] = [];
    const xy = new Map(this.pts.map((p) => [p.id, this.map.project([p.lon, p.lat])]));
    for (const p of this.pts) {
      if (used.has(p.id)) continue;
      const a = xy.get(p.id)!, g = this.pts.filter((q) => !used.has(q.id) && xy.get(q.id)!.dist(a) < R);
      g.forEach((q) => used.add(q.id)); groups.push(g);
    }
    for (const g of groups) {
      // MapLibre moves the outer element with a CSS transform, so the styling (and hover scaling) is on the inner button
      const p = g[0], wrap = document.createElement("div"), el = document.createElement("button");
      wrap.className = "pm-wrap"; wrap.dataset.ids = g.map((q) => q.id).join(","); wrap.appendChild(el);
      el.type = "button"; el.className = `pm${g.length > 1 ? " group" : ""}`;
      const t = this.photos[p.id]?.[0]?.replace(/\.jpg$/, "-s.jpg");
      el.innerHTML = `${t ? `<img src="${t}" alt="">` : ""}<span class="n" style="background:${g.length > 1 ? "#A85A1E" : "#1B2430"}">${g.length > 1 ? g.length : this.numbers.get(p.id)}</span>`;
      el.setAttribute("aria-label", g.length > 1 ? `${g.length} places close together: ${g.map((q) => q.name).join(", ")}` : p.name);
      el.title = g.map((q) => q.name).join(", ");
      el.addEventListener("click", (e) => {
        e.stopPropagation();
        if (g.length === 1) return this.onOpen(p.id);
        const b = new LngLatBounds(); g.forEach((q) => b.extend([q.lon, q.lat]));
        this.map.fitBounds(b, { padding: 90, maxZoom: Math.max(this.map.getZoom() + 2, 10), duration: 600 });
      });
      el.addEventListener("mouseenter", () => g.length === 1 && this.onHover(p.id));
      el.addEventListener("mouseleave", () => this.onHover(null));
      const lng = g.reduce((s, q) => s + q.lon, 0) / g.length, lat = g.reduce((s, q) => s + q.lat, 0) / g.length;
      this.markers.push(new Marker({ element: wrap }).setLngLat([lng, lat]).addTo(this.map));
    }
  }
}

/** The van cut-out for a map marker. It faces left, so it is flipped when the next place is further east. */
export function vanElement(eastward: boolean) {
  const el = document.createElement("div");
  el.className = "van-marker" + (eastward ? " east" : "");
  el.innerHTML = `<img src="./van.png" alt="Our van">`;
  return el;
}
