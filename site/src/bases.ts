// Base camps (route change list 2): the van moves base to base and stays 1-5 nights; nearby places are
// day trips on foot, by bike or by train. Map layers, the base popup, the van's place on a day, and the
// base bars on the timeline.
import { Popup, type Map as MapLibre, type MapLayerMouseEvent } from "maplibre-gl";
import { dateOf, fmtDate, type Base, type Trip } from "./data";
import { MAP } from "./mapstyle";
import { barShare } from "./chapter";

const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);
export const HOW_COLOUR: Record<string, string> = { bike: "#3d8a4a", train: "#2f63c7", walk: "#7d848a" };
const HOW_LABEL: Record<string, string> = { bike: "bike", train: "train", walk: "on foot" };
const BASE_LAYERS = ["base-trips", "base-trip-ends", "base-otw", "base-circles", "base-labels"];

/** Trip day of a date in the bases file (whose dates are for the planned start, whatever start is chosen). */
export const dayOfDate = (trip: Trip, s: string) =>
  Math.round((new Date(s + "T12:00:00").getTime() - new Date((trip.plan_start ?? trip.start_date) + "T12:00:00").getTime()) / 864e5);

/** Where the van is on a trip day: at a base from arrival to the morning it leaves; on a moving day at the
 *  last on-the-way place reached, or still at the base it left. */
export function vanPlace(trip: Trip, bases: Base[], day: number) {
  const i = Math.max(0, bases.findLastIndex((b) => dayOfDate(trip, b.arrive) <= day));
  const b = bases[i], next = bases[i + 1];
  if (!next || day <= dayOfDate(trip, b.leave)) return { lon: b.lon, lat: b.lat, eastward: !!next && next.lon > b.lon };
  const o = next.on_the_way.filter((w) => dayOfDate(trip, w.date) <= day).pop();
  const at = o ?? b;
  return { lon: at.lon, lat: at.lat, eastward: next.lon > at.lon };
}

/** Thin bars under the chapter bar, one for each base's nights, so the days without driving show. */
export function baseBars(trip: Trip, bases: Base[]) {
  const w = 100 / (trip.days + 1);
  return `<div class="base-bars" aria-hidden="true">${bases.filter((b) => b.nights > 0).map((b) => {
    const a = dayOfDate(trip, b.arrive);
    return `<i style="left:${barShare(trip, a)}%;width:${b.nights * w}%" title="${esc(b.name)}: ${b.nights} night${b.nights === 1 ? "" : "s"}"></i>`;
  }).join("")}</div>`;
}

function features(bases: Base[]) {
  const fc = (features: GeoJSON.Feature[]): GeoJSON.FeatureCollection => ({ type: "FeatureCollection", features });
  const pt = (lon: number, lat: number, properties: Record<string, unknown>): GeoJSON.Feature =>
    ({ type: "Feature", properties, geometry: { type: "Point", coordinates: [lon, lat] } });
  const trips = bases.flatMap((b) => b.places.filter((p) => p.how !== "base").map((p) => ({ b, p })));
  return {
    bases: fc(bases.map((b) => pt(b.lon, b.lat, { id: b.id, name: b.name, nights: b.nights, chapter: b.chapter }))),
    trips: fc(trips.map(({ b, p }): GeoJSON.Feature => ({ type: "Feature", properties: { how: p.how, chapter: b.chapter },
      geometry: { type: "LineString", coordinates: [[b.lon, b.lat], [p.lon, p.lat]] } }))),
    ends: fc(trips.map(({ b, p }) => pt(p.lon, p.lat, { how: p.how, chapter: b.chapter, title: p.title }))),
    otw: fc(bases.flatMap((b) => b.on_the_way.map((o) => pt(o.lon, o.lat, { chapter: b.chapter, title: o.title })))),
  };
}

/** The base popup: town, dates, nights, the drive there, ferry, station, day trips, campsites. */
function popupHtml(trip: Trip, b: Base, names: Map<string, string>) {
  const d = (s: string) => fmtDate(dateOf(trip.start_date, dayOfDate(trip, s)));
  const road = trip.drives.filter((x) => x.base === b.id && x.mode === "road");
  const km = road.length ? road.reduce((a, x) => a + (x.km ?? 0), 0) : b.drive_in_km ?? 0;
  const trips = b.places.filter((p) => p.how !== "base");
  const name = (t: string) => esc(names.get(t) ?? t);
  return `<div class="bp">
    <h3>${esc(b.name)}</h3>
    <p class="bp-dt">${b.nights ? `${d(b.arrive)} – ${d(b.leave)} · ${b.nights} night${b.nights === 1 ? "" : "s"}` : `${d(b.arrive)} · passing through`}</p>
    ${km ? `<p>${Math.round(km / 1.609344).toLocaleString("en-GB")} miles (${Math.round(km).toLocaleString("en-GB")} km) to get here${b.ferry_in ? `, with the ferry ${esc(b.ferry_in)}` : ""}</p>`
      : b.ferry_in ? `<p>Ferry ${esc(b.ferry_in)}</p>` : ""}
    ${b.station ? `<p>Station: ${esc(b.station)}</p>` : ""}
    ${trips.length ? `<p class="bp-h">Day trips</p><ul>${trips.map((p) =>
      `<li><span class="how" style="--c:${HOW_COLOUR[p.how]}">${HOW_LABEL[p.how]}</span> ${name(p.title)}, ${p.km} km</li>`).join("")}</ul>` : ""}
    ${b.on_the_way.length ? `<p class="bp-h">On the way here</p><p>${b.on_the_way.map((o) => name(o.title)).join(", ")}</p>` : ""}
    <p class="bp-h">Campsites</p>${b.campsites.length ? `<ul>${b.campsites.map((c) =>
      `<li>${c.src ? `<a href="${esc(c.src)}" target="_blank" rel="noopener">${esc(c.name)}</a>` : esc(c.name)}, ${c.km} km</li>`).join("")}</ul>` : "<p>To find</p>"}
  </div>`;
}

