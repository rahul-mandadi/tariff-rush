"""Small summary tables so the EDA notebook runs without the 1 GB panel cache.

panel/hs10 and panel/hs8 are gitignored and rebuilt by the acquisition scripts, which takes
about an hour. A teammate opening the notebook should not have to do that first, so the views
the notebook actually plots are written out here as CSVs small enough to commit.

Outputs
  eda/chapter_month.csv     chapter x month totals, value and quantity
  eda/chapter_partner.csv   chapter x partner totals, for the share-of-trade views
  eda/featured_series.csv   chapter x partner x month for the chapters the notebook features

Usage:  python3 eda_summary.py
"""
import glob, os
import pandas as pd

FEATURED = ["74", "76", "72", "73", "40", "87"]   # copper, aluminium, steel, rubber, vehicles
os.makedirs("eda", exist_ok=True)

files = sorted(glob.glob("panel/hs8/*.parquet"))
if not files:
    raise SystemExit("no panel -- run harvest_hs10.py then build_panel_hs8.py")

cm, cp, fs = [], [], []
for f in files:
    d = pd.read_parquet(f, columns=["chapter", "cty", "cty_name", "value",
                                    "qty", "qty_ok", "ves_wgt", "air_wgt", "ym"])
    d["kg"] = d.qty.where(d.qty_ok)
    cm.append(d.groupby(["chapter", "ym"], as_index=False)
              .agg(value=("value", "sum"), kg=("kg", "sum"),
                   ves=("ves_wgt", "sum"), air=("air_wgt", "sum")))
    cp.append(d.groupby(["chapter", "cty", "cty_name"], as_index=False)
              .agg(value=("value", "sum")))
    s = d[d.chapter.isin(FEATURED)]
    fs.append(s.groupby(["chapter", "cty", "cty_name", "ym"], as_index=False)
              .agg(value=("value", "sum"), kg=("kg", "sum")))

cm = pd.concat(cm).groupby(["chapter", "ym"], as_index=False).sum()
cp = pd.concat(cp).groupby(["chapter", "cty", "cty_name"], as_index=False).value.sum()
fs = pd.concat(fs).groupby(["chapter", "cty", "cty_name", "ym"], as_index=False).sum()
# keep the featured file small: the partners that actually matter
top = fs.groupby(["chapter", "cty"]).value.sum().reset_index()
top = top[top.value > top.groupby("chapter").value.transform("sum") * 0.01]
fs = fs.merge(top[["chapter", "cty"]], on=["chapter", "cty"])

for name, d in [("chapter_month", cm), ("chapter_partner", cp), ("featured_series", fs)]:
    p = f"eda/{name}.csv"
    d.to_csv(p, index=False)
    print(f"  {p:<28}{len(d):>8,} rows   {os.path.getsize(p)/1e6:>5.2f} MB")

print(f"\nmonths {cm.ym.nunique()}  chapters {cm.chapter.nunique()}  "
      f"total ${cm.value.sum()/1e12:,.1f}T")
