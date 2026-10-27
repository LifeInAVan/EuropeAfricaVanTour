// Festivals (phase 6): dates from each festival's rule for the trip's years, then on route / near miss /
// missed from where the van is each day. The rules are written in pipeline/festival_rules.py and the same
// logic is in pipeline/festival_dates.py (which checks them against the notes).
import { dateOf, fmtDate, type Base, type Festival, type Trip } from "./data";
import { dayOfDate } from "./bases";

export const SETTINGS = { onKm: 30, nearKm: 100, nearDays: 10 };
const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const DAY = 864e5;
type Range = [Date, Date];

const utc = (y: number, m: number, d: number) => new Date(Date.UTC(y, m - 1, d));
const add = (d: Date, n: number) => new Date(d.getTime() + n * DAY);
const wd = (d: Date) => (d.getUTCDay() + 6) % 7; // Monday 0
const md = (y: number, s: string) => utc(y, Number(s.slice(0, 2)), Number(s.slice(3)));

function easter(y: number) {
  const a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4;
  const g = Math.floor((8 * b + 13) / 25), h = (19 * a + b - d - g + 15) % 30, i = Math.floor(c / 4), k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 19 * l) / 433);
  const n = Math.floor((h + l - 7 * m + 90) / 25);
  return utc(y, n, (h + l - 7 * m + 33 * n + 19) % 32);
}
/** Tabular Islamic calendar (can be a day out from the sighted date). */
function hijri(hy: number, hm: number, hd: number) {
  const jd = Math.floor((11 * hy + 3) / 30) + 354 * hy + 30 * hm - Math.floor((hm - 1) / 2) + hd + 1948440 - 385;
  return new Date((jd - 2440588) * DAY); // Julian day 2440588 = 1 Jan 1970
}
function nthWeekday(y: number, m: number, w: number, n: number) {
  if (n > 0) { const f = utc(y, m, 1); return add(f, ((w - wd(f) + 7) % 7) + 7 * (n - 1)); }
  const last = add(utc(y, m + 1, 1), -1);
  return add(last, -((wd(last) - w + 7) % 7) - 7 * (-n - 1));
}
function isoWeekDay(y: number, week: number, w: number) {
  const jan4 = utc(y, 1, 4);
  return add(jan4, -wd(jan4) + 7 * (week - 1) + w);
}
function yearOk(limit: string, y: number) {
  const w = limit.split(/\s+/).filter(Boolean);
  if (!w.length) return true;
  if (w[0] === "odd") return y % 2 === 1;
  if (w[0] === "even") return y % 2 === 0;
  if (w[0] === "only") return y === Number(w[1]);
  if (w[0] === "every") return (y - Number(w[2])) % Number(w[1]) === 0;
  if (w[0] === "jul25sun") return wd(utc(y, 7, 25)) === 6;
  return true;
}
function one(r: string, y: number, placeDays?: string): Range[] {
  const w = r.split(/\s+/), k = w[0];
  if (k === "fixed" || k === "about") { const a = md(y, w[1]); return [[a, w[2] ? md(y, w[2]) : a]]; }
  if (k === "weekday") {
    const a = add(nthWeekday(y, Number(w[3]), DAYS.indexOf(w[2]), Number(w[1])), Number(w[5] ?? 0));
    return [[a, add(a, Number(w[4]) - 1)]];
  }
  if (k === "isoweek") { const a = isoWeekDay(y, Number(w[1]), DAYS.indexOf(w[2])); return [[a, add(a, Number(w[3]) - 1)]]; }
  if (k === "easter") { const e = easter(y); return [[add(e, Number(w[1])), add(e, Number(w[2]))]]; }
  if (k === "hijri") {
    return [y - 579, y - 578].map((hy) => hijri(hy, Number(w[1].slice(0, 2)), Number(w[1].slice(3))))
      .filter((a) => a.getUTCFullYear() === y).map((a) => [a, add(a, Number(w[2]) - 1)] as Range);
  }
  if (k === "weekly") {
    const days = new Set((w[1] === "*" ? placeDays ?? "" : w[1]).split(",").filter(Boolean).map((d) => DAYS.indexOf(d)));
    const out: Range[] = [];
    for (let d = utc(y, 1, 1); d.getUTCFullYear() === y; d = add(d, 1)) if (days.has(wd(d))) out.push([d, d]);
    return out;
  }
  return []; // none
}
/** The festival's dates in year y, and how sure: confirmed, rule or estimate. */
export function festivalDates(rule: string, y: number, placeDays?: string): { ranges: Range[]; sure: string | null } {
  const [bodyAll, limit = ""] = rule.split(";");
  if (!yearOk(limit, y)) return { ranges: [], sure: null };
  let body = bodyAll.trim();
  const guess = body.endsWith("~");
  body = body.replace(/~$/, "").trim();
  if (body.startsWith("dated")) {
    const [head, rest = ""] = body.split("|");
    const [, a, b] = head.trim().split(/\s+/);
    if (Number(a.slice(0, 4)) === y) return { ranges: [[new Date(a + "T00:00:00Z"), new Date(b + "T00:00:00Z")]], sure: "confirmed" };
    body = rest.trim();
  }
  const ranges = body.split(" + ").flatMap((p) => one(p.trim(), y, placeDays));
  return { ranges, sure: ranges.length ? (guess || body.startsWith("about") ? "estimate" : "rule") : null };
}

