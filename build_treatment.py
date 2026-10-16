"""Resolve each tariff event to the panel cells it actually treats.

Three mechanisms, because the orders are written three different ways, and they do not
carry the same amount of dilution:

  ENUMERATED     the order lists HS8 subheadings. Exact match, no dilution.
  COUNTRY_WIDE   IEEPA hits everything from a partner. Also exact: every product from
                 that origin is treated, so there is no product dilution either.
  MATERIAL_CLASS Section 232 names a material, not a list. Resolved to chapters, so this
                 is the one group that still carries dilution and is reported separately.

Dates come from events/tariff_events_dates.csv, which corrected 17 impossible effective
dates. The announcement-to-effective window is the period a rush could happen in.

Outputs
  events_resolved.csv   one row per event x partner, with mechanism and dates
  event_products.csv    one row per enumerated event x HS8 line

Usage:  python3 build_treatment.py
"""
import re
import pandas as pd

# the schedule writes partner names in prose; the panel uses Schedule C codes.
# "South" is a comma-split artifact of "South Korea", confirmed against the text of
# 9903.02.79/.80 and 9903.94.60/.61, which all read "product of South Korea".
NAME2CTY = {
    "Argentina": "3570", "Bangladesh": "5380", "Brazil": "3510", "Cambodia": "5550",
    "Canada": "1220", "China": "5700", "Ecuador": "3310", "El Salvador": "2110",
    "Guatemala": "2050", "Indonesia": "5600", "Japan": "5880", "Jordan": "5110",
    "Liechtenstein": "4411", "Malaysia": "5570", "Mexico": "2010", "South": "5800",
    "South Korea": "5800", "Korea": "5800", "Switzerland": "4419", "Taiwan": "5830",
    "India": "5330", "Vietnam": "5520", "Russia": "4621", "South Africa": "7910",
}

MATERIAL = [
    (r"\baluminum\b", ["76"]), (r"\bsteel\b|\biron\b", ["72", "73"]),
    (r"\bcopper\b", ["74"]), (r"\bautomobile|\bvehicle|\blight truck|\bpassenger vehicle", ["87"]),
    (r"\btimber|\blumber|\bfurniture", ["44", "94"]), (r"\bsemiconductor", ["85"]),
    (r"\bsolar|\bphotovoltaic", ["85"]), (r"\bpharmaceutical", ["30"]),
]


def to_cty(names):
    out = []
    for n in names:
        n = (n or "").strip().rstrip(",.")
        c = NAME2CTY.get(n)
        if c and c not in out:
            out.append(c)
    return out


def main():
    ev = pd.read_csv("events/tariff_events.csv")
    dates = pd.read_csv("events/tariff_events_dates.csv")[
        ["document_number", "announcement_date", "effective_date", "window_days"]]
    ev = ev.drop(columns=["announcement_date", "effective_date"]).merge(
        dates, on="document_number", how="left")

    pl = pd.read_csv("coverage/product_lines.csv", dtype=str)
    lines_by_code = {h: set(g.hs8) for h, g in pl.groupby("htsno")}
    ctys_by_code = {h: (g.countries.dropna().iloc[0] if g.countries.notna().any() else "")
                    for h, g in pl.groupby("htsno")}

    res, prods = [], []
    for _, e in ev.iterrows():
        codes = sorted(set(re.findall(r"9903\.\d{2}\.\d{2}", str(e.hts_codes))))
        hs8 = set().union(*[lines_by_code[c] for c in codes if c in lines_by_code]) \
            if any(c in lines_by_code for c in codes) else set()

        names = []
        for c in codes:
            names += [x for x in str(ctys_by_code.get(c, "")).split(";") if x]
        if isinstance(e.partners, str):
            names += [p.strip() for p in e.partners.split(";")
                      if p.strip() and not p.startswith("EXCEPT:")]
        ctys = to_cty(names)

        if hs8:
            mech, chapters = "ENUMERATED", sorted({x[:2] for x in hs8})
        elif e.authority == "IEEPA":
            mech, chapters = "COUNTRY_WIDE", []
        elif e.authority == "SECTION_232":
            chapters = []
            for rx, chs in MATERIAL:
                if re.search(rx, f"{e.title} {e.get('notes','')}" or "", re.I):
                    chapters += [c for c in chs if c not in chapters]
            mech = "MATERIAL_CLASS" if chapters else None
        else:
            mech, chapters = None, []

        if mech is None or not ctys:
            continue
        for cty in ctys:
            res.append(dict(document_number=e.document_number, authority=e.authority,
                            action_kind=e.action_kind, mechanism=mech, cty=cty,
                            chapters=";".join(chapters), n_hs8=len(hs8),
                            announcement_date=e.announcement_date,
                            effective_date=e.effective_date, window_days=e.window_days))
        for h in sorted(hs8):
            prods.append(dict(document_number=e.document_number, hs8=h))

    r = pd.DataFrame(res)
    p = pd.DataFrame(prods)
    r.to_csv("events_resolved.csv", index=False)
    p.to_csv("event_products.csv", index=False)

    print(f"events in table            {len(ev)}")
    print(f"events resolved to cells   {r.document_number.nunique()}")
    print(f"event x partner rows       {len(r):,}\n")
    print("by mechanism (events, partners):")
    for m, g in r.groupby("mechanism"):
        print(f"  {m:<15} {g.document_number.nunique():>3} events  "
              f"{g.cty.nunique():>3} partners  "
              f"{g.n_hs8.max():>5} max HS8 lines")
    print(f"\nenumerated event x HS8 rows {len(p):,}")
    w = r.drop_duplicates("document_number").window_days.dropna()
    print(f"\nannouncement-to-effective window, days:")
    print(w.describe(percentiles=[.25, .5, .75]).round(1).to_string())
    print(f"  events with a 7+ day window: {(w >= 7).sum()} of {len(w)}")


if __name__ == "__main__":
    main()
