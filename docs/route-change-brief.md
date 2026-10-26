# Brief for the route and stop planning session

Paste this into the session where the route was researched.

---

I'd like your help planning changes to the route and stops. Please **don't edit any files**: the
route now lives in a GitHub repository (LifeInAVan/EuropeAfricaVanTour) that another Claude Code
session maintains. The files in OneDrive (`02 Trip film pipeline`) are an old copy and must not be
changed. Your job is to think it through with me and give me a **change list** that I take back to
that session, which edits the repository and rebuilds the website and film data.

## What has changed since you last saw it
- The start **year is not decided**. Work with day numbers and calendar dates; assume 19 July as the
  departure date for now (19 July 2027 behind the scenes). The website will get a start-date control
  later, so note anything that depends on the year (festivals held only in odd years, Easter-based
  dates, Ramadan, La Vuelta's route).
- Picos de Europa main stop moved to **Fuente Dé** (valley base, about 1,100 m).
- Captions: Pärnu is "Where we set off"; the Laulupidu stop is "Home for the Song Festival
  (Laulupidu)"; Camargue is "Spring — flamingos north".
- Every drive now has real road distance and driving time (38,692 km in total). Long single days
  stand out: Pärnu to Warsaw 842 km on day 1; Häme Castle to Rovaniemi 749 km; Lofotr to
  Kjerringøy 435 km (about 9 h). Car times; the LT31 will be slower.
- 16 chapters (unchanged). Festivals: 132 researched; with the current dates 49 on route, 34 near
  misses, 49 missed.

## How the route is stored (so the change list fits)
- **Main stops** (`data/route.json`): each has an id (e.g. `krakow`), name, caption, coordinates and
  the date we arrive. Ferries are listed between two stops (e.g. `igoumenitsa>matera`).
- **Places between stops** (`pipeline/highlights_src.py`): grouped by leg (`"krakow>tatras"`), in
  driving order, each as (English Wikipedia article title, short caption, type). Types: B beach,
  N nature, C culture, H history, P peaceful. A date pin can fix the day a group of places starts
  (used for festivals).

## Please give me the change list in this form
One line per change, grouped by chapter, in driving order:

- **Move stop**: `id` from date → new date (and why)
- **Add stop**: name, approximate location, arrival date, caption (max ~40 characters), after `id`
- **Remove stop**: `id` (and what happens to the places on its legs)
- **Add place**: exact English Wikipedia article title, caption (max ~40 characters), type letter,
  on leg `from>to`, between which two places, and a fixed date if it matters (festival)
- **Remove place**: Wikipedia title, leg
- **Change caption**: stop id or place title → new caption
- **Ferry**: add / change / remove, with ports and date

For each change, add one line on **why** (festival, season, distance, rest day). At the end, add:
- the **festivals** the changes catch or lose
- any **drive over about 400 km** in a day that remains, and whether that's intended
- anything that **depends on the start year**

Plain English, no marketing language. Captions are short and factual.
