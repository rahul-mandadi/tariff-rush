"""Section 301 China Lists 1 to 3 as 8-digit product lists, dated at the month duties started.

The Federal Register publishes the List annexes as images, so the product codes cannot be read
from the notices. They come instead from the Harmonized Tariff Schedule's Chapter 99 notes, as
already parsed into coverage/product_lines.csv: heading 9903.88.01 (List 1, note 20(b)),
9903.88.02 (List 2, note 20(d)) and 9903.88.03 (List 3, note 20(f)). The notes are the 2026
edition, so codes renumbered since 2018 are missing; the match to the 2017 import data is logged
but not used as a filter.

Dates (first month duties were collected):
  List 1   July 6, 2018, 25 percent
  List 2   August 23, 2018, 25 percent
  List 3   September 24, 2018, 10 percent, raised to 25 percent from May 10, 2019
List 4A (September 1, 2019) is left out: its mapping here is incomplete, and its window runs into
China's COVID shutdown in early 2020, which would read as a tariff effect.

Products also under the 2018 Section 232 steel and aluminum duties (chapters 72, 73, 76) are
dropped, so China's rivals in the same product are not themselves newly taxed.

Usage:  python3 events/build_301_lists.py      # from the repo root
"""
import glob

import pandas as pd

LISTS = [("List 1", "9903.88.01", "2018-07-06", 25.0),
         ("List 2", "9903.88.02", "2018-08-23", 25.0),
         ("List 3", "9903.88.03", "2018-09-24", 10.0)]
pl = pd.read_csv("coverage/product_lines.csv", dtype=str)
p17 = set().union(*[set(pd.read_parquet(f, columns=["hs8"]).hs8) for f in sorted(glob.glob("panel/hs8/2017-*.parquet"))])
rows = []
for name, code, start, rate in LISTS:
    s = sorted(set(pl[pl.htsno == code].hs8))
    for h in s:
        rows.append(dict(list=name, heading=code, hs8=h, start=start, rate_pct=rate,
                         in_2017_data=h in p17, s232=h[:2] in {"72", "73", "76"}))
out = pd.DataFrame(rows)
assert not out.hs8.duplicated().any(), "a product sits on two lists"
print(out.groupby("list").agg(lines=("hs8", "size"), in_2017_data=("in_2017_data", "sum"),
                              section_232=("s232", "sum")).to_string())
# no filter on trading in 2017: that is after the fake dates (2016), so it would select the placebo
# sample on later data. Each stack keeps a product only if China traded it in its own k -18..-7.
out = out[~out.s232]
print("kept:", out.groupby("list").size().to_dict(), "total", len(out))
out.to_csv("events/s301_products.csv", index=False)
print("wrote events/s301_products.csv")
