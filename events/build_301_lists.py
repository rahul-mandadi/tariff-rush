"""The 8-digit product lists of the 2018 Section 301 tariffs on China (Lists 1 to 3).

Reads:  coverage/product_lines.csv, panel/hs8/ (2017 months)
Writes: events/s301_products.csv
Run:    python3 events/build_301_lists.py
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
