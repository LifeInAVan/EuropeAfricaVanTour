import { Map as MapLibre, LngLatBounds, NavigationControl, setWorkerUrl, type GeoJSONSource, type MapLayerMouseEvent } from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url"; // MapLibre 6 keeps its worker in a separate file
import "maplibre-gl/dist/maplibre-gl.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/barlow-condensed/600.css";
import "@fontsource/barlow-condensed/700.css";
import "./style.css";
import { loadAll, loadExtras, dateOf, fmtDay, fmtYear, weatherIndex, type Drive, type Point, type Trip, type Photos, type Site, type Weather } from "./data";
import { Panel } from "./panel";
import { siteStyle, MAP } from "./mapstyle";
import { renderHome } from "./home";
import { chapterBar, chapterPanel, PhotoMarkers } from "./chapter";

const TYPES = ["stop", "beach", "nature", "culture", "history", "peaceful"] as const;
const TYPE_LABEL: Record<string, string> = {
  stop: "Main stop", beach: "Beach", nature: "Nature", culture: "Culture", history: "History", peaceful: "Peaceful",
};
const TYPE_COLOUR: Record<string, string> = {
  stop: "#1D3B53", beach: "#2a8fbd", nature: "#3d8a4a", culture: "#9b4fa8", history: "#b5652b", peaceful: "#5f7f8f",
};
type View = "home" | "chapter" | "calendar" | "country" | "temp";
const VIEWS: [View, string][] = [["home", "Front page"], ["chapter", "Chapters"], ["calendar", "Calendar"], ["country", "Countries"], ["temp", "Temperature"]];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

const $ = <T extends HTMLElement>(sel: string) => document.querySelector(sel) as T;
const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);
let trip: Trip, photos: Photos, map: MapLibre, mapReady = false, panel: Panel, weather: Weather | null = null;
let hovered: string | null = null, selected: string | null = null, section: string | null = null;
let site: Site, route: GeoJSON.FeatureCollection, markers: PhotoMarkers | null = null;

// Everything shown is worked out from this state, which is also kept in the page address.
const state = {
  view: "chapter" as View,
  chapter: 1,
  month: "", // "2027-09"
  day: null as number | null, // a trip day chosen in the calendar
  country: "",
  lo: 18, hi: 28, // temperature range, °C
  types: new Set<string>(), // empty = all types
};

const kindOf = (p: Point) => (p.kind === "stop" ? "stop" : p.type ?? "culture");
const dateOfPoint = (p: Point) => dateOf(trip.start_date, p.day);
const monthKey = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
const monthName = (m: string) => `${MONTHS[Number(m.slice(5)) - 1]} ${m.slice(0, 4)}`;
const hiOf = (p: Point) => weather?.points[p.id]?.hi[weatherIndex(dateOfPoint(p))];

/** Trip months, countries in the order first reached. */
let months: string[] = [], countries: string[] = [];

// ---------- which places are shown ----------
function basePoints(): Point[] {
  const all = trip.points;
  switch (state.view) {
    case "chapter": return all.filter((p) => p.chapter === state.chapter);
    case "calendar": return all.filter((p) => (state.day !== null ? p.day === state.day : monthKey(dateOfPoint(p)) === state.month));
    case "country": return all.filter((p) => p.country === state.country);
    case "home": return [];
    case "temp": return weather ? all.filter((p) => { const t = hiOf(p); return t !== undefined && t >= state.lo && t <= state.hi; }) : [];
  }
}
function shown(): Point[] {
  const b = basePoints();
  return state.types.size ? b.filter((p) => state.types.has(kindOf(p))) : b;
}

