"""Redo the absorption decomposition in levels, because the log version does not decompose.

The earlier figure divided the median log change in a product's total by the median log change in
the named origin and read the remainder as absorption. That ratio is confounded with the origin's
market share: if a supplier holding 21 percent of a product stops entirely and nobody replaces
it, the total falls by 21 percent of the origin's fall, and the same arithmetic reports "79
percent absorbed" with no substitution at all. Separate medians also need not describe the same
episode.

Levels do decompose, because total = treated + others by construction, so

    delta_total = delta_treated + delta_others

and the share of the lost volume that reappears elsewhere is -delta_others / delta_treated,
defined only for episodes where the named origin actually fell. Pooled across episodes this is a
value-weighted absorption rate; the per-episode median is reported alongside it because the
pooled figure is dominated by the largest cases.

Same sample and windows as substitution_test.py, and the same 24-month placebo.

Usage:  python3 substitution_levels.py      # from the repo root
"""
import numpy as np
import pandas as pd
from scipy import stats

H, PRE, SHIFT, MIN_W = 12, 12, 24, 60

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "ym", "value"])
df["ym"] = pd.to_datetime(df.ym)
e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
p = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in p.groupby("document_number")}
e = e[(e.stage == "preliminary") & e.window_days.notna() & (e.window_days >= MIN_W)]
e = e[e.document_number.isin(prods)].copy()
e["a"] = pd.to_datetime(e.initiation_date).dt.to_period("M").dt.to_timestamp()
e["b"] = pd.to_datetime(e.publication_date).dt.to_period("M").dt.to_timestamp()

by_cell = {k: g.set_index("ym").value.sort_index() for k, g in df.groupby(["hs8", "cty"], sort=False)}
by_prod = {k: g.groupby("ym").value.sum().sort_index() for k, g in df.groupby("hs8", sort=False)}


def run(shift):
    out = []
    for _, r in e.iterrows():
        a, b = r.a - pd.DateOffset(months=shift), r.b - pd.DateOffset(months=shift)
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
        rec = {"document_number": r.document_number, "cty": r.cty,
               "share_pre": t[pre].mean() / tot[pre].mean() if tot[pre].mean() > 0 else np.nan}
        for name, s in [("treated", t), ("others", oth)]:
            rec[f"d_{name}"] = float(s[post].mean() - s[pre].mean())   # dollars a month
        out.append(rec)
    return pd.DataFrame(out)


real, plac = run(0), run(SHIFT)
real.to_csv("substitution_levels_real.csv", index=False)

def absorb(d, lab):
    f = d[d.d_treated < 0].copy()                       # only episodes where the origin fell
    pooled = -f.d_others.sum() / f.d_treated.sum()
    f["ratio"] = (-f.d_others / f.d_treated).clip(-2, 3)
    print(f"  {lab:9s} n={len(f):4d}   pooled {pooled:+6.1%}   per-episode median {f.ratio.median():+6.1%}")
    return f, pooled

print(f"episodes: real {len(real)}, placebo {len(plac)}")
print(f"median share of the product held by the named origin before the case: "
      f"{real.share_pre.median():.1%}\n")
print("share of the named origin's lost volume that reappears from other suppliers:")
fr, pr_r = absorb(real, "real")
fp, pr_p = absorb(plac, "placebo")
u = stats.mannwhitneyu(fr.ratio.dropna(), fp.ratio.dropna(), alternative="two-sided")
print(f"\n  real vs placebo on the per-episode ratio: Mann-Whitney p = {u.pvalue:.4f}")
print(f"  difference in pooled absorption: {pr_r - pr_p:+.1%}")
print("\nwrote substitution_levels_real.csv")
