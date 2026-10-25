# Pärnu to Sahara — trip website

Public, interactive website for Peter and Dianne Ferry's 400-day, ~38,700 km camper tour of Europe and North Africa (with their dog Kalev, in a VW LT31 Westfalia Florida). Earliest departure: Pärnu, Estonia, 19 July 2027.

## Owner
- Peter Ferry — not a programmer. Explain changes in plain English, one short paragraph.
- Plain English and engineering terms only. No marketing language on the site or in replies.

## Tech choices
- TypeScript, built with Vite. No other framework unless agreed.
- Maps: MapLibre GL JS with free tile sources only, no API key (e.g. OpenFreeMap, based on OpenStreetMap).
- Hosted on GitHub Pages at the free lifeinavan.github.io address. GitHub Actions builds and publishes the site on every push to `main`.
- Data preparation (route export, photos, weather) is done by scripts run on Peter's computer; the results are committed as files. The live site has no server and no database.
- Weather: Open-Meteo historical data for the last 15 years, downloaded once and cached; store typical values by day of year. Label as "typical weather", not a forecast.
- No paid services or API keys without asking first.
- A failed build is fixed before any other work. The live site keeps the previous version until then.

## Data
- `data/route.json` is the single source of truth for the route. It is shared with the trip montage pipeline — do not change its structure without asking.
- Every page is generated from the data at run time; never hard-code places or dates in HTML.
- All dates are calculated as offsets from a start date, so a changed start date moves everything.

## Features (build in this order)
1. Chapters: the trip split into chapters (legs). Each chapter lists points: cultural sites, beauty spots, festivals/events.
2. Summary map: whole route; hovering a point (or chapter) highlights it on the map and in the list.
3. Point page/panel: feature picture, slideshow, link to more info, local map, typical weather at the scheduled time.
4. Views: by calendar (week / month), by country, by temperature.
5. Start-date control: user changes the start date; the site recalculates every date and flags which fixed-date festivals are caught or missed.

## Content rules
- Photos are mainly places. A few of Peter and Dianne are allowed.
- Public site: no home addresses, no live location, no phone numbers or emails.
- Remove all location (GPS) and camera data from every photo before it is committed. Some of Peter's photos were taken at home.
- Image credits and licences recorded in `data/credits.json`; only use images we are allowed to publish.

## Working rules
- Plan first; make small changes; show me the result in a local preview before committing.
- Commit after each working step with a clear message. Push only when I say so.
- Must work on phone and desktop.
