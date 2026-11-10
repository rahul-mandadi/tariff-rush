"""Export the actual HS8 lines behind each surcharge code, not just a count per chapter.

build_coverage.py already resolves every 9903 code to its enumerated subheadings, but it
collapses them to n_products_in_chapter on the way out. Chapter-level counts are what forced
the earlier analysis to treat a whole chapter as treated when the median action names about
five lines in it, which is the dilution the HS8 panel exists to remove.

This re-runs the same resolution and keeps the codes.

Output
  coverage/product_lines.csv   one row per (9903 code, HS8 line)

Usage:  python3 coverage/explode_products.py      # from the repo root
"""
import json, re, sys, os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_coverage import (note_refs, subchapter_iii, parse_notes,
                            products_in, rate_of, countries_of)

codes = json.load(open("coverage/raw/hts99_codes.json"))
text = open("coverage/raw/hts99_notes.txt", errors="ignore").read()
notes = parse_notes(subchapter_iii(text))

rows = []
for c in codes:
    h = (c.get("htsno") or "").strip()
    if not re.fullmatch(r"9903\.\d{2}\.\d{2}", h):
        continue
    desc = c.get("description") or ""
    rate, _ = rate_of(c.get("general"))
    ctys = countries_of(desc)

    # same rule as build_coverage: a code often cites several notes, one defining the
    # action and another enumerating the subheadings. Take the richest list.
    best, source = [], ""
    for key in note_refs(desc):
        if key in notes:
            p = products_in(notes[key])
            if len(p) > len(best):
                best, source = p, f"note {key[0]}({key[1]})"
    if not best:
        p = products_in(desc)
        if p:
            best, source = p, "own description"

    for code in best:
        rows.append(dict(htsno=h, hs8=code.replace(".", ""), hs8_dotted=code,
                         chapter=code[:2], hs6=code.replace(".", "")[:6],
                         rate_pct=rate, countries=";".join(ctys), scope_source=source))

df = pd.DataFrame(rows)
df.to_csv("coverage/product_lines.csv", index=False)

print(f"{len(df):,} (code, HS8) pairs")
print(f"  distinct 9903 codes with enumerated lines: {df.htsno.nunique():,}")
print(f"  distinct HS8 lines named by any action:    {df.hs8.nunique():,}")
bad = df[~df.hs8.str.fullmatch(r"\d{8}")]
print(f"  malformed HS8: {len(bad)}")
print("\nlines per chapter, top 12:")
print(df.groupby("chapter").hs8.nunique().sort_values(ascending=False).head(12).to_string())
print("\nlines named per code:")
print(df.groupby("htsno").hs8.nunique().describe().round(1).to_string())
