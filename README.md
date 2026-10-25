# Pärnu to Sahara

Planning a 400-day campervan tour of Europe and North Africa: Pärnu, Estonia, 19 July 2027 to 22 August 2028, about 38,700 km. This repository holds the route data, the scripts that prepare it, and (from phase 4) the public trip website.

## Folders

- `data/` – shared by the website and the film pipeline.
  - `route.json` – stops, dates and ferries. The single source of truth for the route.
  - `festivals.json` – 132 festivals and events, with dates and how the route meets each one.
- `docs/` – the website plan, the festival list and the day-by-day highlights.
- `pipeline/` – Python scripts that build the trip data and render the trip film. See `pipeline/README.md`.
- `assets/` – place photos (Wikimedia Commons, Openverse) and a few of our own. Location and camera data are removed before photos are committed.

## Rebuild after changing the route

Needs Python 3 with Pillow and numpy, and ffmpeg for the film.

```
python pipeline/plan.py         # road geometry and dated highlights -> pipeline/cache/plan.json
python pipeline/make_doc.py     # -> docs/daily-highlights.md
python pipeline/render3.py      # the film (optional, about 100 MB, not committed)
```

`CLAUDE.md` has the project rules: tech choices, content rules and the build order.
