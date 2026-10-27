// The front page: hero, numbers, the plan with the whole-route map, chapter cards, the van, the crew,
// other ways into the trip, footer. Words come from data/site.json; everything else from trip.json.
import { Map as MapLibre, LngLatBounds, Marker } from "maplibre-gl";
import { siteStyle, MAP } from "./mapstyle";
import { dateOf, loadExtras, type Chapter, type Photos, type Point, type Site, type Trip } from "./data";

const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);
const short = (d: Date) => d.toLocaleDateString("en-GB", { day: "numeric", month: "short" }); // no year: not decided
const partColour = (c: Chapter) => (c.id <= 8 ? MAP.ochre : MAP.blue);
/** "One: south (2027)" -> "Part one: south (2027)". */
export const partName = (part: string) => `Part ${part.charAt(0).toLowerCase()}${part.slice(1)}`;

/** "19 – 25 Jul", "24 Nov – 12 Feb". */
export function span(start: string, a: number, b: number) {
  const x = dateOf(start, a), y = dateOf(start, b);
  return x.getMonth() === y.getMonth() && b - a < 31 ? `${x.getDate()} – ${short(y)}` : `${short(x)} – ${short(y)}`;
}
/** Countries in the order reached, each once. */
export function countriesInOrder(pts: Point[]) {
  return [...new Set([...pts].sort((a, b) => a.day - b.day).map((p) => p.country).filter((k): k is string => !!k))];
}
export function coverOf(c: Chapter, photos: Photos) {
  const list = c.cover ? photos[c.cover] ?? [] : [];
  return list[c.cover_photo ?? 0] ?? list[0];
}

export function renderHome(el: HTMLElement, trip: Trip, photos: Photos, site: Site, route: GeoJSON.FeatureCollection) {
  const km = trip.drives.filter((d) => d.mode === "road").reduce((a, d) => a + (d.km ?? 0), 0);
  const countries = countriesInOrder(trip.points);
  const start = dateOf(trip.start_date, 0);
  const breakDays = (trip.breaks ?? []).reduce((a, b) => a + b.end_day - b.start_day + 1, 0); // e.g. home for the winter
  const stats: [string, string][] = [
    [String(trip.days + 1 - breakDays), "days on the road"],
    [Math.round(km).toLocaleString("en-GB"), "km of driving"],
    [String(countries.length), "countries"],
    [String(trip.points.length), "places to see"],
    [String(trip.chapters.length), "chapters"],
    [short(start), `leave ${esc(trip.points[0].name)}`],
  ];
  const parts = [...new Set(trip.chapters.map((c) => c.part))];
  const fill = (t: string) => t.replace("{countries}", String(countries.length))
    .replace("{festivals}", String(trip.festivals?.length ?? 0));

  el.innerHTML = `
  <section class="hero" style="background-image:url('${site.hero.image}')">
    <div class="hero-in">
      <img class="hero-badge" src="./logo-badge.png" width="320" height="320"
        alt="Kalev's Grand Tour badge: our VW LT31 camper and Kalev the Samoyed on orange dunes, with the words Pärnu, Sahara, Arctic">
      <p class="hero-kicker">${esc(site.hero.kicker)}</p>
      <h1>Kalev's<br>Grand Tour</h1>
      <p class="hero-line">${esc(site.hero.line)}</p>
      <div class="hero-buttons">
        <a class="btn" href="#v=home&s=route">See the route</a>
        <a class="btn ghost" href="#v=home&s=crew">Meet the crew</a>
      </div>
    </div>
    <p class="hero-credit" id="hero-credit">${esc(site.hero.caption)}</p>
  </section>
  <div class="stats-wrap"><div class="stats">${stats.map(([v, l]) => `<div><b>${v}</b><span>${l}</span></div>`).join("")}</div></div>

  <section class="sect plan" id="route">
    <div class="plan-text">
      <p class="kicker">The plan</p>
      <h2>${esc(site.plan.title)}</h2>
      ${site.plan.paragraphs.map((p) => `<p>${p}</p>`).join("")}
      <ul class="legend-box">
        <li><i class="ln" style="background:${MAP.ochre}"></i>${esc(partName(parts[0] ?? "One"))} · chapters 1–8</li>
        <li><i class="ln" style="background:${MAP.blue}"></i>${esc(partName(parts[1] ?? "Two"))} · chapters 9–16</li>
        <li><i class="ln dash"></i>Ferry crossing</li>
        <li><i class="dot"></i>${esc(trip.points[0].name)}: start and finish</li>
      </ul>
    </div>
    <figure class="plan-map">
      <div id="home-map" role="region" aria-label="Map of the whole route with the 16 chapters numbered"></div>
      <figcaption>Click a number to open that chapter. Map © OpenStreetMap contributors, OpenFreeMap.</figcaption>
    </figure>
  </section>

  <section class="sect" id="chapters">
    <p class="kicker">${trip.chapters.length} chapters</p>
    <h2>The trip, one stretch at a time</h2>
    <p class="intro">${esc(site.chapters_intro)}</p>
    ${parts.map((part) => {
      const cs = trip.chapters.filter((c) => c.part === part);
      return `<div class="part-group">
        <h3><i style="background:${partColour(cs[0])}"></i>${esc(partName(part))}</h3>
        <div class="cards">${cs.map((c) => {
          const pts = trip.points.filter((p) => p.chapter === c.id), img = coverOf(c, photos);
          return `<a class="card" href="#c=${c.id}">
            <span class="card-img" style="${img ? `background-image:url('${img}')` : ""}"><span class="badge" style="border-color:${partColour(c)}">${c.id}</span></span>
            <span class="card-body"><span class="card-name">${esc(c.name)}</span>
              <span class="card-dates">${span(trip.start_date, c.start_day, c.end_day)}</span>
              <span class="card-meta">${c.end_day - c.start_day + 1} days · ${pts.length} places</span>
              <span class="card-meta">${countriesInOrder(pts).map(esc).join(", ")}</span></span></a>`;
        }).join("")}</div></div>`;
    }).join("")}
  </section>

  <section class="van" id="van">
    <div class="sect van-in">
      <img src="${site.van.image}" alt="${esc(site.van.alt)}" loading="lazy">
      <div>
        <p class="kicker light">The van</p>
        <h2>${esc(site.van.title)}</h2>
        <dl>${site.van.specs.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>
        ${site.van.text ? `<p>${esc(site.van.text)}</p>` : ""}
        <a class="btn" href="#v=van">More about the van</a>
      </div>
    </div>
    <div class="sect crew" id="crew">
      <h2>The crew</h2>
      <div class="crew-cards">${site.crew.map((c) => `<figure><img src="${c.image}" alt="${esc(c.alt)}" loading="lazy">
        <figcaption><strong>${esc(c.name)}</strong><span>${esc(c.text)}</span></figcaption></figure>`).join("")}</div>
    </div>
  </section>
  ${site.kalev ? `<section class="sect kalev" id="kalev">
    <p class="kicker">The crew</p>
    <h2>${esc(site.kalev.title)}</h2>
    <p class="intro">${esc(site.kalev.text)}</p>
    <div class="kalev-grid">${site.kalev.photos.map((p) => `<img src="${p.image}" alt="${esc(p.alt)}" loading="lazy">`).join("")}</div>
  </section>` : ""}

  <section class="sect" id="views-cards">
    <h2>Other ways to look at the trip</h2>
    <div class="view-cards">${site.views.map((v) => v.view
      ? `<a class="view-card" href="#v=${v.view}"><b>${esc(v.name)}</b><span>${esc(fill(v.text))}</span></a>`
      : `<div class="view-card later"><b>${esc(v.name)}</b><span>${esc(fill(v.text))}</span></div>`).join("")}</div>
  </section>

  <footer class="foot"><div class="sect foot-in">${site.footer.map((f) => `<p>${esc(f.replace("{years}", "2011–2025"))}</p>`).join("")}</div></footer>`;

  void loadExtras().then(({ credits }) => { // hero photo credit
    const c = credits[site.hero.credit_of];
    if (c) document.getElementById("hero-credit")!.textContent = `${site.hero.caption} · Photo: ${c.artist}, ${c.license}`;
  });
  void homeMap(trip, route);
}