// ---------- page address: #v=calendar&m=2027-09&t=beach,nature&p=point-id ----------
function readHash(): string | null {
  const h = new URLSearchParams(location.hash.slice(1));
  const p = trip.points.find((x) => x.id === h.get("p"));
  const v = h.get("v") as View | null;
  // an empty address opens the front page; old links with only a chapter or place still open the chapter
  state.view = VIEWS.some(([k]) => k === v) ? v! : (h.has("c") || h.has("p") ? "chapter" : "home");
  section = h.get("s");
  const c = Number(h.get("c"));
  state.chapter = trip.chapters.some((x) => x.id === c) ? c : p?.chapter ?? 1;
  state.month = months.includes(h.get("m") ?? "") ? h.get("m")! : months[0];
  const d = h.get("d");
  state.day = d !== null && d !== "" && !Number.isNaN(Number(d)) ? Number(d) : null;
  state.country = countries.includes(h.get("k") ?? "") ? h.get("k")! : countries[0];
  const r = (h.get("r") ?? "").split("-").map(Number);
  if (r.length === 2 && r.every(Number.isFinite)) [state.lo, state.hi] = r;
  state.types = new Set((h.get("t") ?? "").split(",").filter((t) => (TYPES as readonly string[]).includes(t)));
  if (p && state.view === "chapter") state.chapter = p.chapter; // a link to a place opens its chapter
  return p?.id ?? null;
}
function writeHash() {
  const h = new URLSearchParams();
  if (state.view !== "chapter") h.set("v", state.view);
  if (state.view === "home" && section) h.set("s", section);
  if (state.view === "chapter") h.set("c", String(state.chapter));
  if (state.view === "calendar") { h.set("m", state.month); if (state.day !== null) h.set("d", String(state.day)); }
  if (state.view === "country") h.set("k", state.country);
  if (state.view === "temp") h.set("r", `${state.lo}-${state.hi}`);
  if (state.types.size) h.set("t", [...state.types].join(","));
  if (selected) h.set("p", selected);
  history.replaceState(null, "", "#" + h.toString().replace(/%2C/g, ","));
}

// ---------- header: views, the row for the current view, type filters ----------
function renderHeader() {
  const nav: [string, string, boolean][] = [
    ["#v=home&s=route", "Route", state.view === "home" && section !== "van"],
    [`#c=${state.chapter}`, "Chapters", state.view === "chapter"],
    [`#v=calendar&m=${state.month}`, "Calendar", state.view === "calendar"],
    [`#v=country&k=${encodeURIComponent(state.country)}`, "Countries", state.view === "country"],
    ["#v=home&s=van", "The van", state.view === "home" && section === "van"],
  ];
  $("#views").innerHTML = nav.map(([href, label, on]) => `<a class="nav-link" href="${href}" ${on ? 'aria-current="page"' : ""}>${label}</a>`).join("");
  const sub = $("#subnav");
  if (state.view === "home") {
    sub.innerHTML = ""; $("#filters").innerHTML = ""; return;
  } else if (state.view === "chapter") {
    sub.innerHTML = chapterBar(trip, site, state.chapter);
    $("#filters").innerHTML = ""; // the type pills are in the chapter panel
    return;
  } else if (state.view === "calendar") {
    sub.innerHTML = months.map((m) => `<button class="chip" data-m="${m}" aria-pressed="${m === state.month}">${monthName(m)}</button>`).join("");
  } else if (state.view === "country") {
    sub.innerHTML = countries.map((k) => {
      const n = trip.points.filter((p) => p.country === k).length;
      return `<button class="chip" data-k="${esc(k)}" aria-pressed="${k === state.country}">${esc(k)} <b>${n}</b></button>`;
    }).join("");
  } else {
    sub.innerHTML = `<label class="range">Typical daytime high from
      <input type="range" id="lo" min="-15" max="40" value="${state.lo}" aria-label="Lowest"> <output id="lo-v">${state.lo}°C</output>
      to <input type="range" id="hi" min="-15" max="40" value="${state.hi}" aria-label="Highest"> <output id="hi-v">${state.hi}°C</output></label>
      <span class="legend">${[-5, 5, 12, 18, 24, 30].map((t) => `<i style="background:${tempColour(t)}"></i>${t}°`).join("")}</span>`;
  }
  sub.querySelector<HTMLElement>('[aria-pressed="true"]')?.scrollIntoView({ block: "nearest", inline: "center" });
  $("#filters").innerHTML = `<span class="lbl">Show</span>` + TYPES.map((t) =>
    `<button class="filter" data-t="${t}" aria-pressed="${state.types.has(t)}" style="--c:${TYPE_COLOUR[t]}">${TYPE_LABEL[t]}</button>`).join("")
    + (state.types.size ? `<button class="filter clear" data-t="">All types</button>` : "");
}

