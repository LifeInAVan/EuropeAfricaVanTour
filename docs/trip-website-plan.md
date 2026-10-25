# Trip website plan — Pärnu to Sahara

Oct 25, 2026 · @Peter

A static website built from the trip's existing route data, published on GitHub Pages, that shows 416 places and the festivals near them in 16 chapters. You can browse it by chapter, calendar, country or temperature, and changing the start date moves every day and checks each festival again.

## Chapters

Recommended: 16 chapters in two parts, each 12–38 points and two to six weeks long, splitting where the trip itself changes: a ferry, a border, a season or a stop at home.

What makes a good chapter here:

- **One readable map:** about 15–40 markers per summary map; above 50 the markers overlap at country scale.
- **Natural seams:** ferries (Greece–Italy, Sardinia–Barcelona, the Strait of Gibraltar, Tallinn–Helsinki), the winter base, and home time for Laulupidu.
- **One landscape or culture**, with a name someone who isn't on the trip would understand.
- **Similar length**, so moving from one chapter to the next feels like turning a page.

| Part | # | Chapter | Dates (current plan) | Countries | Points |
| --- | --- | --- | --- | --- | --- |
| One: south (2027) | 1 | Baltic departure | 19 – 25 Jul | Estonia, Latvia, Lithuania, Poland | 16 |
|  | 2 | Heart of Europe | 26 Jul – 7 Aug | Slovakia, Hungary, Slovenia | 12 |
|  | 3 | Dinaric wilds | 8 – 23 Aug | Slovenia, Croatia, Bosnia | 14 |
|  | 4 | Adriatic and Ionian | 24 Aug – 13 Sep | Montenegro, Albania, Greece | 25 |
|  | 5 | Puglia to Rome | 14 – 20 Sep | Italy | 14 |
|  | 6 | Pyrenees, the Vuelta and Green Spain | 21 Sep – 17 Oct | Spain, Portugal | 26 |
|  | 7 | Portugal | 18 Oct – 23 Nov | Portugal, Spain | 34 |
|  | 8 | Morocco: Atlas, Sahara, winter and Toubkal | 24 Nov 2027 – 12 Feb 2028 | Morocco | 38 |
| Two: home the long way (2028) | 9 | Al-Andalus and the Mediterranean | 13 Feb – 25 Mar | Morocco, Gibraltar, Spain, France | 38 |
|  | 10 | Provence | 26 Mar – 9 Apr | France | 32 |
|  | 11 | The Alps | 10 – 18 Apr | France, Switzerland | 17 |
|  | 12 | Rhine to the Oder | 19 Apr – 10 May | France, Germany | 32 |
|  | 13 | Poland's coast and lakes | 11 – 28 May | Germany, Poland | 21 |
|  | 14 | Baltic states and Laulupidu | 29 May – 11 Jul | Lithuania, Latvia, Estonia | 32 |
|  | 15 | Lapland and Arctic Norway | 12 – 29 Jul | Finland, Norway | 32 |
|  | 16 | Fjords and home | 30 Jul – 22 Aug | Norway, Sweden, Estonia | 33 |

Changes from the first draft: Morocco's two chapters merged (the winter base alone had only 11 points); Provence and the Alps split (49 points); the Baltic homecoming split at the Lithuanian border (53); the Midnight Sun split at Lofoten (65).

Alternatives:

- **Fewer (14):** also merge 1 with 2 ("Baltics to the Julian Alps", 28) and 3 with 4 ("The Balkans", 39). Fewer clicks, busier maps.
- **Country by country:** about 25 chapters. Simple, but Portugal, Spain and Morocco would each appear twice and some chapters would be only 3–4 days.

Festivals and events sit inside each chapter alongside the places (see Festivals).

## What each point shows

Every point opens a panel with five parts, all built in advance except the map tiles, so the site needs no paid services or API keys.

