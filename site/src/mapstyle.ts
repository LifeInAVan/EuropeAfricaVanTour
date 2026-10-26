// OpenFreeMap Positron, recoloured to the site's palette (design handoff): sand land, blue-grey water,
// quieter labels in English. Village and town labels and road names only on the local (place) map.
import type { StyleSpecification } from "maplibre-gl";

const STYLE_URL = "https://tiles.openfreemap.org/styles/positron";
export const MAP = {
  land: "#F2EFE7", water: "#BCD3DF", waterway: "#A9C4D3", park: "#E5E8DC", residential: "#ECE8DD",
  building: "#E6E1D6", label: "#555A5E", ochre: "#C8702A", blue: "#1D3B53", faint: "#A7ACAF", ferry: "#5B636B",
};
const ENGLISH = ["coalesce", ["get", "name:en"], ["get", "name_en"], ["get", "name"]];

let base: Promise<StyleSpecification> | null = null;

export async function siteStyle(local = false): Promise<StyleSpecification> {
  base ??= fetch(STYLE_URL).then((r) => r.json() as Promise<StyleSpecification>);
  const style = structuredClone(await base);
  for (const l of style.layers) {
    const paint = (l as { paint?: Record<string, unknown> }).paint ??= {};
    const layout = (l as { layout?: Record<string, unknown> }).layout ??= {};
    const id = l.id;
    if (id === "background") paint["background-color"] = MAP.land;
    else if (id === "water") paint["fill-color"] = MAP.water;
    else if (id === "waterway") paint["line-color"] = MAP.waterway;
    else if (id === "park" || id === "landcover_wood") paint["fill-color"] = MAP.park;
    else if (id === "landuse_residential") paint["fill-color"] = MAP.residential;
    else if (id === "building") paint["fill-color"] = MAP.building;
    if (l.type === "symbol") {
      if (!local && (/^label_(village|town|other)$/.test(id) || /^highway-(name|shield)|^road_shield/.test(id))) layout.visibility = "none";
      if ("text-color" in paint || /^label_|water_name/.test(id)) {
        paint["text-color"] = id.startsWith("water_name") ? "#4E6E82" : MAP.label;
        paint["text-halo-color"] = MAP.land;
      }
      if (/^label_(city|city_capital|country_\d|state)$/.test(id)) layout["text-field"] = ENGLISH;
    }
  }
  return style;
}
