# Backlog: ideas to plan and prioritise

Ideas collected during review, with what each would take. Order agreed with Peter on 26 Oct 2026.

## Done

**A. Real roads, distances and the route for what is shown (items 1, 3 and 5 together).**
One download serves all three: OSRM's full road route for every leg between places gives the
road-following line, the distance and the driving time of each leg.
- *1. Route drawn as straight lines.* The film pipeline asked OSRM for a simplified line
  (`overview=simplified` in `plan.py`) and thinned it again: about 3,800 points for 38,700 km.
  Fetch the full geometry once, cached separately so the film is unaffected, and simplify it to
  about 50 m. About an hour of polite downloading; a few MB of data.
- *3. Distance, driving time and dates for each segment.* Show per leg in the list
  ("Kraków → Tatras · 23–26 Jul · 180 km · 3 h 40 min") and as a label on the map, with totals per
  chapter and for the trip; ferries listed separately. (`osrm_dist.py` did this for stop-to-stop
  segments; the new download replaces it.)
- *5. Route for the places shown, in every view.* Split the route by day so the calendar, country and
  temperature views can draw the stretch for their month, day or country in red, as the chapter
  view does. (The bug that hid the route and places in those views was fixed on 26 Oct.)
- With it, two fixes to `data/route.json` (agreed 26 Oct; the film uses the same file):
  - Pärnu start caption → "Start — departure, 19 July 2027" (was "Start — Jaanipäev, June 2027").
  - Picos de Europa stop moved from a 2,416 m summit to Fuente Dé (about 1,100 m), so its pin and
    typical weather are for the valley base.

**B. Whole-trip map (item 2).** Done in the redesign: the whole-route map on the front page. A "Whole trip" chip before chapter 1: every chapter's stretch in its
own colour and labelled; clicking a stretch opens that chapter. Main stops shown; other places from
a closer zoom.

## Next

**C. The van (item 4).** Chosen by Peter (to look at again after the redesign):
- The van cut-out (`assets/_van_profile.png`) as the marker for the place that is open, facing the
  direction of travel.
- A trip timeline under the header (19 Jul 2027 – 22 Aug 2028) with the van at the chosen day;
  dragging it moves through the trip and the map and list follow.

**D. Pictures of Kalev and the van on the front page.** (Peter, 27 Oct 2026.) Today the van photo is
in "The van" section and Kalev has one card under "The crew", both well down the page. Ways to give
them more room, to choose from:
- Kalev and the van in the hero: our own photo of them instead of (or in turn with) the Merzouga dunes.
- The round logo badge (van and Kalev) beside the title in the hero.
- A small gallery in "The van" and "The crew": several of our photos of the van and of Kalev
  (spare Kalev photo already in the handoff: `kalev-beach.jpg`), plates blurred, no metadata.
- Needs: which photos Peter wants used.

## Not chosen for now
- The van as the site's logo and browser-tab icon.
- "Play the trip": the van driving the route on the whole-trip map, like the film.
- A short "The van" page.
