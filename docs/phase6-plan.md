# Phase 6: start date and festivals (plan)

Six steps, each shown in the local preview before it is committed.

1. Festival date rules and positions (this step)
2. The site works out on route / near miss / missed; festival lines come back on chapter pages
3. Start-date control (date and year); every date moves
4. Festivals view: all festivals in date order, with a map
5. Seasonal warnings for the chosen dates
6. Best start date: try a range of dates and years

## Step 1: one date rule per festival

Each of the 132 festivals in `pipeline/build_festivals.py` gets a position (lat, lon) and a date rule the
site can work out for any year. The kinds of rule, with an example from the list:

| Rule | Example | Written as |
|---|---|---|
| Fixed dates | Jaanipäev, 23–24 Jun | `fixed 06-23 06-24` |
| Weekday in a month | Východná, first weekend of July | `weekday 1st Fri of Jul, 3 days` |
| | Lights on the Lake, penultimate Saturday of July | `weekday 2nd-last Sat of Jul, 1 day` |
| Easter-based | Cádiz Carnival | `easter -52 -42` (days before / after Easter Sunday) |
| Islamic calendar | Ramadan, some moussems | `hijri 9-01, 30 days` |
| Announced for a year | Sziget 2027: 10–14 Aug | `dated 2027-08-10 2027-08-14`, plus a rule for other years |
| Estimated from past years | FOLIO, about 7–17 Oct | `about 10-07 10-17` (shown as "about") |
| Long season | Kraków Summer Jazz, late Jun – end Aug | `fixed 06-27 08-31` |
| Not by date | Douro grape harvest, big-wave contest | `none` (shown, never marked on route) |

Some only happen in some years: `odd years` (Villaviciosa), `every 5 years from 2028` (Laulupidu),
`2027 only` (Évora Capital of Culture, Santiago Holy Year).

Each festival keeps its source link and a "how sure" mark: confirmed, by rule, or estimated.

## How the site will judge each festival (step 2)

- **On route:** on a festival day the van is at a base within 30 km, or passes within 30 km on a moving day.
- **Near miss:** within 10 days of that, or on the dates but 30–100 km away.
- **Missed:** everything else.

The distances and the 10 days are settings that can be changed.