| Part | Source | How it is made | Notes |
| --- | --- | --- | --- |
| Feature photo | Wikipedia lead image (Wikimedia Commons), else Openverse | Already fetched by the film pipeline for 361 of 378 highlights; resized to about 1200 px | Credit and licence shown under every photo |
| Slideshow (3–6 photos) | Commons category of the place, plus Openverse | Fetched at build time, checked on a contact sheet before publishing | Commons rate-limits heavy use, so fetch slowly and cache |
| More information | Wikipedia article; OpenStreetMap where there is none; official site for festivals | Link stored per point | Same links as the highlights list |
| Local map | MapLibre GL with OpenFreeMap tiles | Zoomed to the point, route line drawn through it | OpenFreeMap: free, no key, no request limits |
| Weather at the scheduled date | Open-Meteo historical archive (ERA5, from 1940) | Typical daytime high, night low and chance of rain per point for every day of the year, worked out once and stored | Not a forecast; no key needed for non-commercial use |

Weather is stored by day of year, so changing the start date re-reads the stored values with no new downloads. A typical panel line: "Typical for 12 Sep: 24°C by day, 15°C at night, rain on 3 days in 10."

Rough size: 420 points × 5 photos × 150 KB is about 300 MB, inside GitHub Pages' 1 GB limit.

## Views

Four ways into the same points, sharing one set of filters (type: beach, nature, culture, history, peaceful, festival), so a filter set in one view carries into the others.

- **Chapter view (home):** chapter list across the top; summary map on the right with the route line and numbered markers; point list on the left. Hovering a list row highlights its marker and hovering a marker highlights its row. Clicking either opens the point panel. On a phone the map sits above the list.
- **Calendar view:** month grid or week list. Each day shows its points as small photo tiles, festivals marked. Clicking a day shows that day on the map.
- **Country view:** one chip per country with its point count and date span. Choosing a country zooms the map and filters the list.
- **Temperature view:** markers coloured by the typical daytime high on their scheduled date, with a slider to show only a range (for example 18–28°C). Points outside it are greyed rather than hidden, so gaps in the route stay visible.

The page address keeps the start date, view and filters, so a link you send opens on the same screen.

## Start date and fixed festivals

Every point is stored as a day number from departure (day 0 = leaving Pärnu), so changing the start date moves the whole trip; festivals keep their own dates and the site checks each one again.

Each festival has a date rule:

| Rule type | Example | How the date is found |
| --- | --- | --- |
| Fixed date | Greek panigiria, 15 August; Gitan pilgrimage, 24–25 May | Same date every year |
| Easter-based | Semana Santa; Feria de Abril (about two weeks after Easter) | Calculated from Easter for that year |
| Usual week | San Mateo, Logroño (around 21 September); Golegã Horse Fair (early November) | Approximate until the year's dates are published |
| Announced per year | La Vuelta stage towns (due December 2026); Laulupidu 2028 (30 June – 9 July) | Entered by hand; marked "not yet confirmed" until then |

For each festival the site compares its dates with the day the route passes that place and gives one of three results:

- **On route:** you are there during it.
- **Near miss:** you pass within 10 days; the site says how many days earlier or later to start to catch it.
- **Missed:** more than 10 days away.

Seasonal limits are checked the same way and shown as warnings: midnight sun at Nordkapp (ends about 29 July), Toubkal winter conditions (December to March; licensed guide compulsory), Morocco vehicle import (6 months per calendar year), and home dates for Laulupidu.

A later addition: tick the festivals you most want, and the site tries every start date within 60 days either side and shows which catch the most.

## Festivals

132 events on or near the route, from official sites and local news. Against the itinerary leaving on 19 Jul 2027: 50 on route, 34 near misses (within 10 days), 48 missed. The full list by chapter, with date rules and a source for every row, is in the Festivals tab.

What changes the plan:

- **Leaving on 19 Jul misses most of the 2027 summer festivals.** Pohoda, the Mostar diving, the Zagori feasts, the Diada and the Fátima procession all come before we arrive. We catch the last week of La Vuelta (22–26 Sep). The 2028 festivals are unchanged.
- **Laulupidu 2028 runs 30 Jun – 9 Jul.** It is the first joint edition (dance, then song); we are home in Pärnu 25 Jun – 11 Jul for all of it.
- **Tallinn Maritime Days has moved from late August to mid-July**, which fits the 11–12 Jul pass to the Helsinki ferry.
- **Ramadan is expected about 28 Jan – 27 Feb 2028:** the last two weeks at Tiznit and the drive north. Expect quieter days and changed opening hours.
- **Most 2027–28 dates are not announced.** Each row says whether a date is confirmed or worked out from the usual rule.

