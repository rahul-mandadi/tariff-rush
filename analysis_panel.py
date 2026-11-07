"""Apply the inclusion rules from DESIGN.md and write the panel the tests run on.

Rules, fixed before any model was fit:
  - at least 36 months of history in the cell (an STL baseline needs three cycles)
  - median monthly value at least $100,000 (drops cells that are noise)
The third rule, that an untreated origin must exist for the same product and month,
is applied inside the test because it depends on which event is being looked at.

Output: panel/analysis.parquet

Usage:  python3 analysis_panel.py
"""
import glob
import numpy as np
import pandas as pd

MIN_MONTHS, MIN_MED = 36, 100_000

files = sorted(glob.glob("panel/hs8/*.parquet"))
df = pd.concat([pd.read_parquet(f, columns=["hs8", "cty", "chapter", "value",
                                            "qty", "qty_ok", "ves_wgt", "air_wgt", "ym"])
                for f in files], ignore_index=True)
print(f"full panel: {len(df):,} cells")

keep = df.groupby(["hs8", "cty"]).agg(months=("ym", "nunique"), med=("value", "median"))
keep = keep[(keep.months >= MIN_MONTHS) & (keep.med >= MIN_MED)]
print(f"cells passing inclusion rules: {len(keep):,}")

df = df.merge(keep.index.to_frame(index=False), on=["hs8", "cty"], how="inner")
df = df[df.value > 0]
df["lv"] = np.log(df.value)
df["lq"] = np.where(df.qty_ok & (df.qty > 0), np.log(df.qty.where(df.qty > 0)), np.nan)
df["seaborne"] = df.ves_wgt > (df.air_wgt + df.ves_wgt) * 0.5

print(f"analysis panel: {len(df):,} rows, ${df.value.sum()/1e12:,.2f}T, "
      f"{df.hs8.nunique():,} HS8 lines, {df.cty.nunique()} partners")
print(f"  rows with usable quantity: {df.lq.notna().sum():,} "
      f"({100*df.lq.notna().mean():.1f}%)")
df.to_parquet("panel/analysis.parquet", index=False, compression="zstd")
print("wrote panel/analysis.parquet")
