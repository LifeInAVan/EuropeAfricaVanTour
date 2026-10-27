# Film: base camps (plan, not built yet)

Route change list 2 (27 Oct 2026) asks the film to "pause on each base and draw its day trips outward before
the van moves on". Nothing is rendered until Peter says so.

## What changes in `pipeline/render3.py`

1. **Route.** The van follows the base-to-base line in `cache/base_legs.json` (from `build_bases.py`), not the
   stop-to-stop line in `cache/plan.json`. The van no longer drives out to day-trip places, so the film shows
   the true van route: 26,895 km instead of 28,933.
2. **On the way.** Each on-the-way place is still a short hold on the line (as highlights are now, 17 frames),
   with its card and photo.
3. **At each base** (107 bases):
   - the van stops on the base; a filled circle grows to its size (by nights, as on the website map);
   - each day trip draws outward as a thin dashed line from the base to the place, coloured by how
     (green bike, blue train, grey walk), with the place card and photo for about 0.7 s each;
   - the date chip counts through the base's dates;
   - then the van moves on.
   Bases with no day trips get a short hold (about 0.5 s) so 107 stops do not drag.
4. **Main stops** (the 34 in `route.json`) keep their longer pause and postcard.
5. **Winter break.** At Málaga a "Van in storage, 20 Dec – 19 Feb" card replaces the drive; the date chip
   jumps to 19 Feb.
6. **Ferries.** As now (ship icon, dashed line), now nine crossings including Kiel–Klaipėda,
   Gryllefjord–Andenes and Moskenes–Bodø, taken from `base_legs.json`.
7. **End card.** The closing title is still "Pärnu → Sahara → Nordkapp" in the script (and `route.json` title);
   Nordkapp is no longer on the route. Proposed: "Pärnu → Sahara → Arctic", the same as the website strapline.

## Length

Now: 50 s of travel plus pauses. Adding 107 base holds and about 107 day-trip draws at the times above adds
roughly 2 minutes. To keep the film near its current length, the day-trip draws could be shortened to 0.4 s,
or shown only for bases of three nights or more (about 40 bases).

## Steps when approved

1. Read `cache/base_legs.json` and `data/bases.json` in `render3.py`, build the path per base move.
2. Add `base_pause(base)` drawing the circle and day-trip lines (Pillow, on the same map layer as the route).
3. Málaga storage card; end card text.
4. A 2-minute test render of chapters 1–3 (`TEST=` setting) for Peter to check before the full render.
