#!/usr/bin/env python3
"""Dates of a festival rule (festival_rules.py) in a given year: dates(rule, year) -> [(first, last), ...] and
how sure they are: "confirmed" (announced), "rule" (follows a fixed rule) or "estimate" (from past years).
The website has the same logic in site/src/festivals.ts; `python pipeline/festival_dates.py` checks every rule
and prints its 2027 and 2028 dates next to the notes in data/festivals.json."""
from datetime import date, timedelta

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def easter(y):
    """Easter Sunday (Gregorian), anonymous algorithm."""
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 19 * l) // 433
    n = (h + l - 7 * m + 90) // 25
    return date(y, n, (h + l - 7 * m + 33 * n + 19) % 32)

def hijri_to_date(hy, hm, hd):
    """Tabular Islamic calendar to Gregorian (can be a day out from the sighted date)."""
    jd = (11 * hy + 3) // 30 + 354 * hy + 30 * hm - (hm - 1) // 2 + hd + 1948440 - 385
    return date.fromordinal(jd - 1721425)

def nth_weekday(y, m, wd, n):
    if n > 0:
        d = date(y, m, 1); d += timedelta((wd - d.weekday()) % 7)
        return d + timedelta(7 * (n - 1))
    last = (date(y + (m == 12), m % 12 + 1, 1) - timedelta(1))
    return last - timedelta((last.weekday() - wd) % 7) - timedelta(7 * (-n - 1))

def md(y, s): return date(y, int(s[:2]), int(s[3:]))

def year_ok(limit, y):
    if not limit: return True
    w = limit.split()
    if w[0] == "odd": return y % 2 == 1
    if w[0] == "even": return y % 2 == 0
    if w[0] == "only": return y == int(w[1])
    if w[0] == "every": return (y - int(w[2])) % int(w[1]) == 0
    if w[0] == "jul25sun": return date(y, 7, 25).weekday() == 6
    raise ValueError(limit)

def one(r, y, place_days=None):
    w = r.split()
    k = w[0]
    if k in ("fixed", "about"):
        a = md(y, w[1]); b = md(y, w[2]) if len(w) > 2 else a
        return [(a, b)]
    if k == "weekday":
        n, wd, m, ln = int(w[1]), DAYS.index(w[2]), int(w[3]), int(w[4])
        a = nth_weekday(y, m, wd, n) + timedelta(int(w[5]) if len(w) > 5 else 0)
        return [(a, a + timedelta(ln - 1))]
    if k == "isoweek":
        a = date.fromisocalendar(y, int(w[1]), DAYS.index(w[2]) + 1)
        return [(a, a + timedelta(int(w[3]) - 1))]
    if k == "easter":
        e = easter(y); return [(e + timedelta(int(w[1])), e + timedelta(int(w[2])))]
    if k == "hijri":
        out = []
        for hy in (y - 579, y - 578):          # the Islamic year runs about 11 days shorter
            a = hijri_to_date(hy, int(w[1][:2]), int(w[1][3:]))
            if a.year == y: out.append((a, a + timedelta(int(w[2]) - 1)))
        return out
    if k == "weekly":
        days = {DAYS.index(d) for d in (place_days or "").split(",") if d} if w[1] == "*" else {DAYS.index(d) for d in w[1].split(",")}
        d, out = date(y, 1, 1), []
        while d.year == y:
            if d.weekday() in days: out.append((d, d))
            d += timedelta(1)
        return out
    if k == "none": return []
    raise ValueError(r)

def dates(rule, y, place_days=None):
    """[(first, last), ...] in year y, and how sure: confirmed, rule or estimate (None if no dates)."""
    body, _, limit = rule.partition(";")
    if not year_ok(limit.strip(), y): return [], None
    guess = body.strip().endswith("~")
    body = body.strip().rstrip("~").strip()
    if body.startswith("dated"):
        head, _, rest = body.partition("|")
        a, b = head.split()[1:3]
        if int(a[:4]) == y: return [(date.fromisoformat(a), date.fromisoformat(b))], "confirmed"
        body = rest.strip()
    out = [r for part in body.split(" + ") for r in one(part.strip(), y, place_days)]
    if not out: return [], None
    sure = "estimate" if guess or body.startswith("about") else "rule"
    return out, sure

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from festival_rules import R
    import json
    F = [(f["chapter"], f["event"], f["place"], f["timing"], f["dates"])
         for f in json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "festivals.json"), encoding="utf-8"))]
    keys = {(f[0], f[1]) for f in F}
    missing = [k for k in keys if k not in R]; extra = [k for k in R if k not in keys]
    print("festivals:", len(F), "rules:", len(R), "missing:", missing, "extra:", extra)
    fmt = lambda rs: "; ".join(a.strftime("%d %b") + ("" if a == b else "–" + b.strftime("%d %b")) for a, b in rs[:3]) + (" …" if len(rs) > 3 else "")
    for f in F:
        rule = R[(f[0], f[1])][0]
        line = []
        for y in (2027, 2028):
            rs, s = dates(rule, y, "Sat")
            line.append(f"{y}: {fmt(rs) or '-'} ({s or '-'})")
        print(f"{f[1][:38]:38} | {f[4][:44]:44} | {' | '.join(line)}")
