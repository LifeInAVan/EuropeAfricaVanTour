# Redesign plan: Kalev's Grand Tour

From the design handoff (`03 Website design/handoff/HANDOFF.md` and its screens in the planning folder),
agreed with Peter on 26 Oct 2026. Each step is shown in the local preview before it is committed;
pushing only when Peter says.

## Kept
TypeScript, Vite, MapLibre, GitHub Pages; `data/route.json` and `data/trip.json`; routing, weather,
calendar, country and temperature logic; existing links (`#c=4`, `#c=4&p=kotor`, `#v=calendar&m=…`).
An empty address now opens the front page instead of chapter 1.

## Steps
1. **Look and header.** Colour tokens, Barlow Condensed and Inter (bundled with the site), logo,
   favicon (32 and 16 px), header and nav, start-date button (inactive until phase 6), map recoloured
   (sand land, blue water, quieter labels), route ochre for part one and blue for part two with a
   white casing, ferries dashed. Applied to every existing view.
2. **Front page.** Hero (Merzouga), numbers worked out from the data (38,692 km from the road route),
   "The plan" with the whole-route map and numbered chapter circles (backlog B), chapter cards in two
   parts, the van, the crew, other views, footer. Chapter covers and the hero photo kept in
   `data/chapters.json`, not in the page.
3. **Chapter page.** Chapter bar (previous/next, "Chapter 1 of 16" menu, 16-part bar sized by days),
   side panel (cover, dates, countries in order, typical temperature range, festivals on our dates
   from `festivals.json`, filter pills, places grouped by day), photo markers grouped when they
   overlap, other chapters' route faint.
4. **Place page.** Full page instead of the panel: slideshow, tags, "Day 6 · Saturday 24 July 2027",
   caption, short description (Wikipedia summary, credited and linked), weather card, local map with
   Wikipedia and OpenStreetMap links, "Same day" card, previous/next.
5. **Phone layouts.** Chapter page: map on top, list in a bottom sheet. Place page stacked. 390 px.
6. **Calendar, countries and temperature** in the new style; final checks at 390 and 1440 px,
   contrast, no console errors, GitHub build passes.

## Decisions (Peter, 26 Oct 2026)
- Number plates: blur the plates in our van photos already in the repository and commit the blurred
  versions (the old versions stay in git history).
- Place descriptions: opening sentences of each place's Wikipedia article, fetched once, credited
  "From Wikipedia" with a link (CC BY-SA).
- Fonts bundled with the site (no requests to Google).
- Desktop first, checked at phone width at every step; full phone pass in step 5.
- Screen day numbers start at Day 1; the data keeps day 0 as departure.
- Still open: the van paragraph and crew captions (Peter to write); whether driving times should be
  scaled for the van; backlog C (van marker, timeline) to be looked at again after step 3.
- Only photos of Peter and Dianne (and Kalev) among people; place photos showing other people as the
  subject to be dropped in review.
