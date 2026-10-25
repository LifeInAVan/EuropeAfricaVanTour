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
- `osrm_dist.py` – true road distances and driving times -> `cache/osrm_dist.json`
- `fetch_all.py`, `fetch_hl_images.py`, `add_new.py` – fetch highlight and stop photos and their credits
- `strip_metadata.py` – removes GPS, camera and other metadata from every photo in `assets/`, without
  re-compressing; `--check` lists any photo that still has some. Run it before committing photos.
- `build_credits.py` – `data/credits.json`: artist, licence and source for every photo, keyed by path
- `export.py` – `data/trip.json` for the website: chapters, points with fixed IDs and day numbers, festivals

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
