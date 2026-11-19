"""Can an HS8 x partner cell support a per-cell baseline, and can it be identified?

DESIGN.md leaves one thing open: HS8 may be too thin to fit a counterfactual per cell,
in which case the fallback is HS6. Two separate questions, answered here before any
inclusion rule is fixed.

  1. Depth.    Does the cell have enough continuous monthly history to fit a baseline?
  2. Control.  For a treated cell, is the same product imported from some untreated
               origin in the same month? Without that there is nothing to compare to
               and the within-product design cannot run on it.

Usage:  python3 cell_density.py
"""
import glob
import pandas as pd
import numpy as np

MIN_MONTHS = 36      # STL needs three seasonal cycles
files = sorted(glob.glob("panel/hs8/*.parquet"))
df = pd.concat([pd.read_parquet(f, columns=["hs8", "cty", "value", "qty", "ym"])
                for f in files], ignore_index=True)
print(f"panel: {len(df):,} cells, {df.hs8.nunique():,} HS8 lines, "
      f"{df.cty.nunique()} partners, {df.ym.nunique()} months\n")

# ---- 1. depth -------------------------------------------------------------
cell = df.groupby(["hs8", "cty"]).agg(
    months=("ym", "nunique"), tot=("value", "sum"),
    med=("value", "median"), qty_n=("qty", "count"))
print(f"distinct HS8 x partner cells: {len(cell):,}")
print("\nmonths of history per cell:")
print(cell.months.describe(percentiles=[.25, .5, .75, .9]).round(1).to_string())

deep = cell[cell.months >= MIN_MONTHS]
print(f"\ncells with >= {MIN_MONTHS} months: {len(deep):,} "
      f"({100*len(deep)/len(cell):.1f}% of cells)")
print(f"  they carry ${deep.tot.sum()/1e12:,.2f}T of ${cell.tot.sum()/1e12:,.2f}T "
      f"({100*deep.tot.sum()/cell.tot.sum():.1f}% of all value)")
print(f"  of those, share with quantity on most months: "
      f"{100*(deep.qty_n >= MIN_MONTHS).mean():.1f}%")

for thr in [1e4, 1e5, 1e6]:
    k = deep[deep.med >= thr]
    print(f"  and median monthly value >= ${thr:>9,.0f}: {len(k):>8,} cells, "
          f"{100*k.tot.sum()/cell.tot.sum():5.1f}% of value")

# ---- 2. control availability ----------------------------------------------
lines = pd.read_csv("coverage/product_lines.csv", dtype={"hs8": str})
treated_lines = set(lines.hs8.unique())
print(f"\nHS8 lines named by some action: {len(treated_lines):,}")

# per product-month, how many partners supply it at all
pm = df.groupby(["hs8", "ym"]).cty.nunique().rename("n_origins").reset_index()
pm["named"] = pm.hs8.isin(treated_lines)
print("\norigins per product-month:")
print(pm.groupby("named").n_origins.describe(percentiles=[.25, .5, .75])
        .round(1).to_string())

enough = (pm.n_origins >= 2).groupby(pm.named).mean() * 100
print("\nproduct-months with 2+ origins (so a within-product control can exist):")
for k, v in enough.items():
    print(f"  {'named by an action' if k else 'not named':<22} {v:5.1f}%")