// ---------- the left-hand list ----------
function rows(pts: Point[]) {
  // drive lines between places only where the list follows the route: a chapter or a calendar month or day
  const withDrives = !state.types.size && (state.view === "chapter" || state.view === "calendar");
  return `<ol class="points">${pts.map((p, i) => {
    const drive = withDrives && i > 0 ? driveRow(pts[i - 1], p) : "";
    const thumb = photos[p.id]?.[0], k = kindOf(p), t = state.view === "temp" ? hiOf(p) : undefined;
    const mark = t !== undefined ? `${t}°` : String(i + 1);
    const colour = t !== undefined ? tempColour(t) : TYPE_COLOUR[k];
    return `${drive}<li class="pt ${p.kind}${p.id === selected ? " selected" : ""}" data-p="${p.id}" tabindex="0">
      <span class="num${t !== undefined ? " temp" : ""}" style="--c:${colour}">${mark}</span>
      ${thumb ? `<img src="${thumb.replace(/\.jpg$/, "-s.jpg")}" alt="" loading="lazy">` : `<span class="noimg"></span>`}
      <span class="txt"><span class="name">${esc(p.name)}</span>
        <span class="meta">${fmtDay(dateOfPoint(p))} · ${TYPE_LABEL[k]}${state.view !== "country" && p.country ? ` · ${esc(p.country)}` : ""}</span>
        <span class="cap">${esc(p.caption)}</span></span>
    </li>`;
  }).join("")}</ol>` + (pts.length ? "" : `<p class="empty-list">No places match. ${state.types.size ? "Try showing all types." : ""}</p>`);
}

/** Runs of consecutive trip days, e.g. two separate visits to Spain. */
function spans(days: number[]) {
  const out: [number, number][] = [];
  for (const d of [...new Set(days)].sort((a, b) => a - b)) {
    const last = out[out.length - 1];
    if (last && d - last[1] <= 3) last[1] = d; else out.push([d, d]);
  }
  return out.map(([a, b]) => a === b ? fmtYear(dateOf(trip.start_date, a)) : `${fmtYear(dateOf(trip.start_date, a))} – ${fmtYear(dateOf(trip.start_date, b))}`);
}

function renderList() {
  const pts = shown();
  let head = "";
  if (state.view === "chapter") {
    const chapter = trip.chapters.find((x) => x.id === state.chapter)!;
    $("#list").innerHTML = chapterPanel({ trip, photos, chapter, shown: pts, types: state.types, weather, selected, kindOf, hiOf, driveRow,
      drive: totals(trip.drives.filter((d) => d.chapter === chapter.id)) });
    $("#list").scrollTop = 0;
    return;
  }
  if (state.view === "calendar") {
    head = calendarGrid() + `<h2 class="day-h">${state.day !== null ? fmtYear(dateOf(trip.start_date, state.day)) : monthName(state.month)}</h2>
      <p class="muted">${count(pts)}${state.day !== null ? ` · <button class="link" data-act="month">whole month</button>` : " · choose a day to see just that day"}</p>`;
  } else if (state.view === "country") {
    head = `<p class="eyebrow">Country</p><h2>${esc(state.country)}</h2>
      <p class="muted">${count(pts)} · ${spans(trip.points.filter((p) => p.country === state.country).map((p) => p.day)).join("; ")}</p>`;
  } else {
    head = `<p class="eyebrow">Typical daytime high on the day we are there</p><h2>${state.lo}°C to ${state.hi}°C</h2>
      <p class="muted">${weather ? `${count(pts)} in this range; the rest are grey on the map` : "Loading typical weather…"}</p>`;
  }
  $("#list").innerHTML = `<div class="chapter-head">${head}</div>` + rows(pts);
  $("#list").scrollTop = 0;
}
const count = (pts: Point[]) => `${pts.length} place${pts.length === 1 ? "" : "s"}`;

