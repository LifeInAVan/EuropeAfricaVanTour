// Trip data, loaded at run time from the repository's data/ folder (see vite.config.ts).

export interface Chapter { id: number; part: string; name: string; start_day: number; end_day: number; cover?: string; cover_photo?: number }
export interface Point {
  id: string; kind: "stop" | "highlight"; name: string; title?: string; caption: string;
  type?: "beach" | "nature" | "culture" | "history" | "peaceful";
  day: number; chapter: number; leg: string; lat: number; lon: number; wikipedia?: string; link: string; country?: string;
}
/** A drive (or ferry) between consecutive places; from/to are missing at a ferry port. */
export interface Drive { mode: "road" | "sea"; from?: string; to?: string; km?: number; min?: number; day: number; chapter: number; ferry?: string; base?: string }
/** A stretch of days not in any chapter (the winter break). */
export interface Break { name: string; start_day: number; end_day: number }
/** A base camp (data/bases.json): the van stays here; nearby places are day trips on foot, by bike or by train. */
export interface BasePlace { title: string; how: "base" | "walk" | "bike" | "train" | "on the way"; km: number; lon: number; lat: number; date: string }
export interface Base {
  id: string; name: string; center_place: string; station: string | null; lon: number; lat: number;
  arrive: string; leave: string; nights: number; chapter: number; ferry_in: string | null;
  campsites: { name: string; src: string | null; km: number }[];
  drive_in_km?: number; drive_days?: number; places: BasePlace[]; on_the_way: BasePlace[];
}
export interface Ferry { name: string }
export interface Festival { chapter: number; event: string; place: string; timing: string; dates: string; status: "on" | "near" | "missed"; our_pass: string; source: string; url: string }
export interface Trip {
  festivals?: Festival[];
  title: string; subtitle: string; start_date: string; days: number; chapters: Chapter[]; points: Point[];
  drives: Drive[]; ferries: Record<string, Ferry>; breaks?: Break[];
}
export type Photos = Record<string, string[]>;
/** Front-page words and photos (data/site.json). */
export interface Site {
  hero: { image: string; kicker: string; line: string; caption: string; credit_of: string };
  plan: { title: string; paragraphs: string[] };
  chapters_intro: string;
  van: { title: string; image: string; alt: string; specs: [string, string][]; text: string };
  crew: { name: string; text: string; image: string; alt: string }[];
  views: { name: string; view: string; text: string }[];
  footer: string[];
  bar_labels?: { chapter: number; text: string }[];
  kalev?: { title: string; text: string; photos: { image: string; alt: string }[] };
  van_page?: { history: string; photos: { image: string; alt: string }[] };
}

async function json<T>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json() as Promise<T>;
}

export async function loadAll() {
  const [trip, photos, route, site, bases] = await Promise.all([
    json<Trip>("data/trip.json"),
    json<Photos>("data/photos.json"),
    json<GeoJSON.FeatureCollection>("data/route-line.json"),
    json<Site>("data/site.json"),
    json<{ bases: Base[] }>("data/bases.json").then((b) => b.bases).catch(() => [] as Base[]),
  ]);
  return { trip, photos, route, site, bases };
}

export interface Credit { place?: string; artist?: string; license?: string; license_url?: string; source?: string; url?: string }
export interface Weather { source: string; years: string; points: Record<string, { elev: number; grid_elev: number; hi: number[]; lo: number[]; rain: number[] }> }

export interface Description { text: string; title: string; url: string }
let extras: Promise<{ credits: Record<string, Credit>; weather: Weather; descriptions: Record<string, Description> }> | null = null;
/** Photo credits, weather and descriptions (about 2 MB together): loaded the first time they are needed. */
export function loadExtras() {
  extras ??= Promise.all([
    json<Record<string, Credit>>("data/credits.json"),
    json<Weather>("data/weather.json"),
    json<{ places: Record<string, Description> }>("data/descriptions.json").catch(() => ({ places: {} })),
  ]).then(([credits, weather, d]) => ({ credits, weather, descriptions: d.places }));
  return extras;
}

/** Index into the weather arrays: day of the year as in a leap year (0 = 1 Jan, 59 = 29 Feb). */
export function weatherIndex(d: Date): number {
  return Math.round((Date.UTC(2028, d.getMonth(), d.getDate()) - Date.UTC(2028, 0, 1)) / 864e5);
}

/** Date of a trip day, worked out from the start date (never stored). */
export function dateOf(start: string, day: number): Date {
  const d = new Date(start + "T12:00:00");
  d.setDate(d.getDate() + day);
  return d;
}

// Dates are shown without year or weekday: the start year is not decided yet (Peter, 27 Oct 2026).
export const fmtDate = (d: Date) => d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
export const fmtLong = (d: Date) => d.toLocaleDateString("en-GB", { day: "numeric", month: "long" });
