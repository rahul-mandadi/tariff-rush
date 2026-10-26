"""Can we predict WHICH origin absorbs volume displaced by a tariff?

q3_absorbers.py showed the answer is not in the tariff: absorption is more diffuse than a
placebo window, and conditional on the target country the most frequent absorber appears in
only about a quarter of cases. The open question is whether it is predictable from features of
the *alternatives* instead.

Unit of analysis: one row per (case, candidate origin). The candidate is any origin already
supplying the product basket before the case. Label: did that candidate end up the largest
absorber of share.

Every feature is measurable at the case's initiation date, so nothing leaks:
  share_pre        candidate's share of the product basket over the 12 months before
  rank_pre         its rank among suppliers by that share
  growth_pre       its own log growth over the 12 months before, against the 12 before that
  log_value_pre    absolute size in the basket
  n_origins        how many origins compete for the basket
  treated_share    size of the prize, the target's share before
  hhi_pre          how concentrated the basket already is
  same_region      crude proxy, shares the first digit of the Schedule C code with the target
  is_also_treated  the candidate is itself named by some AD/CVD case on this product, so it is
                   a poor substitute

The benchmark to beat is deliberately dumb: predict the largest incumbent. If that wins, no
model is needed and the honest answer is that the question is answered by a sort.

Validation is grouped by case and by year, so no case appears in both folds and the model is
always tested on cases later than those it learned from.

Usage:  python3 absorber_model.py
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

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

# every (hs8, origin) that any case names, to flag poor substitutes
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
    gains = d[(d > 0) & (d.index != r.cty)]
    if gains.empty:
        continue
    winner = gains.idxmax()
    v_pre = pre.groupby("cty").value.sum()
    v_pre2 = pre2.groupby("cty").value.sum() if not pre2.empty else pd.Series(dtype=float)
    hhi = float((s_pre ** 2).sum())
    for c in s_pre.index:
        if c == r.cty or s_pre[c] <= 0:
            continue
        g0 = v_pre2.get(c, np.nan)
        rows.append(dict(
            case=r.document_number, year=int(a.year), cand=c, treated=r.cty,
            share_pre=float(s_pre[c]),
            rank_pre=int((s_pre > s_pre[c]).sum()) + 1,
            growth_pre=float(np.log(v_pre[c] / g0)) if (g0 and g0 > 0) else 0.0,
            log_value_pre=float(np.log1p(v_pre[c])),
            n_origins=len(s_pre), treated_share=float(s_pre.get(r.cty, 0)),
            hhi_pre=hhi,
            same_region=int(str(c)[:1] == str(r.cty)[:1]),
            is_also_treated=int(any((h, c) in treated_pairs for h in hs)),
            y=int(c == winner)))

X = pd.DataFrame(rows)
print(f"rows (case x candidate): {len(X):,}   cases: {X.case.nunique()}   "
      f"positives: {X.y.sum()} ({X.y.mean():.1%})")

FEATS = ["share_pre", "rank_pre", "growth_pre", "log_value_pre", "n_origins",
         "treated_share", "hhi_pre", "same_region", "is_also_treated"]

# forward-chaining by year: train on earlier cases, test on later ones
years = sorted(X.year.unique())
cuts = [y for y in years if (X.year < y).sum() > 400 and (X.year == y).sum() > 60]
print(f"\nvalidation: train on cases before each year, test on that year")
print(f"{'year':<7}{'n test':>8}{'naive AUC':>12}{'logit AUC':>12}{'GBM AUC':>10}"
      f"{'naive top1':>12}{'GBM top1':>10}")
acc = []
for y in cuts:
    tr, te = X[X.year < y], X[X.year == y]
    if te.y.sum() == 0:
        continue
    naive = -te.rank_pre.to_numpy(dtype=float)          # biggest incumbent first
    lg = LogisticRegression(max_iter=2000, class_weight="balanced").fit(
        tr[FEATS], tr.y)
    gb = GradientBoostingClassifier(random_state=0, n_estimators=200,
                                    max_depth=3).fit(tr[FEATS], tr.y)
    pl, pg = lg.predict_proba(te[FEATS])[:, 1], gb.predict_proba(te[FEATS])[:, 1]
    # top-1 accuracy: within each case, does the highest-scored candidate win
    def top1(score):
        t = te.assign(s=score)
        return t.sort_values("s", ascending=False).groupby("case").head(1).y.mean()
    row = dict(year=y, n=len(te),
               naive_auc=roc_auc_score(te.y, naive),
               logit_auc=roc_auc_score(te.y, pl),
               gbm_auc=roc_auc_score(te.y, pg),
               naive_top1=top1(naive), gbm_top1=top1(pg), logit_top1=top1(pl))
    acc.append(row)
    print(f"{y:<7}{len(te):>8,}{row['naive_auc']:>12.3f}{row['logit_auc']:>12.3f}"
          f"{row['gbm_auc']:>10.3f}{row['naive_top1']:>12.2f}{row['gbm_top1']:>10.2f}")

if acc:
    a = pd.DataFrame(acc)
    print(f"\n{'mean':<7}{a.n.sum():>8,}{a.naive_auc.mean():>12.3f}"
          f"{a.logit_auc.mean():>12.3f}{a.gbm_auc.mean():>10.3f}"
          f"{a.naive_top1.mean():>12.2f}{a.gbm_top1.mean():>10.2f}")
    print(f"\nbaseline rate (pick a candidate at random): {X.y.mean():.1%}")
    gb = GradientBoostingClassifier(random_state=0, n_estimators=200, max_depth=3).fit(X[FEATS], X.y)
    imp = pd.Series(gb.feature_importances_, index=FEATS).sort_values(ascending=False)
    print("\nfeature importance (fit on all rows, for description only):")
    print(imp.round(3).to_string())
    a.to_csv("absorber_model_folds.csv", index=False)