// ---------- drives between places ----------
const hm = (min: number) => min < 60 ? `${min} min` : `${Math.floor(min / 60)} h${min % 60 ? ` ${min % 60} min` : ""}`;
const kmText = (km: number) => `${Math.round(km).toLocaleString("en-GB")} km`;
function totals(ds: Drive[]) {
  const road = ds.filter((d) => d.mode === "road");
  const km = road.reduce((a, d) => a + (d.km ?? 0), 0), min = road.reduce((a, d) => a + (d.min ?? 0), 0);
  return km ? `${kmText(km)} · ${hm(min)} driving` : "";
}
/** The drives (and any ferry) from place a to the next place b, in route order; [] if b does not follow a. */
function drivesBetween(a: Point, b: Point): Drive[] {
  const i = trip.drives.findIndex((d) => d.from === a.id);
  if (i < 0) return [];
  const out: Drive[] = [];
  for (let j = i; j < trip.drives.length && j < i + 6; j++) {
    out.push(trip.drives[j]);
    if (trip.drives[j].to === b.id) return out;
    if (trip.drives[j].to) return []; // reached another place first
  }
  return [];
}
function driveRow(a: Point, b: Point) {
  const ds = drivesBetween(a, b);
  if (!ds.length) return "";
  const parts: string[] = [];
  const t = totals(ds);
  if (t) parts.push(t.replace(" driving", ""));
  const ferry = ds.find((d) => d.mode === "sea");
  if (ferry) parts.push(`ferry${ferry.ferry ? ` ${esc(ferry.ferry)}` : ""}`);
  const gap = b.day - a.day;
  if (gap === 1) parts.push("next day"); else if (gap > 1) parts.push(`${gap} days later`);
  return `<li class="drive" aria-hidden="true"><span>${parts.join(" · ")}</span></li>`;
}

function calendarGrid() {
  const [y, m] = state.month.split("-").map(Number);
  const first = new Date(y, m - 1, 1), days = new Date(y, m, 0).getDate();
  const lead = (first.getDay() + 6) % 7; // Monday first
  const byDay = new Map<number, Point[]>();
  for (const p of trip.points) {
    if (state.types.size && !state.types.has(kindOf(p))) continue;
    const d = dateOfPoint(p);
    if (monthKey(d) === state.month) byDay.set(d.getDate(), [...(byDay.get(d.getDate()) ?? []), p]);
  }
  const startMs = new Date(trip.start_date + "T12:00:00").getTime();
  const cells: string[] = Array.from({ length: lead }, () => `<span class="cell out"></span>`);
  for (let n = 1; n <= days; n++) {
    const tripDay = Math.round((new Date(y, m - 1, n, 12).getTime() - startMs) / 864e5);
    const pts = byDay.get(n) ?? [];
    const inTrip = tripDay >= 0 && tripDay <= trip.days;
    const thumbs = pts.slice(0, 2).map((p) => photos[p.id]?.[0]).filter(Boolean)
      .map((s) => `<img src="${s!.replace(/\.jpg$/, "-s.jpg")}" alt="" loading="lazy">`).join("");
    cells.push(`<button class="cell${pts.length ? " has" : ""}${inTrip ? "" : " out"}${state.day === tripDay ? " on" : ""}" data-day="${tripDay}"
      ${pts.length ? "" : "disabled"} aria-label="${n} ${monthName(state.month)}: ${pts.length} places">
      <span class="dn">${n}</span>${thumbs ? `<span class="th">${thumbs}</span>` : ""}${pts.length > 2 ? `<span class="more-n">+${pts.length - 2}</span>` : ""}
      ${pts.length ? `<span class="dots">${pts.map((p) => `<i style="background:${TYPE_COLOUR[kindOf(p)]}"></i>`).join("")}</span>` : ""}</button>`);
  }
  return `<div class="cal"><div class="wd">${["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d) => `<span>${d}</span>`).join("")}</div>
    <div class="grid">${cells.join("")}</div></div>`;
}

// ---------- map ----------
function tempColour(t: number) {
  const stops: [number, number[]][] = [[-5, [44, 123, 182]], [8, [171, 217, 233]], [16, [255, 255, 191]], [24, [253, 174, 97]], [32, [215, 25, 28]]];
  if (t <= stops[0][0]) return `rgb(${stops[0][1]})`;
  for (let i = 1; i < stops.length; i++) {
    const [t1, c1] = stops[i], [t0, c0] = stops[i - 1];
    if (t <= t1) { const f = (t - t0) / (t1 - t0); return `rgb(${c0.map((v, j) => Math.round(v + f * (c1[j] - v))).join(",")})`; }
  }
  return `rgb(${stops[stops.length - 1][1]})`;
}

function shownFeatures(): GeoJSON.FeatureCollection {
  return {
    type: "FeatureCollection",
    features: shown().map((p, i) => {
      const t = state.view === "temp" ? hiOf(p) : undefined;
      return {
        type: "Feature",
        properties: { id: p.id, n: i + 1, label: t !== undefined ? `${t}` : `${i + 1}`, colour: t !== undefined ? tempColour(t) : TYPE_COLOUR[kindOf(p)],
          text: t !== undefined && t < 26 && t > 4 ? "#1c1f21" : "#ffffff" },
        geometry: { type: "Point", coordinates: [p.lon, p.lat] },
      };
    }),
  };
}

