import { Map as MapLibre, LngLatBounds, NavigationControl, setWorkerUrl, type MapLayerMouseEvent } from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url"; // MapLibre 6 keeps its worker in a separate file
import "maplibre-gl/dist/maplibre-gl.css";
import "./style.css";
import { loadAll, dateOf, fmtDay, fmtYear, type Point, type Trip, type Photos } from "./data";

const TYPE_LABEL: Record<string, string> = {
  stop: "Main stop", beach: "Beach", nature: "Nature", culture: "Culture", history: "History", peaceful: "Peaceful",
};
const TYPE_COLOUR: Record<string, string> = {
  stop: "#1f2a30", beach: "#2a8fbd", nature: "#3d8a4a", culture: "#9b4fa8", history: "#b5652b", peaceful: "#5f7f8f",
};

const $ = <T extends HTMLElement>(sel: string) => document.querySelector(sel) as T;
let trip: Trip, photos: Photos, map: MapLibre;
let chapter = 1, hovered: string | null = null;

// ---------- page address: #c=3&p=point-id ----------
function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  const c = Number(h.get("c"));
  chapter = trip.chapters.some((x) => x.id === c) ? c : 1;
}
function writeHash() {
  history.replaceState(null, "", `#c=${chapter}`);
}

// ---------- chapters ----------
function renderChapters() {
  let part = "";
  $("#chapters").innerHTML = trip.chapters
    .map((c) => {
      const head = c.part !== part ? `<span class="part">${(part = c.part)}</span>` : "";
      const from = dateOf(trip.start_date, c.start_day), to = dateOf(trip.start_date, c.end_day);
      return `${head}<button class="chip" data-c="${c.id}" aria-pressed="${c.id === chapter}" title="${fmtYear(from)} – ${fmtYear(to)}">
        <b>${c.id}</b> ${c.name}</button>`;
    })
    .join("");
}

// ---------- point list ----------
const pointsOf = (c: number) => trip.points.filter((p) => p.chapter === c);
const kindOf = (p: Point) => (p.kind === "stop" ? "stop" : p.type ?? "culture");

function renderList() {
  const c = trip.chapters.find((x) => x.id === chapter)!;
  const pts = pointsOf(chapter);
  const from = dateOf(trip.start_date, c.start_day), to = dateOf(trip.start_date, c.end_day);
  $("#list").innerHTML = `
    <div class="chapter-head">
      <p class="eyebrow">Chapter ${c.id} · ${c.part}</p>
      <h2>${c.name}</h2>
      <p class="muted">${fmtYear(from)} – ${fmtYear(to)} · ${c.end_day - c.start_day + 1} days · ${pts.length} places</p>
    </div>
    <ol class="points">${pts
      .map((p, i) => {
        const thumb = photos[p.id]?.[0];
        const k = kindOf(p);
        return `<li class="pt ${p.kind}" data-p="${p.id}" tabindex="0">
          <span class="num" style="--c:${TYPE_COLOUR[k]}">${i + 1}</span>
          ${thumb ? `<img src="${thumb.replace(/\.jpg$/, "-s.jpg")}" alt="" loading="lazy">` : `<span class="noimg"></span>`}
          <span class="txt"><span class="name">${p.name}</span>
            <span class="meta">${fmtDay(dateOf(trip.start_date, p.day))} · ${TYPE_LABEL[k]}</span>
            <span class="cap">${p.caption}</span></span>
        </li>`;
      })
      .join("")}</ol>`;
  $("#list").scrollTop = 0;
}

// ---------- map ----------
function pointFeatures(): GeoJSON.FeatureCollection {
  return {
    type: "FeatureCollection",
    features: trip.points.map((p) => {
      const n = pointsOf(p.chapter).indexOf(p) + 1;
      return {
        type: "Feature",
        properties: { id: p.id, chapter: p.chapter, n, kind: kindOf(p), colour: TYPE_COLOUR[kindOf(p)] },
        geometry: { type: "Point", coordinates: [p.lon, p.lat] },
      };
    }),
  };
}

