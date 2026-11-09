"""Does the volume come back? Predicting how much of a product's trade survives a duty.

This is the question the project set out to answer, and it is the one prediction target that
has not been tried. The two earlier attempts both asked about the destination: which origin
absorbs the displaced volume (classification), and how much each origin takes (regression).
Both lost to a naive benchmark, because picking the winner among a dozen countries is close to
idiosyncratic.

This asks something structurally different and much more answerable: when duties land on one
origin, does the product's TOTAL import volume hold up, or does it fall? That is what a lender
or an importer actually needs, it has 583 episodes behind it rather than the 21 the rush
analysis rests on, and the drivers should be structural. How many alternative suppliers exist,
how concentrated the market already is, how large the targeted origin was, whether the
alternatives are themselves under duty: those are what determine whether a market can replace
a supplier.

  target   log(total basket volume over H months after duties start / over the 12 months
           before the case opened), so negative means the product lost trade overall

Every feature is measurable at the case's initiation date. The two benchmarks are deliberately
hard: predicting the training mean, and predicting that the basket simply continues its own
recent growth. Validation is forward-chaining by year and grouped by case, so no case appears
in both folds and the model is always tested on cases later than the ones it learned from.

Usage:  python3 retention_model.py [--h 12]
"""
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error
from scipy.stats import spearmanr

args = sys.argv
H = int(args[args.index("--h")+1]) if "--h" in args else 12
PRE, MIN_W = 12, 60

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

# every (product, origin) any case names, so origins already under duty can be flagged as
# poor substitutes at the time of the case
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
    if pre.empty or post.empty:
        continue
    v_pre, v_post = pre.value.sum(), post.value.sum()
    if v_pre <= 0 or v_post <= 0:
        continue
    # monthly averages, because the windows differ in length
    m_pre = v_pre / pre.ym.nunique()
    m_post = v_post / post.ym.nunique()
    m_pre2 = (pre2.value.sum() / pre2.ym.nunique()) if (not pre2.empty and pre2.value.sum() > 0) else np.nan

    s_pre = pre.groupby("cty").value.sum() / v_pre
    t_share = float(s_pre.get(r.cty, 0.0))
    if t_share <= 0 or t_share >= 0.999:
        continue
    alts = s_pre.drop(index=r.cty, errors="ignore")
    also = [c for c in alts.index if any((h, c) in treated_pairs for h in hs)]

    tr_pre = pre[pre.cty == r.cty].value.sum()
    tr_pre2 = pre2[pre2.cty == r.cty].value.sum() if not pre2.empty else 0

    rows.append(dict(
        case=r.document_number, cty=r.cty, year=int(a.year),
        # --- features, all from before the case opened ---
        treated_share=t_share,
        n_origins=int(len(s_pre)),
        n_alts_meaningful=int((alts > 0.01).sum()),
        hhi=float((s_pre ** 2).sum()),
        top_alt_share=float(alts.max()) if len(alts) else 0.0,
        share_also_treated=float(alts[also].sum()) if also else 0.0,
        log_basket=float(np.log1p(m_pre)),
        n_hs8=len(hs),
        window_days=float(r.window_days),
        pre_growth_total=float(np.log(m_pre / m_pre2)) if m_pre2 and m_pre2 > 0 else 0.0,
        pre_growth_treated=float(np.log(tr_pre / tr_pre2)) if tr_pre2 > 0 and tr_pre > 0 else 0.0,
        # --- target ---
        y=float(np.log(m_post / m_pre))))

X = pd.DataFrame(rows)
print(f"episodes: {len(X)}   cases: {X.case.nunique()}   countries: {X.cty.nunique()}")
print(f"\ntarget, log change in the product's total monthly volume:")
print(X.y.describe(percentiles=[.1, .25, .5, .75, .9]).round(3).to_string())
print(f"  share of episodes where the product lost volume: {(X.y < 0).mean():.0%}")

FEATS = ["treated_share", "n_origins", "n_alts_meaningful", "hhi", "top_alt_share",
         "share_also_treated", "log_basket", "n_hs8", "window_days",
         "pre_growth_total", "pre_growth_treated"]

years = sorted(X.year.unique())
cuts = [y for y in years if (X.year < y).sum() > 120 and (X.year == y).sum() > 20]
print(f"\nforward-chaining validation, train on cases before each year\n")
print(f"{'year':<7}{'n':>5}{'mean R2':>10}{'trend R2':>10}{'ridge R2':>10}{'GBM R2':>9}"
      f"{'ridge rho':>11}{'GBM rho':>9}")
acc = []
for yr in cuts:
    tr, te = X[X.year < yr], X[X.year == yr]
    mu = tr.y.mean()
    naive_mean = np.full(len(te), mu)
    naive_trend = te.pre_growth_total.to_numpy()     # the basket keeps growing as it was
    rg = Ridge(alpha=1.0).fit(tr[FEATS], tr.y)
    gb = GradientBoostingRegressor(random_state=0, n_estimators=300, max_depth=2,
                                   learning_rate=0.05, subsample=0.9).fit(tr[FEATS], tr.y)
    pr, pg = rg.predict(te[FEATS]), gb.predict(te[FEATS])
    row = dict(year=yr, n=len(te),
               mean_r2=r2_score(te.y, naive_mean),
               trend_r2=r2_score(te.y, naive_trend),
               ridge_r2=r2_score(te.y, pr), gbm_r2=r2_score(te.y, pg),
               ridge_rho=spearmanr(pr, te.y).correlation,
               gbm_rho=spearmanr(pg, te.y).correlation,
               mean_mae=mean_absolute_error(te.y, naive_mean),
               gbm_mae=mean_absolute_error(te.y, pg),
               ridge_mae=mean_absolute_error(te.y, pr))
    acc.append(row)
    print(f"{yr:<7}{len(te):>5}{row['mean_r2']:>10.3f}{row['trend_r2']:>10.3f}"
          f"{row['ridge_r2']:>10.3f}{row['gbm_r2']:>9.3f}"
          f"{row['ridge_rho']:>11.3f}{row['gbm_rho']:>9.3f}")

a = pd.DataFrame(acc)
print(f"\n{'mean':<7}{a.n.sum():>5}{a.mean_r2.mean():>10.3f}{a.trend_r2.mean():>10.3f}"
      f"{a.ridge_r2.mean():>10.3f}{a.gbm_r2.mean():>9.3f}"
      f"{a.ridge_rho.mean():>11.3f}{a.gbm_rho.mean():>9.3f}")
print(f"\nmean absolute error:  predict-the-mean {a.mean_mae.mean():.3f}   "
      f"ridge {a.ridge_mae.mean():.3f}   GBM {a.gbm_mae.mean():.3f}")
print("\nR2 above 0 beats predicting the mean. rho is rank correlation, which is what")
print("matters if the output is used to sort cases by risk rather than to quote a level.")

rg = Ridge(alpha=1.0).fit(X[FEATS], X.y)
gb = GradientBoostingRegressor(random_state=0, n_estimators=300, max_depth=2,
                               learning_rate=0.05, subsample=0.9).fit(X[FEATS], X.y)
imp = pd.Series(gb.feature_importances_, index=FEATS).sort_values(ascending=False)
print("\nfeature importance (fit on all rows, description only):")
print(imp.round(3).to_string())
coef = pd.Series(rg.coef_, index=FEATS).sort_values(key=abs, ascending=False)
print("\nridge coefficients, sign is the interpretable part:")
print(coef.round(3).to_string())
X.to_csv("retention_episodes.csv", index=False)
a.to_csv("retention_folds.csv", index=False)