async function initMap(route: GeoJSON.FeatureCollection) {
  setWorkerUrl(workerUrl);
  map = new MapLibre({
    container: "map", style: await siteStyle(),
    bounds: boundsOf(shown().length ? shown() : trip.points), fitBoundsOptions: { padding: 40 }, attributionControl: { compact: true },
  });
  map.addControl(new NavigationControl({ showCompass: false }), "top-right");
  map.on("load", () => {
    const all: GeoJSON.FeatureCollection = { type: "FeatureCollection", features: trip.points.map((p) => ({
      type: "Feature", properties: { id: p.id }, geometry: { type: "Point", coordinates: [p.lon, p.lat] } })) };
    map.addSource("route", { type: "geojson", data: route });
    map.addSource("all", { type: "geojson", data: all });
    map.addSource("points", { type: "geojson", data: shownFeatures(), promoteId: "id" });
    // the whole route faint; the part being looked at in its part colour (ochre 2027, blue 2028) on a white casing
    map.addLayer({ id: "route-all", type: "line", source: "route", layout: { "line-join": "round", "line-cap": "round" },
      paint: { "line-color": MAP.faint, "line-width": 2, "line-opacity": 0.7 },
      filter: ["==", ["get", "mode"], "road"] });
    map.addLayer({ id: "route-sea", type: "line", source: "route", paint: { "line-color": MAP.ferry, "line-width": 2, "line-dasharray": [2, 2] },
      filter: ["==", ["get", "mode"], "sea"] });
    map.addLayer({ id: "route-casing", type: "line", source: "route", layout: { "line-join": "round", "line-cap": "round" },
      paint: { "line-color": "#ffffff", "line-width": 7 }, filter: routeFilter() });
    map.addLayer({ id: "route-chapter", type: "line", source: "route", layout: { "line-join": "round", "line-cap": "round" },
      paint: { "line-color": ["case", ["<=", ["get", "chapter"], 8], MAP.ochre, MAP.blue], "line-width": 3.6 }, filter: routeFilter() });
    map.addLayer({ id: "route-km", type: "symbol", source: "route", minzoom: 7.5, // distance of each drive, when zoomed in
      filter: ["all", ["==", ["get", "mode"], "road"], [">=", ["coalesce", ["get", "km"], 0], 3]],
      layout: { "symbol-placement": "line-center", "text-field": ["concat", ["to-string", ["round", ["get", "km"]]], " km"],
        "text-font": ["Noto Sans Regular"], "text-size": 11 },
      paint: { "text-color": "#3A4652", "text-halo-color": MAP.land, "text-halo-width": 1.5 } });
    map.addLayer({ id: "points-all", type: "circle", source: "all", paint: { "circle-radius": 2.5, "circle-color": "#9aa0a4" } });
    map.addLayer({ id: "points", type: "circle", source: "points",
      layout: { "circle-sort-key": ["get", "n"] }, // same order as the labels, so each label sits on its own circle
      paint: {
        // small dots without labels when the whole trip is in view ("zoom" must be the outermost step)
        "circle-radius": ["step", ["zoom"],
          ["case", ["any", ["boolean", ["feature-state", "hover"], false], ["boolean", ["feature-state", "selected"], false]], 9, 5], 4.5,
          ["case", ["any", ["boolean", ["feature-state", "hover"], false], ["boolean", ["feature-state", "selected"], false]], 13, 9]],
        "circle-color": ["get", "colour"],
        "circle-stroke-color": ["case", ["boolean", ["feature-state", "hover"], false], MAP.ochre, ["boolean", ["feature-state", "selected"], false], MAP.blue, "#ffffff"],
        "circle-stroke-width": ["case", ["any", ["boolean", ["feature-state", "hover"], false], ["boolean", ["feature-state", "selected"], false]], 3, 1.5],
      } });
    map.addLayer({ id: "points-num", type: "symbol", source: "points",
      layout: { "text-field": ["get", "label"], "text-font": ["Noto Sans Bold"], "text-size": 10, "text-allow-overlap": true, "symbol-sort-key": ["get", "n"] },
      paint: { "text-color": ["get", "text"], "text-opacity": ["step", ["zoom"], 0, 4.5, 1] } });
    map.on("mousemove", "points", (e: MapLayerMouseEvent) => {
      const id = e.features?.[0]?.properties?.id as string | undefined;
      if (id) setHover(id, "map");
      map.getCanvas().style.cursor = "pointer";
    });
    map.on("mouseleave", "points", () => { setHover(null, "map"); map.getCanvas().style.cursor = ""; });
    map.on("click", "points", (e: MapLayerMouseEvent) => {
      const id = e.features?.[0]?.properties?.id as string | undefined;
      if (id) openPoint(id);
    });
    markers = new PhotoMarkers(map, photos, openPoint, (id) => setHover(id, "map"));
    mapReady = true;
    updateMap(false); // the view may have changed while the map was loading
  });
}

