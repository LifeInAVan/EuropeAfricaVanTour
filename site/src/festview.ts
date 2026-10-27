// The festivals view (phase 6): every festival in date order with its result for the chosen start date, and
// the festivals on the map coloured by result.
import { Popup, type Map as MapLibre, type MapLayerMouseEvent, type GeoJSONSource } from "maplibre-gl";
import { dateOf, fmtDate, type Trip } from "./data";
import type { Judged } from "./festivals";

const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);
export const STATUS: Record<string, { label: string; colour: string }> = {
  on: { label: "On route", colour: "#A85A1E" }, near: { label: "Near miss", colour: "#46748F" }, missed: { label: "Missed", colour: "#9AA0A4" },
};
const LAYERS = ["fest-circles"];

/** Festivals for the view: by date (those with no dates in the trip last), one filter at a time. */
export function festivalsShown(trip: Trip, filter: string) {
  const list = (trip.festivals ?? []) as Judged[];
  return list.map((f, i) => ({ f, i })).filter(({ f }) => !filter || f.status === filter)
    .sort((x, y) => (x.f.first ?? 1e6) - (y.f.first ?? 1e6) || x.i - y.i);
}

/** Status chips with counts, for the row under the header. */
export function festivalChips(trip: Trip, filter: string) {
  const list = trip.festivals ?? [];
  const n = (s: string) => list.filter((f) => f.status === s).length;
  return `<button class="chip" data-f="" aria-pressed="${!filter}">All <b>${list.length}</b></button>`
    + Object.entries(STATUS).map(([k, v]) => `<button class="chip" data-f="${k}" aria-pressed="${filter === k}">
      <i class="fest-dot" style="background:${v.colour}"></i>${v.label} <b>${n(k)}</b></button>`).join("");
}

/** The list: festivals grouped by the month of their dates during the trip. */
export function festivalList(trip: Trip, filter: string) {
  const items = festivalsShown(trip, filter);
  let month = "";
  const rows = items.map(({ f, i }) => {
    const m = f.first !== undefined ? dateOf(trip.start_date, Math.max(0, f.first)).toLocaleDateString("en-GB", { month: "long" }) : "Not dated during the trip";
    const head = m !== month ? `<li class="fest-month">${esc(m)}</li>` : "";
    month = m;
    const s = STATUS[f.status];
    return `${head}<li class="fest-item" data-i="${i}" tabindex="0">
      <span class="fest-badge" style="background:${s.colour}">${s.label}</span>
      <strong>${esc(f.event)}</strong>
      <span class="fest-place">${esc(f.place)}</span>
      <span class="fest-pass">${esc(f.our_pass)}</span>
      <a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.source)}</a></li>`;
  }).join("");
  return `<div class="ch-head"><p class="kicker">Festivals</p><h1>${filter ? STATUS[filter].label : "All festivals"}</h1>
    <p class="ch-facts">For a start on ${fmtDate(dateOf(trip.start_date, 0))} ${dateOf(trip.start_date, 0).getFullYear()}.
      On route: within 30 km on its dates. Near miss: within 10 days, or 30–100 km away. Change the start date at the top.</p></div>
    <ol class="fest-list">${rows || `<li class="empty-list">None.</li>`}</ol>`;
}

function features(trip: Trip): GeoJSON.FeatureCollection {
  const list = (trip.festivals ?? []) as Judged[];
  return { type: "FeatureCollection", features: list.flatMap((f, i) => (f.places ?? []).map((p): GeoJSON.Feature => ({
    type: "Feature", properties: { i, status: f.status, colour: STATUS[f.status].colour, order: f.status === "on" ? 3 : f.status === "near" ? 2 : 1 },
    geometry: { type: "Point", coordinates: [p.lon, p.lat] } }))) };
}

export function popupHtml(f: Judged) {
  const s = STATUS[f.status];
  return `<div class="bp"><h3>${esc(f.event)}</h3><p class="bp-dt">${esc(f.place)}</p>
    <p><span class="how" style="--c:${s.colour}">${s.label}</span> · ${esc(f.our_pass)}</p>
    <p class="bp-dt">Usually: ${esc(f.timing)}</p>
    <p><a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.source)}</a></p></div>`;
}

export class FestivalLayer {
  private popup = new Popup({ maxWidth: "300px", className: "base-popup" });
  constructor(private map: MapLibre, private trip: () => Trip, onPick: (i: number) => void) {
    map.addSource("festivals", { type: "geojson", data: features(trip()) });
    map.addLayer({ id: "fest-circles", type: "circle", source: "festivals", layout: { visibility: "none", "circle-sort-key": ["get", "order"] },
      paint: { "circle-radius": ["step", ["zoom"], 5, 5, 7], "circle-color": ["get", "colour"], "circle-stroke-color": "#ffffff", "circle-stroke-width": 1.5 } });
    map.on("click", "fest-circles", (e: MapLayerMouseEvent) => { const i = e.features?.[0]?.properties?.i; if (i !== undefined) onPick(Number(i)); });
    map.on("mouseenter", "fest-circles", () => { map.getCanvas().style.cursor = "pointer"; });
    map.on("mouseleave", "fest-circles", () => { map.getCanvas().style.cursor = ""; });
  }
  /** Show (with a filter) or hide; the data is refreshed because a new start date changes the results. */
  show(on: boolean, filter: string) {
    (this.map.getSource("festivals") as GeoJSONSource).setData(features(this.trip()));
    for (const id of LAYERS) {
      this.map.setLayoutProperty(id, "visibility", on ? "visible" : "none");
      this.map.setFilter(id, filter ? ["==", ["get", "status"], filter] : null);
    }
    this.popup.remove(); // a new filter or start date: the open festival may no longer be shown
  }
  open(i: number) {
    const f = (this.trip().festivals ?? [])[i] as Judged | undefined, p = f?.places?.[0];
    if (!f) return;
    if (p) { this.popup.setLngLat([p.lon, p.lat]).setHTML(popupHtml(f)).addTo(this.map); this.map.easeTo({ center: [p.lon, p.lat], duration: 600 }); }
    else this.popup.remove();
  }
  bounds(filter: string): [number, number][] {
    return ((this.trip().festivals ?? []) as Judged[]).filter((f) => !filter || f.status === filter).flatMap((f) => (f.places ?? []).map((p) => [p.lon, p.lat] as [number, number]));
  }
}