function initMap(route: GeoJSON.FeatureCollection) {
  setWorkerUrl(workerUrl);
  map = new MapLibre({
    container: "map",
    style: "https://tiles.openfreemap.org/styles/positron",
    bounds: chapterBounds(),
    fitBoundsOptions: { padding: 40 },
    attributionControl: { compact: true },
  });
  map.addControl(new NavigationControl({ showCompass: false }), "top-right");
  map.on("load", () => {
    map.addSource("route", { type: "geojson", data: route });
    map.addSource("points", { type: "geojson", data: pointFeatures(), promoteId: "id" });
    map.addLayer({ id: "route-all", type: "line", source: "route", paint: { "line-color": "#8a8f93", "line-width": 1.5, "line-opacity": 0.6 },
      filter: ["==", ["get", "mode"], "road"] });
    map.addLayer({ id: "route-sea", type: "line", source: "route", paint: { "line-color": "#4b7fa6", "line-width": 1.5, "line-dasharray": [2, 2] },
      filter: ["==", ["get", "mode"], "sea"] });
    map.addLayer({ id: "route-chapter", type: "line", source: "route", paint: { "line-color": "#c2412d", "line-width": 3 },
      filter: ["all", ["==", ["get", "mode"], "road"], ["==", ["get", "chapter"], chapter]] });
    map.addLayer({ id: "points-other", type: "circle", source: "points",
      paint: { "circle-radius": 2.5, "circle-color": "#8a8f93" }, filter: ["!=", ["get", "chapter"], chapter] });
    map.addLayer({ id: "points", type: "circle", source: "points", filter: ["==", ["get", "chapter"], chapter],
      layout: { "circle-sort-key": ["get", "n"] }, // same order as the numbers, so each label sits on its own circle
      paint: {
        "circle-radius": ["case", ["boolean", ["feature-state", "hover"], false], 13, 9],
        "circle-color": ["get", "colour"],
        "circle-stroke-color": ["case", ["boolean", ["feature-state", "hover"], false], "#ffd34d", "#ffffff"],
        "circle-stroke-width": ["case", ["boolean", ["feature-state", "hover"], false], 3, 1.5],
      } });
    map.addLayer({ id: "points-num", type: "symbol", source: "points", filter: ["==", ["get", "chapter"], chapter],
      layout: { "text-field": ["to-string", ["get", "n"]], "text-font": ["Noto Sans Bold"], "text-size": 10, "text-allow-overlap": true,
        "symbol-sort-key": ["get", "n"] },
      paint: { "text-color": "#ffffff" } });

    map.on("mousemove", "points", (e: MapLayerMouseEvent) => {
      const id = e.features?.[0]?.properties?.id as string | undefined;
      if (id) setHover(id, "map");
      map.getCanvas().style.cursor = "pointer";
    });
    map.on("mouseleave", "points", () => { setHover(null, "map"); map.getCanvas().style.cursor = ""; });
  });
}

function chapterBounds(): LngLatBounds {
  const b = new LngLatBounds();
  for (const p of pointsOf(chapter)) b.extend([p.lon, p.lat]);
  return b;
}

function showChapterOnMap() {
  if (!map.isStyleLoaded()) return;
  const f = ["==", ["get", "chapter"], chapter] as const;
  map.setFilter("points", f as never);
  map.setFilter("points-num", f as never);
  map.setFilter("points-other", ["!=", ["get", "chapter"], chapter]);
  map.setFilter("route-chapter", ["all", ["==", ["get", "mode"], "road"], ["==", ["get", "chapter"], chapter]]);
  map.fitBounds(chapterBounds(), { padding: 40, duration: 800 });
}

// ---------- hover: list row <-> map marker ----------
function setHover(id: string | null, from: "map" | "list") {
  if (id === hovered) return;
  if (hovered) {
    map.setFeatureState({ source: "points", id: hovered }, { hover: false });
    document.querySelector(`.pt[data-p="${hovered}"]`)?.classList.remove("hover");
  }
  hovered = id;
  if (!id) return;
  map.setFeatureState({ source: "points", id }, { hover: true });
  const row = document.querySelector<HTMLElement>(`.pt[data-p="${id}"]`);
  row?.classList.add("hover");
  if (from === "map") row?.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

function selectChapter(c: number) {
  if (c === chapter) return;
  setHover(null, "list");
  chapter = c;
  writeHash();
  renderChapters();
  renderList();
  showChapterOnMap();
  document.querySelector(`.chip[data-c="${c}"]`)?.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
}

// ---------- start ----------
async function start() {
  const data = await loadAll();
  ({ trip, photos } = data);
  $("#subtitle").textContent = `${fmtYear(dateOf(trip.start_date, 0))} – ${fmtYear(dateOf(trip.start_date, trip.days))} · ${trip.points.length} places in ${trip.chapters.length} chapters`;
  readHash();
  renderChapters();
  document.querySelector(`.chip[data-c="${chapter}"]`)?.scrollIntoView({ block: "nearest", inline: "center" });
  renderList();
  initMap(data.route);

  $("#chapters").addEventListener("click", (e) => {
    const b = (e.target as HTMLElement).closest<HTMLElement>(".chip");
    if (b) selectChapter(Number(b.dataset.c));
  });
  const list = $("#list");
  list.addEventListener("mouseover", (e) => {
    const row = (e.target as HTMLElement).closest<HTMLElement>(".pt");
    setHover(row?.dataset.p ?? null, "list");
  });
  list.addEventListener("mouseleave", () => setHover(null, "list"));
  list.addEventListener("focusin", (e) => setHover((e.target as HTMLElement).closest<HTMLElement>(".pt")?.dataset.p ?? null, "list"));
  window.addEventListener("hashchange", () => { const c = chapter; readHash(); const n = chapter; chapter = c; selectChapter(n); });
}

start().catch((e) => {
  $("#list").innerHTML = `<p class="error">Could not load the trip data (${String(e)}).</p>`;
});