/** Which stretch of road is red: the chapter, the month or day, or the drives from the country's places. */
function routeFilter(): never {
  const road = ["==", ["get", "mode"], "road"];
  if (state.view === "chapter") return ["all", road, ["==", ["get", "chapter"], state.chapter]] as never;
  if (state.view === "calendar") {
    if (state.day !== null) return ["all", road, ["==", ["get", "day"], state.day]] as never;
    const days = trip.points.filter((p) => monthKey(dateOfPoint(p)) === state.month).map((p) => p.day);
    return ["all", road, [">=", ["get", "day"], Math.min(...days)], ["<=", ["get", "day"], Math.max(...days)]] as never;
  }
  if (state.view === "country") {
    const ids = trip.points.filter((p) => p.country === state.country).map((p) => p.id);
    return ["all", road, ["in", ["coalesce", ["get", "from"], ""], ["literal", ids]]] as never;
  }
  return road as never; // temperature: the whole route
}

function boundsOf(pts: Point[]) {
  const b = new LngLatBounds();
  for (const p of pts) b.extend([p.lon, p.lat]);
  return b;
}

function updateMap(animate = true) {
  if (!mapReady) return; // the load handler calls this again
  (map.getSource("points") as GeoJSONSource).setData(shownFeatures());
  // the chapter view uses round photo markers; the other views the numbered circles
  const photoView = state.view === "chapter";
  for (const id of ["points", "points-num"]) map.setLayoutProperty(id, "visibility", photoView ? "none" : "visible");
  if (photoView) {
    const all = trip.points.filter((p) => p.chapter === state.chapter);
    markers!.show(shown(), new Map(all.map((p, i) => [p.id, i + 1])));
    markers!.mark(selected, "sel");
  } else markers?.clear();
  map.setFilter("route-chapter", routeFilter());
  map.setFilter("route-casing", routeFilter());
  if (selected) map.setFeatureState({ source: "points", id: selected }, { selected: true });
  const sel = trip.points.find((x) => x.id === selected), pts = shown();
  if (sel) map.easeTo({ center: [sel.lon, sel.lat], duration: animate ? 600 : 0 });
  else if (pts.length) map.fitBounds(boundsOf(pts), { padding: mapPadding(), maxZoom: 11, duration: animate ? 800 : 0 });
}

/** On a phone the chapter list is a sheet over the bottom of the map: keep the places above it. */
function mapPadding() {
  const sheet = phone() && state.view === "chapter" ? $("#list").getBoundingClientRect().height : 0;
  const base = state.view === "chapter" ? 70 : 50;
  return sheet ? { top: 60, left: 40, right: 40, bottom: Math.min(sheet + 30, innerHeight * .7) } : base;
}
const phone = () => matchMedia("(max-width: 760px)").matches;

// ---------- phone: the chapter list as a bottom sheet (drag the handle or tap it) ----------
const SHEET = [0.2, 0.5, 0.86]; // share of the space below the header
function setupSheet() {
  const list = $("#list");
  let start: { y: number; h: number } | null = null;
  const room = () => list.parentElement!.getBoundingClientRect().height;
  const snap = (h: number) => {
    const r = room(), target = SHEET.reduce((a, b) => (Math.abs(b * r - h) < Math.abs(a * r - h) ? b : a));
    list.style.height = `${Math.round(target * 100)}%`;
    list.dataset.size = String(target);
  };
  list.addEventListener("pointerdown", (e) => {
    if (!phone() || !(e.target as HTMLElement).closest(".sheet-handle")) return;
    start = { y: e.clientY, h: list.getBoundingClientRect().height };
    list.setPointerCapture(e.pointerId); list.classList.add("dragging");
  });
  list.addEventListener("pointermove", (e) => {
    if (!start) return;
    list.style.height = `${Math.max(90, Math.min(room() * .92, start.h + start.y - e.clientY))}px`;
  });
  list.addEventListener("pointerup", (e) => {
    if (!start) return;
    const moved = Math.abs(e.clientY - start.y) > 6, h = list.getBoundingClientRect().height;
    list.classList.remove("dragging"); start = null;
    if (moved) snap(h);
    else { // a tap: next size up, from the largest back to the smallest
      const i = SHEET.indexOf(Number(list.dataset.size ?? 0.5));
      snap(SHEET[(i + 1) % SHEET.length] * room());
    }
  });
}

