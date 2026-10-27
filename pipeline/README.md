# Pärnu → Sahara montage pipeline

`data/route.json` in, film out. Default output 1920×1080. Run from the repository root.

```
python pipeline/plan.py                      # road geometry + dated highlights -> cache/plan.json
python pipeline/make_doc.py                  # -> docs/daily-highlights.md
python pipeline/render3.py film_silent.mp4   # the film
python pipeline/music.py <duration_seconds>  # generated instrumental -> music.wav
ffmpeg -i film_silent.mp4 -i music.wav -c:v copy -c:a aac -shortest film.mp4
```

Films and `music.wav` are not committed.

## Scripts
- `plan.py` – routes every stop-to-stop segment through its highlights; writes `cache/plan.json`
- `highlights_src.py` – the places between stops, with date pins for festivals
- `make_doc.py` – day-by-day highlights list
- `render3.py`, `music.py` – the film and its music
- `build_festivals.py` – `data/festivals.json` and `docs/festivals.md`
- `festival_rules.py` – the date rule and place of each festival; `festival_dates.py` works out the dates for any
  year and, run on its own, lists every rule's 2027 and 2028 dates; `fetch_festival_places.py` – map positions
- `osrm_dist.py` – true road distances and driving times -> `cache/osrm_dist.json`
- `fetch_all.py`, `fetch_hl_images.py`, `add_new.py` – fetch highlight and stop photos and their credits
- `strip_metadata.py` – removes GPS, camera and other metadata from every photo in `assets/`, without
  re-compressing; `--check` lists any photo that still has some. Run it before committing photos.
- `build_credits.py` – `data/credits.json`: artist, licence and source for every photo, keyed by path
- `export.py` – `data/trip.json` for the website: chapters, points with fixed IDs and day numbers, festivals
- `build_bases.py` – the van's route base to base (`data/bases.json`) -> `cache/base_legs.json`; export.py uses it
  for the drives and the route line

## Slideshow photos (website)
1. `python pipeline/fetch_slides.py` – up to 10 candidates per point from Wikipedia, Commons and Openverse,
   with 330 px previews in `cache/slides/` (not committed). About 70 minutes; resumes if stopped.
2. `python pipeline/review_photos.py`, then open http://localhost:8765 – choose photos per chapter;
   saves `data/photo_picks.json`.
3. `python pipeline/make_web_photos.py` – 1200 px copies and 400 px thumbnails in `assets/web/<point>/`,
   `data/photos.json` and `assets/web/credits.json`; then run `build_credits.py`.

## Data
- `../data/route.json` – legs (colours), stops (id, lat/lon, date, caption), `ferries` keyed `fromId>toId`
  with port coordinates and sea waypoints (so sailings never cross land)
- `cache/hl_info.json` – coordinates and sources for each highlight
- `cache/road_cache.json` – road-following geometry from OSRM; new segments are fetched automatically
- `cache/basemap.json`, `cache/roads.json` – Natural Earth coastlines/borders and road network

## Pictures
- `assets/_hl/<hash>.jpg` + `credits.json` – highlight photos
- `assets/_sights/<stop>.jpg` + `credits.json` – Wikimedia Commons location photos (shown as postcards, credited at the end)
- `assets/<stop>/` – our photos; they drift across the top while the van travels
- `assets/_van_profile.png` – cut-out of the van, points along the road
- `assets/_title/`, `assets/_end/` – title and end card backgrounds

## Changing the route
Edit `data/route.json` (stops, dates, ferries) and/or `highlights_src.py` (places between stops), then
run from the repository root, in this order:
1. `python pipeline/plan.py` – plan and film road geometry (`cache/plan.json`)
2. `python pipeline/make_doc.py` – `docs/daily-highlights.md`
3. `python pipeline/export.py` – `data/trip.json` (new place IDs appear here)
4. `python pipeline/fetch_roads.py` then `python pipeline/export.py` again – real roads, km and times
4b. Update `data/bases.json` (bases, nights, day trips), then `python pipeline/build_bases.py` and `export.py` –
   the van's base-to-base route, which the site shows
5. `python pipeline/fetch_countries.py`, `fetch_weather.py`, `fetch_descriptions.py` – new places only (cached)
6. `python pipeline/fetch_slides.py`, review on `review_photos.py`, then `make_web_photos.py --suggested`
   and `build_credits.py` – photos for new places
7. Update the festival "our pass" results in `build_festivals.py` and run it (until phase 6 works these out)
8. `python pipeline/export.py` once more, check the site in the preview, commit, push when Peter says
