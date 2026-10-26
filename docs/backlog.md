# Backlog: ideas to plan and prioritise

Ideas collected during review. Not scheduled yet; each line notes what it would take.

## From Peter's review of the chapter view (26 Oct 2026)

1. **Route drawn as straight lines, not the roads taken.**
   The road geometry comes from the film pipeline, which asked OSRM for a *simplified* line
   (`overview=simplified` in `plan.py`) and thinned it again: about 3,800 points for 38,700 km,
   one every 10 km. Fix: fetch the full road geometry once (OSRM `overview=full`, cached separately
   so the film is unaffected), simplify it to about 50 m, and split it by chapter so each chapter
   loads only its own roads. Estimate: a few MB in total, about an hour of polite downloading.

2. **No map of the whole route.**
   Add a "Whole trip" view before chapter 1: every chapter's stretch in its own colour, labelled,
   with clicking a stretch opening that chapter. Main stops shown; highlights only from a closer zoom.

3. **Distance, driving time and dates for each segment.**
   `pipeline/osrm_dist.py` already works out true road distance and driving time for each
   stop-to-stop segment through its highlights; it has not been run since the 25 Oct route changes.
   Show per segment (e.g. "Kraków → Tatras · 23–26 Jul · 180 km · 3 h 40 min driving") in the list
   and as a label on the map, and totals per chapter and for the trip. Ferries listed separately.

4. **Using the van in the layout and map.** Ideas to choose from:
   - The van cut-out (`assets/_van_profile.png`) as the marker for the selected place, facing the
     direction of travel, instead of the plain dot.
   - A trip timeline bar (19 Jul 2027 – 22 Aug 2028) under the header with the van at the chosen
     day; dragging it moves through the trip and the map follows.
   - "Play the trip" on the whole-route map: the van drives the route with the date counting up,
     like the film.
   - The van as the site's logo and browser-tab icon.
   - A short "The van" page: the VW LT31 Westfalia Florida, with a few of our photos.

5. **Route for the places shown, in every view.** (Peter, 26 Oct 2026.) The calendar, country and
   temperature views drew no route or places on the live site: a map-style error, fixed the same
   day, and the whole route is now darker. Still to do: highlight in red the stretch of road for the
   month, day or country chosen, as the chapter view does for its chapter (needs the route split by
   day, which item 1's new road geometry can provide).

## Earlier notes
- The Pärnu start caption in `data/route.json` still says "Start — Jaanipäev, June 2027"
  (departure is now 19 July). The film pipeline shares that file, so ask before changing it.
- The Picos stop's coordinates are on a 2,416 m summit, so its typical weather is for the top.