/** Adds the base layers (hidden until shown) and the popup on a click. names: place title -> name shown. */
export function addBaseLayers(map: MapLibre, trip: Trip, bases: Base[], names: Map<string, string>) {
  const f = features(bases);
  map.addSource("bases", { type: "geojson", data: f.bases });
  map.addSource("base-trips", { type: "geojson", data: f.trips });
  map.addSource("base-ends", { type: "geojson", data: f.ends });
  map.addSource("base-otw", { type: "geojson", data: f.otw });
  const hidden = { visibility: "none" as const };
  map.addLayer({ id: "base-trips", type: "line", source: "base-trips", layout: hidden,
    paint: { "line-color": ["match", ["get", "how"], "bike", HOW_COLOUR.bike, "train", HOW_COLOUR.train, HOW_COLOUR.walk],
      "line-width": 1.8, "line-dasharray": [2, 1.5] } });
  map.addLayer({ id: "base-trip-ends", type: "circle", source: "base-ends", layout: hidden,
    paint: { "circle-radius": 4, "circle-color": ["match", ["get", "how"], "bike", HOW_COLOUR.bike, "train", HOW_COLOUR.train, HOW_COLOUR.walk],
      "circle-stroke-color": "#ffffff", "circle-stroke-width": 1.5 } });
  map.addLayer({ id: "base-otw", type: "circle", source: "base-otw", layout: hidden,
    paint: { "circle-radius": 4, "circle-color": "#ffffff", "circle-stroke-color": MAP.blue, "circle-stroke-width": 2 } });
  map.addLayer({ id: "base-circles", type: "circle", source: "bases", layout: hidden,
    paint: { "circle-radius": ["min", 22, ["+", 5, ["*", 3, ["sqrt", ["get", "nights"]]]]], // area grows with the nights
      "circle-color": MAP.blue, "circle-opacity": 0.9, "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
  map.addLayer({ id: "base-labels", type: "symbol", source: "bases", minzoom: 5.5,
    layout: { ...hidden, "text-field": ["get", "name"], "text-font": ["Noto Sans Bold"], "text-size": 12, "text-offset": [0, 1.4], "text-anchor": "top" },
    paint: { "text-color": MAP.blue, "text-halo-color": "#ffffff", "text-halo-width": 1.5 } });
  const popup = new Popup({ maxWidth: "300px", className: "base-popup" });
  map.on("click", "base-circles", (e: MapLayerMouseEvent) => {
    const b = bases.find((x) => x.id === e.features?.[0]?.properties?.id);
    if (b) popup.setLngLat([b.lon, b.lat]).setHTML(popupHtml(trip, b, names)).addTo(map);
  });
  map.on("mouseenter", "base-circles", () => { map.getCanvas().style.cursor = "pointer"; });
  map.on("mouseleave", "base-circles", () => { map.getCanvas().style.cursor = ""; });
  return popup;
}

/** Shows the base layers for one chapter, or hides them (chapter null). */
export function showBases(map: MapLibre, chapter: number | null) {
  for (const id of BASE_LAYERS) {
    map.setLayoutProperty(id, "visibility", chapter === null ? "none" : "visible");
    if (chapter !== null) map.setFilter(id, ["==", ["get", "chapter"], chapter]);
  }
}

/** The map switch between photo markers and base camps, with the legend for base camps. */
export function layerSwitch(on: "photos" | "bases") {
  return `<div class="layer-switch" role="group" aria-label="Map shows">
      <button type="button" data-layer="photos" aria-pressed="${on === "photos"}">Photos</button>
      <button type="button" data-layer="bases" aria-pressed="${on === "bases"}">Base camps</button>
    </div>
    ${on === "bases" ? `<div class="base-legend">
      <span><i class="lg-base"></i>Base (size = nights)</span><span><i class="lg-otw"></i>On the way</span>
      ${(["walk", "bike", "train"] as const).map((h) => `<span><i class="lg-trip" style="--c:${HOW_COLOUR[h]}"></i>${h === "walk" ? "Walk" : h === "bike" ? "Bike" : "Train"}</span>`).join("")}
    </div>` : ""}`;
}
