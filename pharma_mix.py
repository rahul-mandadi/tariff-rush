"""Why pharmaceuticals look opposite on dollars and on quantity.

chapter_quantity.py ranks chapter 30 at 2.86 on dollars and -0.33 on quantity, which reads at
first like the dollar signal was an illusion. It is not. The surge is real; it is a shift in
product mix rather than in tonnage, and tonnage cannot see it.

This matters beyond pharmaceuticals. Cocoa shows that dollars confuse a price rise with a volume
surge. Pharmaceuticals shows that quantity confuses a mix shift with no surge at all. Neither
measure is safe at chapter level, which is the same argument as the coverage dilution: one HS8
line is one product with one unit, and both problems go away there.

Usage:  python3 pharma_mix.py      # from the repo root
"""
import numpy as np
import pandas as pd

CH = 30
SRC = "eda/chapter_month_qty.csv"


def expected(s, cut="2024-12"):
    """Same counterfactual as gen_figures.py and chapter_quantity.py."""
    pre = np.log(s[:cut])
    me = pre.groupby(pre.index.month).mean() - pre.mean()
    t = np.arange(len(pre))
    slope, intercept = np.polyfit(t[-36:], pre.values[-36:], 1)
    pred = np.exp(pre.values[-1] + slope * (np.arange(len(s)) - (len(pre) - 1))
                  + s.index.month.map(me).values)
    resid = pre.values - (intercept + slope * t) - pre.index.month.map(me).values
    return pd.Series(pred, index=s.index), float(np.std(resid, ddof=1))


d = pd.read_csv(SRC, parse_dates=["ym"])
p = d[d.chapter == CH].set_index("ym").sort_index()

print("Chapter 30, pharmaceuticals. Dominant unit KG.\n")
for col, lab in [("qty", "tonnage"), ("value", "dollars")]:
    pred, sd = expected(p[col])
    dev = (p[col] / pred - 1).loc["2025-01":"2025-08"]
    print(f"  {lab:8s} band +/-{1.96*sd*100:3.0f}%   peak {dev.max()*100:+4.0f}% "
          f"in {dev.idxmax():%b-%y}   ratio {dev.max()/(1.96*sd):+.2f}")

base, h1 = p.loc["2023-01":"2024-12"], p.loc["2025-01":"2025-08"]
print(f"\n  2025 Jan-Aug against the 2023-24 average:")
for col, lab, scale in [("value", "value", 1e9), ("qty", "tonnage", 1e3)]:
    print(f"    {lab:8s} {h1[col].mean()/scale:8.0f} vs {base[col].mean()/scale:8.0f}"
          f"   {100*(h1[col].mean()/base[col].mean()-1):+.0f}%")
print(f"    {'$ per kg':8s} {(h1.value/h1.qty).mean():8.0f} vs {(base.value/base.qty).mean():8.0f}"
      f"   {100*((h1.value/h1.qty).mean()/(base.value/base.qty).mean()-1):+.0f}%")
print("\n  So tonnage grew, at its own trend rate. Only the dollar value left the band.")

# what the March 2025 dollar spike actually was
def lines(ym):
    x = pd.read_parquet(f"panel/hs8/{ym}.parquet",
                        columns=["hs8", "cty_name", "value", "qty", "unit"])
    return x[x.hs8.astype(str).str.startswith(str(CH))]

feb, mar, apr = lines("2025-02"), lines("2025-03"), lines("2025-04")
g = lambda x: x.groupby("hs8").value.sum()
c = pd.DataFrame({"feb": g(feb), "mar": g(mar), "apr": g(apr)}).fillna(0)
c["jump"] = c.mar - (c.feb + c.apr) / 2
top = c.sort_values("jump", ascending=False).head(3)
print("\n  Biggest March 2025 jumps over the Feb/Apr average, $bn:")
for h, r in top.iterrows():
    print(f"    {h}  feb {r.feb/1e9:5.2f}  mar {r.mar/1e9:5.2f}  apr {r.apr/1e9:5.2f}"
          f"   jump {r.jump/1e9:+.2f}")

line = top.index[0]
o = mar[mar.hs8.astype(str) == line].groupby("cty_name").agg(
    bn=("value", "sum"), t=("qty", "sum")).sort_values("bn", ascending=False).head(4)
print(f"\n  Where {line} came from in March 2025:")
for cty, r in o.iterrows():
    print(f"    {cty:14s} ${r.bn/1e9:5.2f}bn  {r.t/1e3:8.0f}t  ${r.bn/r.t:8.0f}/kg")
print("\n  Same tonnage, far more of it high-value. That is a mix shift, not a price rise,")
print("  and not nothing. Tonnage is the wrong ruler for a chapter this heterogeneous.")