let homeMapObj: MapLibre | null = null;
async function homeMap(trip: Trip, route: GeoJSON.FeatureCollection) {
  homeMapObj?.remove();
  const box = document.getElementById("home-map")!;
  const all = new LngLatBounds();
  for (const p of trip.points) all.extend([p.lon, p.lat]);
  const map = (homeMapObj = new MapLibre({
    container: box, style: await siteStyle(), bounds: all, fitBoundsOptions: { padding: 30 },
    attributionControl: { compact: true }, cooperativeGestures: true,
  }));
  map.on("load", () => {
    map.resize(); // the page may have reflowed (fonts, images) since the map was created
    map.fitBounds(all, { padding: 30, duration: 0 });
    map.addSource("route", { type: "geojson", data: route });
    map.addLayer({ id: "sea", type: "line", source: "route", filter: ["==", ["get", "mode"], "sea"],
      paint: { "line-color": MAP.ferry, "line-width": 1.5, "line-dasharray": [2, 2] } });
    map.addLayer({ id: "casing", type: "line", source: "route", filter: ["==", ["get", "mode"], "road"],
      layout: { "line-join": "round", "line-cap": "round" }, paint: { "line-color": "#ffffff", "line-width": 5 } });
    map.addLayer({ id: "road", type: "line", source: "route", filter: ["==", ["get", "mode"], "road"],
      layout: { "line-join": "round", "line-cap": "round" },
      paint: { "line-color": ["case", ["<=", ["get", "chapter"], 8], MAP.ochre, MAP.blue], "line-width": 2.6 } });
  });
  // numbered chapter circles at the middle place of each chapter; a dark dot at the start
  for (const c of trip.chapters) {
    const pts = trip.points.filter((p) => p.chapter === c.id);
    // a chapter with no new places (home for Laulupidu): where the van is at its start
    const mid = pts[Math.floor(pts.length / 2)] ?? trip.points.findLast((p) => p.day <= c.start_day);
    if (!mid) continue;
    const a = document.createElement("a");
    a.className = "ch-marker"; a.href = `#c=${c.id}`; a.textContent = String(c.id);
    a.style.borderColor = partColour(c); a.title = `Chapter ${c.id}: ${c.name}`; a.setAttribute("aria-label", a.title);
    new Marker({ element: a }).setLngLat([mid.lon, mid.lat]).addTo(map);
  }
  const s = document.createElement("span"); s.className = "start-dot"; s.title = trip.points[0].name;
  new Marker({ element: s }).setLngLat([trip.points[0].lon, trip.points[0].lat]).addTo(map);
}