// ---------- where the van is each day ----------
interface Spot { lat: number; lon: number; name: string; country?: string; home?: boolean }
function km(a: { lat: number; lon: number }, b: { lat: number; lon: number }) {
  const r = Math.PI / 180, x = Math.sin(((b.lat - a.lat) * r) / 2) ** 2
    + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(((b.lon - a.lon) * r) / 2) ** 2;
  return 12742 * Math.asin(Math.sqrt(x));
}
const countryNear = (trip: Trip, lat: number, lon: number) =>
  trip.points.reduce((best, p) => (km(p, { lat, lon }) < km(best, { lat, lon }) ? p : best), trip.points[0]).country;
/** For each trip day: the base the van stays at, and the places passed on a moving day. Days of a break (the
 *  van in storage) have none. A long stay at home (the start town) counts for the whole country. */
function spotsByDay(trip: Trip, bases: Base[]) {
  const days: Spot[][] = Array.from({ length: trip.days + 1 }, () => []);
  const away = (d: number) => (trip.breaks ?? []).some((b) => d >= b.start_day && d <= b.end_day);
  for (const b of bases) {
    const country = countryNear(trip, b.lat, b.lon), home = b.name === trip.points[0].name && b.nights > 7;
    const name = b.name.split(" (")[0];
    for (let d = dayOfDate(trip, b.arrive); d <= dayOfDate(trip, b.leave); d++) if (!away(d)) days[d]?.push({ lat: b.lat, lon: b.lon, name, country, home });
    for (const o of b.on_the_way) days[dayOfDate(trip, o.date)]?.push({ lat: o.lat, lon: o.lon, name: o.title.split(/[,(]/)[0].trim(), country: countryNear(trip, o.lat, o.lon) });
  }
  return days;
}

export interface Judged extends Festival { first?: number; last?: number; sure?: string | null }

/** On route / near miss / missed for every festival, with a short "our pass" line; chapter from the matched day. */
export function judgeFestivals(trip: Trip, bases: Base[], list: Festival[]): Judged[] {
  if (!bases.length) return list;
  const spots = spotsByDay(trip, bases);
  const start = new Date(trip.start_date + "T00:00:00Z"), y0 = start.getUTCFullYear();
  const tripDay = (d: Date) => Math.round((d.getTime() - start.getTime()) / DAY);
  const chapterOf = (d: number) => trip.chapters.find((c) => d >= c.start_day && d <= c.end_day)?.id;
  const when = (d: number) => fmtDate(dateOf(trip.start_date, d));
  const seen = new Set<string>(); // the same festival listed in two chapters (midsummer): shown once
  return list.map((f): Judged => {
    const places = f.places?.map((p) => ({ ...p, ranges: [] as [number, number][] })) ?? [{ lat: 0, lon: 0, days: undefined, ranges: [] as [number, number][] }];
    let sure: string | null = null;
    for (const p of places)
      for (let y = y0; y <= y0 + 1; y++) {
        const r = festivalDates(f.rule ?? "none", y, p.days);
        sure ??= r.sure;
        p.ranges.push(...r.ranges.map(([a, b]) => [tripDay(a), tripDay(b)] as [number, number]));
      }
    const placeCountry = f.places?.length ? countryNear(trip, f.places[0].lat, f.places[0].lon) : f.country;
    const near = (s: Spot, p: { lat: number; lon: number }) => (f.country || s.home
      ? (s.country === (f.country ?? placeCountry) ? 0 : f.country ? Infinity : km(s, p)) : km(s, p));
    let best: { gap: number; dist: number; day: number; spot: Spot; range: [number, number] } | null = null;
    for (const p of places)
      for (const range of p.ranges) {
        const [a, b] = range;
        if (b < -SETTINGS.nearDays || a > trip.days + SETTINGS.nearDays) continue;
        for (let d = Math.max(0, a - SETTINGS.nearDays); d <= Math.min(trip.days, b + SETTINGS.nearDays); d++)
          for (const s of spots[d]) {
            const dist = near(s, p), gap = d < a ? a - d : d > b ? d - b : 0;
            if (dist > SETTINGS.nearKm || (gap && dist > SETTINGS.onKm)) continue;
            const score = (gap ? 1000 : 0) + gap * 10 + dist / 10; // on the dates first, then fewest days, then closest
            if (!best || score < (best.gap ? 1000 : 0) + best.gap * 10 + best.dist / 10) best = { gap, dist, day: d, spot: s, range };
          }
      }
    if (!best) return { ...f, status: "missed", our_pass: f.rule === "none" || !f.rule ? "Not on fixed dates" : "Not near our route on its dates", sure };
    const on = !best.gap && best.dist <= SETTINGS.onKm;
    const [a, b] = best.range;
    const dates = a === b ? when(a) : `${when(a)} – ${when(b)}`;
    const est = sure === "estimate" ? " (dates estimated)" : "";
    const pass = on ? `${dates}${est}: we are ${best.spot.home ? "at home in" : "at"} ${best.spot.name} on ${when(best.day)}`
      : best.gap ? `${dates}${est}: ${best.spot.name} on ${when(best.day)}, ${best.gap} day${best.gap === 1 ? "" : "s"} ${best.day < a ? "early" : "late"}`
      : `${dates}${est}: ${best.spot.name} on ${when(best.day)}, ${Math.round(best.dist)} km away`;
    return { ...f, status: on ? "on" : "near", our_pass: pass, chapter: chapterOf(best.day) ?? f.chapter, first: a, last: b, sure };
  }).filter((f) => {
    const key = `${f.event.split(" (")[0]}|${f.first ?? ""}`;
    if (f.first === undefined) return true;
    if (seen.has(key)) return false;
    seen.add(key); return true;
  });
}
