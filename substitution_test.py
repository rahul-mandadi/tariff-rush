"""Does the volume disappear, or does it move to another country?

The episode test measures a gap: the tariffed origin against other origins of the same
product. A falling gap is consistent with two very different worlds.

  substitution   the tariffed origin falls, other origins rise, total roughly holds
  contraction    the tariffed origin falls, others do not rise, total falls

They mean opposite things to anyone committing port or trucking capacity. Under
substitution the cargo still arrives, on a different lane, through possibly different ports.
Under contraction it is simply gone. The gap cannot tell them apart, so this decomposes it
into the three absolute series.

For each AD/CVD case, within the products it names:
  treated   log volume from the named country
  others    log volume of the same products from every other origin
  total     log volume of those products from everywhere

Each is indexed to its own mean over the 12 months before initiation, so the three are on a
common footing, then compared before the case and after duties start. Paired with the same
24 month placebo shift as everything else.

Usage:  python3 substitution_test.py [--h 12]
"""
import sys
import numpy as np
import pandas as pd
from scipy import stats

args = sys.argv
H = int(args[args.index("--h")+1]) if "--h" in args else 12
PRE, SHIFT, MIN_W = 12, 24, 60

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "ym", "value"])
df["ym"] = pd.to_datetime(df.ym)

e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
p = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in p.groupby("document_number")}
e = e[(e.stage == "preliminary") & e.window_days.notna() & (e.window_days >= MIN_W)]
e = e[e.document_number.isin(prods)].copy()
e["a"] = pd.to_datetime(e.initiation_date).dt.to_period("M").dt.to_timestamp()
e["b"] = pd.to_datetime(e.publication_date).dt.to_period("M").dt.to_timestamp()
print(f"cases: {len(e)} doc-country rows, {e.document_number.nunique()} documents")

# value by (hs8, cty) and by hs8, as month-indexed series, so "others" is total minus treated
by_cell = {k: g.set_index("ym").value.sort_index()
           for k, g in df.groupby(["hs8", "cty"], sort=False)}
by_prod = {k: g.groupby("ym").value.sum().sort_index()
           for k, g in df.groupby("hs8", sort=False)}


def run(shift):
    out = []
    for _, r in e.iterrows():
        a = r.a - pd.DateOffset(months=shift)
        b = r.b - pd.DateOffset(months=shift)
        hs = [h for h in prods[r.document_number] if h in by_prod]
        if not hs:
            continue
        tot = None
        for h in hs:
            tot = by_prod[h] if tot is None else tot.add(by_prod[h], fill_value=0)
        t = None
        for h in hs:
            s2 = by_cell.get((h, r.cty))
            if s2 is not None:
                t = s2 if t is None else t.add(s2, fill_value=0)
        if t is None or tot is None or tot.empty:
            continue
        idx = tot.index
        t = t.reindex(idx, fill_value=0.0)
        oth = (tot - t).clip(lower=0)
        pre = (idx >= a - pd.DateOffset(months=PRE)) & (idx < a)
        post = (idx >= b) & (idx < b + pd.DateOffset(months=H))
        if pre.sum() < PRE - 3 or post.sum() < 6:
            continue
        rec = {"document_number": r.document_number, "cty": r.cty}
        ok = True
        for name, s in [("treated", t), ("others", oth), ("total", tot)]:
            base = s[pre].mean()
            if base <= 0 or s[post].mean() <= 0:
                ok = False
                break
            rec[name] = float(np.log(s[post].mean() / base))
        if ok:
            out.append(rec)
    return pd.DataFrame(out)


real, plac = run(0), run(SHIFT)
real.to_csv("substitution_real.csv", index=False)
print(f"\nepisodes: real {len(real)}, placebo {len(plac)}")
print(f"horizon: {H} months after duties start, against the 12 months before initiation\n")
print(f"  {'series':<10}{'real mean':>12}{'real med':>11}{'placebo':>11}{'p (vs plac)':>13}")
for c in ["treated", "others", "total"]:
    a, b = real[c].dropna(), plac[c].dropna()
    pv = stats.mannwhitneyu(a, b, alternative="two-sided").pvalue if min(len(a), len(b)) > 5 else np.nan
    print(f"  {c:<10}{a.mean():>+12.4f}{a.median():>+11.4f}{b.median():>+11.4f}{pv:>13.4f}")

print("\nin percent, real events:")
for c in ["treated", "others", "total"]:
    m = real[c].median()
    print(f"  {c:<10}{100*(np.exp(m)-1):>+8.1f}%")

print("\nreading:")
tr, ot, to = real.treated.median(), real.others.median(), real.total.median()
if tr < -0.05 and ot > 0.02:
    print("  the named origin falls and other origins rise: substitution")
elif tr < -0.05 and to < -0.05 and ot <= 0.02:
    print("  the named origin falls, others do not rise, the total falls: contraction")
else:
    print("  mixed, read the numbers rather than a label")
print(f"\n  share of episodes where others rose while treated fell: "
      f"{100*((real.treated<0)&(real.others>0)).mean():.0f}%")
