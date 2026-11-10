"""How much of the displaced share does each origin take? The regression framing.

absorber_model.py asked which single origin absorbs most, a 1-of-13 classification, and a sort
by incumbent size beat both models. That target may simply have been the wrong one: picking the
single winner throws away the magnitudes, and the magnitudes are what a lender or a carrier
would actually use.

Target here is compositional. For each (case, candidate):

    frac = (candidate's share after - share before) / (treated origin's share loss)

so the fractions sum to about 1 across the candidates and read as "this origin took this much
of what was lost". Negative values are allowed, since some origins shrink too.

The benchmark is the economic null rather than a dumb one: **proportional reallocation**, where
the loss is shared out in proportion to the incumbents' existing shares.

    naive_frac = share_pre / (1 - treated_share_pre)

That is what you would predict with no model and no data beyond the current supplier mix. If a
model cannot beat it, the honest answer is that trade reallocates proportionally and there is
nothing further to learn.

Validation is forward-chaining by year and grouped by case, as before.

Usage:  python3 absorber_regression.py
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error
from scipy.stats import spearmanr

PRE, MIN_W, MIN_LOSS, H = 12, 60, 0.02, 12

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "ym", "value"])
df["ym"] = pd.to_datetime(df.ym)
e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
p = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in p.groupby("document_number")}
e = e[(e.stage == "preliminary") & e.window_days.notna() & (e.window_days >= MIN_W)]
e = e[e.document_number.isin(prods)].drop_duplicates(
    ["cty", "initiation_date", "publication_date"]).copy()
e["a"] = pd.to_datetime(e.initiation_date).dt.to_period("M").dt.to_timestamp()
e["b"] = pd.to_datetime(e.publication_date).dt.to_period("M").dt.to_timestamp()

treated_pairs = set()
for _, r in e.iterrows():
    treated_pairs |= {(h, r.cty) for h in prods[r.document_number]}

by_prod = {h: g for h, g in df.groupby("hs8", sort=False)}
rows = []
for _, r in e.iterrows():
    hs = [h for h in prods[r.document_number] if h in by_prod]
    if not hs:
        continue
    sub = pd.concat([by_prod[h] for h in hs], ignore_index=True)
    a, b = r.a, r.b
    pre = sub[(sub.ym >= a - pd.DateOffset(months=PRE)) & (sub.ym < a)]
    pre2 = sub[(sub.ym >= a - pd.DateOffset(months=2*PRE)) & (sub.ym < a - pd.DateOffset(months=PRE))]
    post = sub[(sub.ym >= b) & (sub.ym < b + pd.DateOffset(months=H))]
    if pre.empty or post.empty or pre.value.sum() <= 0 or post.value.sum() <= 0:
        continue
    s_pre = pre.groupby("cty").value.sum() / pre.value.sum()
    s_post = post.groupby("cty").value.sum() / post.value.sum()
    idx = s_pre.index.union(s_post.index)
    d = s_post.reindex(idx, fill_value=0) - s_pre.reindex(idx, fill_value=0)
    loss = -d.get(r.cty, 0.0)
    if loss < MIN_LOSS:
        continue
    t_share = float(s_pre.get(r.cty, 0.0))
    if t_share >= 0.999:
        continue
    v_pre = pre.groupby("cty").value.sum()
    v_pre2 = pre2.groupby("cty").value.sum() if not pre2.empty else pd.Series(dtype=float)
    hhi = float((s_pre ** 2).sum())
    for c in s_pre.index:
        if c == r.cty or s_pre[c] <= 0:
            continue
        g0 = v_pre2.get(c, np.nan)
        rows.append(dict(
            case=r.document_number, year=int(a.year), cand=c,
            share_pre=float(s_pre[c]),
            rank_pre=int((s_pre > s_pre[c]).sum()) + 1,
            growth_pre=float(np.log(v_pre[c] / g0)) if (g0 and g0 > 0) else 0.0,
            log_value_pre=float(np.log1p(v_pre[c])),
            n_origins=len(s_pre), treated_share=t_share, hhi_pre=hhi,
            same_region=int(str(c)[:1] == str(r.cty)[:1]),
            is_also_treated=int(any((h, c) in treated_pairs for h in hs)),
            naive_frac=float(s_pre[c] / (1 - t_share)),
            frac=float(d[c] / loss)))

X = pd.DataFrame(rows)
X = X[np.isfinite(X.frac)]
print(f"rows: {len(X):,}   cases: {X.case.nunique()}")
print(f"target frac: median {X.frac.median():+.3f}  IQR "
      f"{X.frac.quantile(.25):+.3f} to {X.frac.quantile(.75):+.3f}  "
      f"sd {X.frac.std():.2f}")
print(f"naive_frac:  median {X.naive_frac.median():.3f}\n")

FEATS = ["share_pre", "rank_pre", "growth_pre", "log_value_pre", "n_origins",
         "treated_share", "hhi_pre", "same_region", "is_also_treated"]

years = sorted(X.year.unique())
cuts = [y for y in years if (X.year < y).sum() > 400 and (X.year == y).sum() > 60]
print(f"{'year':<7}{'n':>7}{'naive R2':>11}{'ridge R2':>11}{'GBM R2':>10}"
      f"{'naive rho':>11}{'GBM rho':>10}")


def within_case_rho(te, pred):
    t = te.assign(p=pred)
    rs = []
    for _, g in t.groupby("case"):
        if len(g) > 2 and g.frac.nunique() > 1:
            r = spearmanr(g.p, g.frac).correlation
            if np.isfinite(r):
                rs.append(r)
    return float(np.mean(rs)) if rs else np.nan


acc = []
for y in cuts:
    tr, te = X[X.year < y], X[X.year == y]
    rg = Ridge(alpha=1.0).fit(tr[FEATS], tr.frac)
    gb = GradientBoostingRegressor(random_state=0, n_estimators=300,
                                   max_depth=3, learning_rate=0.05).fit(tr[FEATS], tr.frac)
    pr, pg = rg.predict(te[FEATS]), gb.predict(te[FEATS])
    row = dict(year=y, n=len(te),
               naive_r2=r2_score(te.frac, te.naive_frac),
               ridge_r2=r2_score(te.frac, pr),
               gbm_r2=r2_score(te.frac, pg),
               naive_rho=within_case_rho(te, te.naive_frac.to_numpy()),
               gbm_rho=within_case_rho(te, pg),
               ridge_rho=within_case_rho(te, pr),
               naive_mae=mean_absolute_error(te.frac, te.naive_frac),
               gbm_mae=mean_absolute_error(te.frac, pg))
    acc.append(row)
    print(f"{y:<7}{len(te):>7,}{row['naive_r2']:>11.3f}{row['ridge_r2']:>11.3f}"
          f"{row['gbm_r2']:>10.3f}{row['naive_rho']:>11.3f}{row['gbm_rho']:>10.3f}")

a = pd.DataFrame(acc)
print(f"\n{'mean':<7}{a.n.sum():>7,}{a.naive_r2.mean():>11.3f}{a.ridge_r2.mean():>11.3f}"
      f"{a.gbm_r2.mean():>10.3f}{a.naive_rho.mean():>11.3f}{a.gbm_rho.mean():>10.3f}")
print(f"\nmean absolute error: naive {a.naive_mae.mean():.3f}   GBM {a.gbm_mae.mean():.3f}")
print("\nR2 of 0 means no better than predicting the mean; negative is worse than that.")
print("rho is the average within-case rank correlation, which is what you need if you")
print("are ranking candidate origins rather than estimating a level.")
a.to_csv("absorber_regression_folds.csv", index=False)