// ---------- hover: list row <-> map marker ----------
function setHover(id: string | null, from: "map" | "list") {
  if (id === hovered) return;
  if (hovered) {
    if (mapReady) map.setFeatureState({ source: "points", id: hovered }, { hover: false });
    document.querySelector(`.pt[data-p="${hovered}"]`)?.classList.remove("hover");
  }
  hovered = id;
  markers?.mark(id, "hover");
  if (!id) return;
  if (mapReady) map.setFeatureState({ source: "points", id }, { hover: true });
  const row = document.querySelector<HTMLElement>(`.pt[data-p="${id}"]`);
  row?.classList.add("hover");
  if (from === "map") row?.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

// ---------- the place panel ----------
function openPoint(id: string) {
  const p = trip.points.find((x) => x.id === id);
  if (!p) return;
  if (!shown().includes(p)) { // e.g. a link to a place: show the chapter it belongs to
    Object.assign(state, { view: "chapter", chapter: p.chapter });
    render();
    updateMap(false);
  }
  if (mapReady && selected && selected !== id) map.setFeatureState({ source: "points", id: selected }, { selected: false });
  selected = id;
  if (mapReady) map.setFeatureState({ source: "points", id }, { selected: true });
  markers?.mark(id, "sel");
  writeHash();
  document.querySelectorAll(".pt.selected").forEach((r) => r.classList.remove("selected"));
  document.querySelector(`.pt[data-p="${id}"]`)?.classList.add("selected");
  void panel.open(p);
  if (mapReady) map.easeTo({ center: [p.lon, p.lat], duration: 600 }); // otherwise the load handler centres it
}

function closePoint() {
  if (mapReady && selected) map.setFeatureState({ source: "points", id: selected }, { selected: false });
  const id = selected;
  selected = null;
  markers?.mark(null, "sel");
  panel.close();
  writeHash();
  document.querySelectorAll(".pt.selected").forEach((r) => r.classList.remove("selected"));
  document.querySelector<HTMLElement>(`.pt[data-p="${id}"]`)?.focus({ preventScroll: false });
}

function backLabel() {
  if (state.view === "chapter") { const c = trip.chapters.find((x) => x.id === state.chapter)!; return `Chapter ${c.id} · ${c.name}`; }
  if (state.view === "calendar") return state.day !== null ? fmtYear(dateOf(trip.start_date, state.day)) : monthName(state.month);
  if (state.view === "country") return state.country;
  return `${state.lo}–${state.hi}°C`;
}

// ---------- changing what is shown ----------
function render() {
  setHover(null, "list");
  const home = state.view === "home";
  document.body.classList.toggle("home", home);
  document.body.dataset.view = state.view;
  document.body.classList.remove("menu-open"); $("#menu-btn").setAttribute("aria-expanded", "false");
  $("#home").hidden = !home;
  renderHeader();
  if (home) {
    if (!$("#home").childElementCount) renderHome($("#home"), trip, photos, site, route);
    const target = section ? document.getElementById(section) : null;
    if (target) target.scrollIntoView({ behavior: "smooth" }); else window.scrollTo(0, 0);
  } else {
    renderList();
    if (mapReady) map.resize(); // the map was hidden behind the front page
  }
  writeHash();
}
function change(update: Partial<typeof state>) {
  if (selected) closePoint();
  Object.assign(state, update);
  render();
  updateMap();
}
async function needWeather() {
  if (weather) return;
  weather = (await loadExtras()).weather;
  if (state.view === "temp") { renderList(); updateMap(); }
  if (state.view === "chapter") renderList(); // typical temperature range
}

// ---------- start ----------
async function start() {
  const data = await loadAll();
  ({ trip, photos, site, route } = data);
  months = [...new Set(trip.points.map((p) => monthKey(dateOfPoint(p))))];
  countries = [...new Set(trip.points.map((p) => p.country).filter((k): k is string => !!k))];
  $("#start-label").textContent = `Start date: ${fmtYear(dateOf(trip.start_date, 0))}`;
  const first = readHash();
  panel = new Panel({
    trip, photos, route: data.route, typeLabel: (p) => TYPE_LABEL[kindOf(p)],
    siblings: () => shown(), backLabel, onClose: closePoint, onMove: openPoint,
  });
  render();
  void initMap(data.route);
  if (state.view === "temp" || state.view === "chapter") void needWeather();
  if (first) openPoint(first);

  $("#menu-btn").addEventListener("click", () => {
    const open = document.body.classList.toggle("menu-open");
    $("#menu-btn").setAttribute("aria-expanded", String(open));
  });
  setupSheet();
  $("#subnav").addEventListener("change", (e) => {
    const t = e.target as HTMLSelectElement;
    if (t.id === "chapter-select") change({ chapter: Number(t.value) });
  });
  $("#subnav").addEventListener("click", (e) => {
    const r = (e.target as HTMLElement).closest<HTMLElement>("button.round");
    if (r?.dataset.c) { change({ chapter: Number(r.dataset.c) }); return; }
    const b = (e.target as HTMLElement).closest<HTMLElement>(".chip");
    if (b?.dataset.c) change({ chapter: Number(b.dataset.c) });
    if (b?.dataset.m) change({ month: b.dataset.m, day: null });
    if (b?.dataset.k) change({ country: b.dataset.k });
  });
  $("#subnav").addEventListener("input", (e) => { // temperature sliders: update the labels while dragging
    const t = e.target as HTMLInputElement;
    if (t.id === "lo" || t.id === "hi") $(`#${t.id}-v`).textContent = `${t.value}°C`;
  });
  $("#subnav").addEventListener("change", (e) => {
    const t = e.target as HTMLInputElement;
    if (t.id !== "lo" && t.id !== "hi") return;
    const lo = Number($<HTMLInputElement>("#lo").value), hi = Number($<HTMLInputElement>("#hi").value);
    change({ lo: Math.min(lo, hi), hi: Math.max(lo, hi) });
  });
  $("#filters").addEventListener("click", (e) => {
    const t = (e.target as HTMLElement).closest<HTMLElement>(".filter")?.dataset.t;
    if (t === undefined) return;
    const types = new Set(state.types);
    if (t === "") types.clear(); else if (types.has(t)) types.delete(t); else types.add(t);
    change({ types });
  });
  const list = $("#list");
  list.addEventListener("mouseover", (e) => setHover((e.target as HTMLElement).closest<HTMLElement>(".pt")?.dataset.p ?? null, "list"));
  list.addEventListener("mouseleave", () => setHover(null, "list"));
  list.addEventListener("focusin", (e) => setHover((e.target as HTMLElement).closest<HTMLElement>(".pt")?.dataset.p ?? null, "list"));
  list.addEventListener("click", (e) => {
    const el = e.target as HTMLElement;
    const pill = el.closest<HTMLElement>(".pill");
    if (pill) {
      const t = pill.dataset.t ?? "", types = new Set(state.types);
      if (t === "") types.clear(); else if (types.has(t)) types.delete(t); else types.add(t);
      change({ types }); return;
    }
    const cell = el.closest<HTMLElement>(".cell.has");
    if (cell) { const d = Number(cell.dataset.day); change({ day: state.day === d ? null : d }); return; }
    if (el.closest("[data-act=month]")) { change({ day: null }); return; }
    const row = el.closest<HTMLElement>(".pt");
    if (row?.dataset.p) openPoint(row.dataset.p);
  });
  list.addEventListener("keydown", (e) => {
    const row = (e.target as HTMLElement).closest<HTMLElement>(".pt");
    if (row?.dataset.p && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); openPoint(row.dataset.p); }
  });
  window.addEventListener("hashchange", () => {
    const p = readHash();
    if (selected && p !== selected) closePoint();
    render(); updateMap();
    if (state.view === "temp" || state.view === "chapter") void needWeather();
    if (p && p !== selected) openPoint(p);
  });
}

start().catch((e) => {
  $("#list").innerHTML = `<p class="error">Could not load the trip data (${esc(String(e))}).</p>`;
});
