"""Attach product and partner scope to each tariff event, then flag treated panel cells.

Scope is resolved by three routes, in order of reliability:
  1. the event cites a 9903 code that exists in the current schedule  -> use its coverage
  2. the event is Section 232, which names a material class           -> use the chapter rule
  3. the event is IEEPA, which is country-wide                        -> every chapter the partner ships

Route 1 fails for older Section 232 actions because the schedule has since renumbered those
headings, which is why route 2 exists.

Outputs
  coverage/event_scope.csv    one row per event and chapter, with partner scope and dates
  coverage/treated_cells.csv  one row per chapter, partner and month that sits inside a window
"""
import re
import pandas as pd

# Section 232 names a material. Map the material words to the chapters that carry them.
MATERIAL = [
    (r"\baluminum\b",                      ["76"]),
    (r"\bsteel\b|\biron\b",                ["72", "73"]),
    (r"\bcopper\b",                        ["74"]),
    (r"\bautomobile|\bvehicle|\blight truck|\bpassenger vehicle", ["87"]),
    (r"\btimber|\blumber|\bfurniture",     ["44", "94"]),
    (r"\bsemiconductor",                   ["85"]),
    (r"\bsolar|\bphotovoltaic",            ["85"]),
    (r"\bpharmaceutical",                  ["30"]),
]

def material_chapters(text):
    out = []
    for rx, chs in MATERIAL:
        if re.search(rx, text or "", re.I):
            out += [c for c in chs if c not in out]
    return out

def main():
    e   = pd.read_csv("events/tariff_events.csv")
    cov = pd.read_csv("coverage/coverage_final.csv", dtype={"chapter": str})
    by_code = {h: g for h, g in cov.groupby("htsno")}

    rows = []
    for _, ev in e.iterrows():
        codes = sorted(set(re.findall(r"9903\.\d{2}\.\d{2}", str(ev.hts_codes) or "")))
        chapters, partners, route = [], [], None

        hits = [by_code[c] for c in codes if c in by_code]
        if hits:
            g = pd.concat(hits)
            if (g.chapter == "ALL").any():
                chapters, route = ["ALL"], "code -> country-wide"
            else:
                chapters = sorted(set(g.chapter)); route = "code -> enumerated"
            partners = sorted({p for s in g.countries.dropna() for p in str(s).split(";") if p})

        if not chapters and ev.authority == "SECTION_232":
            chapters = material_chapters(f"{ev.title} {ev.get('notes','')}")
            route = "material class" if chapters else None

        if not chapters and ev.authority == "IEEPA":
            chapters, route = ["ALL"], "IEEPA country-wide"

        if not partners and isinstance(ev.partners, str):
            partners = [p.strip() for p in ev.partners.split(";")
                        if p.strip() and not p.startswith("EXCEPT:")]

        for ch in (chapters or [None]):
            rows.append(dict(document_number=ev.document_number, authority=ev.authority,
                             action_kind=ev.action_kind, announcement_date=ev.announcement_date,
                             effective_date=ev.effective_date, chapter=ch,
                             partners=";".join(partners), route=route))

    s = pd.DataFrame(rows)
    s.to_csv("coverage/event_scope.csv", index=False)

    scoped = s[s.chapter.notna()]
    print(f"events                     {len(e)}")
    print(f"events with resolved scope {scoped.document_number.nunique()}")
    print(f"event x chapter rows       {len(scoped):,}\n")
    print("how scope was resolved:")
    print(scoped.drop_duplicates("document_number").route.value_counts().to_string())
    print("\nby authority:")
    print(scoped.groupby("authority").document_number.nunique().to_string())
    unresolved = set(e.document_number) - set(scoped.document_number)
    print(f"\nstill unresolved: {len(unresolved)}")

if __name__ == "__main__":
    main()
