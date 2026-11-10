"""Re-extract effective dates from document text.

The original parser took the first date near an effective-date phrase. Proclamations recite the
history of earlier rate changes using the same phrasing, so it often picked a date from years
earlier. Two rules fix almost all of it:

  1. an effective date cannot precede the announcement
  2. among the dates that survive, the operative one is the date the document repeats most often

Announcement dates are taken from the Federal Register signing_date where present, which is the
date the President actually signed, and from the publication date otherwise.
"""
import json, re, os
from collections import Counter
from datetime import datetime
import pandas as pd

CUE = re.compile(r"(effective|on or after|entered for consumption|withdrawn from warehouse|"
                 r"shall apply|takes effect|take effect)", re.I)
DATE = re.compile(r"\b([A-Z][a-z]+ \d{1,2}, \d{4})\b")

def parse(d):
    try: return datetime.strptime(d, "%B %d, %Y").date()
    except ValueError: return None

def effective_date(text, announced):
    """Dates appearing near an effective-date cue, filtered and ranked."""
    cands = []
    for m in DATE.finditer(text):
        window = text[max(0, m.start()-160):m.end()+60]
        if not CUE.search(window): continue
        d = parse(m.group(1))
        if d and (announced is None or d >= announced):
            cands.append(d)
    if not cands: return None, 0
    counts = Counter(cands)
    top = max(counts.values())
    best = min(d for d, n in counts.items() if n == top)   # most repeated, earliest on a tie
    return best, top

def main():
    idx = {x["document_number"]: x for x in json.load(open("events/fr_index.json"))}
    e = pd.read_csv("events/tariff_events.csv")

    rows = []
    for _, r in e.iterrows():
        meta = idx.get(r.document_number, {})
        ann = parse_iso(meta.get("signing_date") or meta.get("publication_date"))
        path = f"events/raw/{r.document_number}.txt"
        eff, hits = (None, 0)
        if ann and os.path.exists(path):
            eff, hits = effective_date(open(path, errors="ignore").read(), ann)
        rows.append(dict(document_number=r.document_number, authority=r.authority,
                         action_kind=r.action_kind,
                         announcement_date=ann, announcement_source=
                         "signing" if meta.get("signing_date") else "publication",
                         effective_date_old=r.effective_date,
                         effective_date=eff, mentions=hits,
                         window_days=(eff - ann).days if (eff and ann) else None))
    out = pd.DataFrame(rows)
    out.to_csv("events/tariff_events_dates.csv", index=False)

    old = pd.to_datetime(e.effective_date, errors="coerce")
    oann = pd.to_datetime(e.announcement_date, errors="coerce")
    print(f"{'':<34}{'before':>10}{'after':>10}")
    print(f"{'events with an effective date':<34}{old.notna().sum():>10}{out.effective_date.notna().sum():>10}")
    print(f"{'effective before announcement':<34}{int((old < oann).sum()):>10}"
          f"{int((pd.to_datetime(out.effective_date) < pd.to_datetime(out.announcement_date)).sum()):>10}")
    w_old = (old - oann).dt.days
    print(f"{'median window, days':<34}{w_old[w_old >= 0].median():>10.0f}"
          f"{out.window_days.median():>10.0f}")
    print(f"\nannouncement date source: "
          f"{(out.announcement_source=='signing').sum()} signing, "
          f"{(out.announcement_source=='publication').sum()} publication")
    w = out.window_days.dropna()
    print(f"\nwindow length distribution (n={len(w)}):")
    for lo, hi, lab in [(0,6,"0-6 days"),(7,20,"7-20 days"),(21,60,"21-60 days"),(61,9999,"61+ days")]:
        print(f"  {lab:<12}{int(w.between(lo,hi).sum()):>5}")
    al = out[out.document_number == "2025-02832"]
    if len(al):
        a = al.iloc[0]
        print(f"\naluminum proclamation: announced {a.announcement_date}, "
              f"effective {a.effective_date} (was {a.effective_date_old}), "
              f"window {a.window_days} days")

def parse_iso(s):
    if not s: return None
    try: return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError: return None

if __name__ == "__main__":
    main()