Departure moved to 19 Jul 2027 (decided 25 Oct 2026): every 2027 date is 24 days later; 2028 is unchanged.

- 400 days: leave Pärnu 19 Jul 2027, home for Laulupidu 25 Jun 2028, finish 22 Aug 2028.
- Toubkal moved to the end of the winter base (9–12 Feb 2028): a guided winter climb with crampons and ice axe; a licensed guide is compulsory. Marrakech dropped (already visited): from Ouzoud Falls the route crosses the Atlas by the Tizi n'Tichka to Telouet and Aït Benhaddou.
- Winter base at Tiznit 19 Dec – 7 Feb (7 weeks, was 9).
- For La Vuelta: Pärnu to Kraków direct via Warsaw; Sardinia and the Salento detour dropped; two days in Rome; Civitavecchia–Barcelona ferry (about 22 h) on 20 Sep; no stop in Barcelona. This catches the last week of the race (22–26 Sep), then the Pyrenees, Green Spain and Galicia. Spain, Portugal and Morocco are about 2 weeks earlier than the straight shift.
- Seasons: Albania and Greece late Aug – mid-Sep, northern Spain and Galicia late Sep – mid-Oct, Portugal late Oct – Nov, the Atlas and Sahara early December (snow possible on the high passes, cold desert nights).
- Dubrovnik added on 25 Aug for the last night of its Summer Festival (Ostrog moved to the day before Albania). Also: Zagori to 8 Sep (Nativity feast), Villaviciosa cider festival 8 Oct, Golegã 10–12 Nov then Marvão chestnut fair 13 Nov and Alcobaça sweets fair 18 Nov, Zagora and Rissani on market days. Cheap fixes still open: the San Sebastián Film Festival (2 days) and the Valley of Arts (3 days).

## How it is built

&#91;embedded content: how the site is built and served\]

Claude Code prepares the data, photos and weather on your computer; GitHub builds and hosts the site; the browser fetches only map tiles while you look. The site is plain TypeScript with MapLibre GL, built with Vite: no server and no database.

## Build plan

Seven phases, each small enough for one or two Claude Code sessions. The site is usable after phase 4, and each later phase adds to it.

1. **Repository and data:** create the GitHub repository, move in the existing film pipeline (route, highlights, road geometry, photos), and write one export script that produces the trip data: chapters, points as day numbers, and festivals with their date rules.
2. **Photos and credits:** add slideshow fetching (Commons categories, Openverse), a contact sheet for checking by eye, and resizing; credits stored with each photo.
3. **Weather:** download the climate history for each point once from Open-Meteo, slowly and cached, and store typical values by day of year.
4. **Chapter view:** summary map, point list with hover highlighting, and the point panel with photo, slideshow, link, local map and weather.
5. **Other views:** calendar, country and temperature views; shared filters; settings kept in the page address.
6. **Start date and festivals:** date picker, festival rules, on-route / near-miss / missed results, seasonal warnings, then the best-start-date search.
7. **Publish:** automatic build to GitHub Pages on every change; test on a phone, a laptop and the 3440×1440 monitor.

## Decisions for you

- [x] **Public or private:** decided: public site and repository on GitHub Free, with no home addresses.
- [x] **Your own photos:** decided: a few pictures of you, Dianne, Kalev and the van; everything else is places.
- [x] **Chapters:** decided: the recommended 16 in two parts.
- [x] **Festivals to track:** leaving 19 Jul 2027, the route catches 50 of the 132 researched (see Festivals).
- [x] **Weather period:** decided: the last 15 years.
- [x] **Site address:** decided: the free github.io address for now.

## Sources

- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api): ERA5 data from 1940; no key for non-commercial use
- [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits): 1 GB site, 100 GB a month bandwidth (soft limit)
- [What is GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages): public repositories on GitHub Free; private needs Pro or above
- [OpenFreeMap, described by Simon Willison](https://simonwillison.net/2024/Sep/28/openfreemap): free vector tiles for MapLibre, no key, no request limits
- Festivals: one source link per event in the Festivals tab
- Trip data: the route, the 378 highlights, road geometry and photo credits from the film pipeline, listed in daily-highlights.md
