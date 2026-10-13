"""How much of a chapter does each tariff action actually touch?

The earlier analysis treated a whole HS chapter as treated whenever an action named
anything inside it. If an action names five HS8 lines out of four hundred, the chapter
series is mostly untreated trade and any real response is averaged away. That is the
dilution the HS8 panel exists to remove, and this measures it in dollars rather than
in line counts: a chapter can have few lines named and still be nearly fully covered
if those lines carry the value.

Reads the HS8 panel and coverage/product_lines.csv. Value shares are computed over a
reference window so they describe the trade mix before the tariffs, not after.

Usage:  python3 coverage_share.py [--ref 2017]
"""
import glob, sys, os
import pandas as pd

REF = "2017"
if "--ref" in sys.argv:
    REF = sys.argv[sys.argv.index("--ref") + 1]

files = sorted(glob.glob("panel/hs8/*.parquet"))
if not files:
    sys.exit("no HS8 panel -- run build_panel_hs8.py first")

ref = [f for f in files if os.path.basename(f).startswith(REF)]
if not ref:
    ref = files
    print(f"note: no {REF} months on disk, using all {len(files)} available instead\n")

cols = ["hs8", "chapter", "cty", "value"]
panel = pd.concat([pd.read_parquet(f, columns=cols) for f in ref], ignore_index=True)
print(f"reference window: {len(ref)} months, ${panel.value.sum()/1e9:,.0f}B, "
      f"{panel.hs8.nunique():,} HS8 lines")

lines = pd.read_csv("coverage/product_lines.csv", dtype={"hs8": str, "chapter": str})

# value per HS8 line and per chapter, over the reference window
by_line = panel.groupby("hs8", as_index=False).value.sum()
by_chap = panel.groupby("chapter", as_index=False).value.sum().rename(
    columns={"value": "chapter_value"})

named = lines.merge(by_line, on="hs8", how="left")
matched = named.value.notna().sum()
print(f"\nHS8 lines named by an action:      {lines.hs8.nunique():,}")
print(f"  matched to trade in the panel:   {named[named.value.notna()].hs8.nunique():,}")
print(f"  named but no trade in window:    {named[named.value.isna()].hs8.nunique():,}")
named["value"] = named.value.fillna(0)

# per action-chapter: what share of the chapter's value do its named lines carry
g = (named.groupby(["htsno", "chapter"], as_index=False)
          .agg(n_lines=("hs8", "nunique"), named_value=("value", "sum"))
          .merge(by_chap, on="chapter", how="left"))
g["share"] = g.named_value / g.chapter_value
g = g[g.chapter_value.notna() & (g.chapter_value > 0)]

print(f"\nshare of chapter value covered, per (action, chapter) pair, n={len(g):,}")
print(g.share.describe(percentiles=[.1, .25, .5, .75, .9]).round(3).to_string())

bands = pd.cut(g.share, [-0.001, .01, .05, .25, .75, 1.001],
               labels=["<1%", "1-5%", "5-25%", "25-75%", ">75%"])
print("\nhow diluted a chapter-level treatment flag would have been:")
tab = bands.value_counts().reindex(["<1%", "1-5%", "5-25%", "25-75%", ">75%"])
for k, v in tab.items():
    print(f"  {k:>7}  {v:>5,}  ({100*v/len(g):4.1f}%)")

g.sort_values("share", ascending=False).to_csv("coverage/coverage_share.csv", index=False)
print(f"\nwrote coverage/coverage_share.csv  ({len(g):,} rows)")
