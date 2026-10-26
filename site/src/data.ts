// Trip data, loaded at run time from the repository's data/ folder (see vite.config.ts).

export interface Chapter { id: number; part: string; name: string; start_day: number; end_day: number }
export interface Point {
  id: string; kind: "stop" | "highlight"; name: string; title?: string; caption: string;
  type?: "beach" | "nature" | "culture" | "history" | "peaceful";
  day: number; chapter: number; leg: string; lat: number; lon: number; wikipedia?: string; link: string;
}
export interface Trip { title: string; subtitle: string; start_date: string; days: number; chapters: Chapter[]; points: Point[] }
export type Photos = Record<string, string[]>;

async function json<T>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json() as Promise<T>;
}

export async function loadAll() {
  const [trip, photos, route] = await Promise.all([
    json<Trip>("data/trip.json"),
    json<Photos>("data/photos.json"),
    json<GeoJSON.FeatureCollection>("data/route-line.json"),
  ]);
  return { trip, photos, route };
}

/** Date of a trip day, worked out from the start date (never stored). */
export function dateOf(start: string, day: number): Date {
  const d = new Date(start + "T12:00:00");
  d.setDate(d.getDate() + day);
  return d;
}

export const fmtDay = (d: Date) => d.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" });
export const fmtYear = (d: Date) => d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
