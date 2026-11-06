"""One held-out test: can facts known at the preliminary beat the historical recovery benchmark?

Target, per targeted product-country pair with complete follow-up (recovery_benchmark.py):
  bad = fell by 20 percent or more and had not recovered by k = 18 (categories "not recovered"
  or "exited"); good = "no fall" or "recovered".
Features, all known by the preliminary determination (k = 0), none from later months:
  from the raw panel, every country trading the product in k -18..-7: the targeted country's
  share, its monthly share trend (slope), log of its pre-case value, number of rival countries
  (log), concentration of shares (HHI); from the notices published by k = 0 only: affirmative
  critical circumstances and the preliminary duty rate (sum of the AD and CVD all-others or
  country-wide rates, events/parse_margins.py; log of one plus the rate) with a missing
  indicator; whether the case has both AD and CVD petitions (known at initiation); China as the
  targeted country.
Model: L2-regularized logistic regression on standardized features, C chosen by grouped
cross-validation inside the training years.
Validation: forward-chaining by year of k = 0. Training uses only episodes whose 18 months had
finished before the test year began, so every training label was observable at test time.
Baseline: the benchmark, i.e. the episode-weighted share of bad outcomes in those training
episodes. Every score is episode-weighted, as in recovery_benchmark.py.
Scores: Brier score (lower is better), log loss, and AUC. The test passes only if the model's
pooled Brier is below the benchmark's.

Usage:  python3 prediction_test.py
"""
import glob

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

K_HI = 18
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
pairs = pd.read_csv("recovery_pairs_real_fall20.csv", dtype={"hs8": str})
pairs["hs8"] = pairs.hs8.str.zfill(8)
pairs = pairs[pairs.category != "censored"].copy()
pairs["bad"] = pairs.category.isin(["not recovered", "exited"]).astype(int)

# Pre-case features come from every country that traded the product before the case, read from
# the raw panel. The stacks are not used here: their rival lists drop countries named in later
# cases (clean controls for estimation), which would put future information into the features.
files = sorted(glob.glob("panel/hs8/*.parquet"))
need = set(pairs.hs8)
raw = pd.concat([pd.read_parquet(f, columns=["hs8", "cty", "ym", "value"]) for f in files])
raw = raw[raw.hs8.isin(need) & (raw.value > 0)]
raw["m"] = raw.ym.dt.year * 12 + raw.ym.dt.month - 1
by_h = {h: g[["cty", "m", "value"]] for h, g in raw.groupby("hs8")}
rows = []
for s_, h in pairs[["sid", "hs8"]].drop_duplicates().itertuples(index=False):
    b0, tc = int(ep.b[s_]), ep.cty[s_]
    g = by_h.get(h)
    g = g[(g.m >= b0 - 18) & (g.m <= b0 - 7)] if g is not None else None
    if g is None or g.empty:
        continue
    cs = g.groupby("cty").value.sum()
    csh = cs / cs.sum()
    mon = g.groupby("m").value.sum()
    tgm = g[g.cty == tc].groupby("m").value.sum().reindex(mon.index, fill_value=0)
    shm = (tgm / mon)
    x = (shm.index - b0).to_numpy(float)
    rows.append(dict(sid=s_, hs8=h, pre_share=float(csh.get(tc, 0.0)),
                     pre_trend=float(np.polyfit(x, shm.to_numpy(float), 1)[0]) if len(x) > 2 else 0.0,
                     log_pre_value=float(np.log1p(cs.get(tc, 0.0))),
                     hhi=float((csh ** 2).sum()), n_rivals=float(np.log(max(len(cs) - 1, 1)))))
f = pd.DataFrame(rows)

# Case facts as of k = 0: only notices published by the month of the first preliminary. A
# companion AD or CVD preliminary that comes out months later carries a rate nobody knew at k = 0.
ev = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str}).drop_duplicates("document_number")
pubm = pd.to_datetime(ev.set_index("document_number").publication_date)
pubm = pubm.dt.year * 12 + pubm.dt.month - 1
crit = ev.set_index("document_number").critical_affirm.fillna(False).astype(bool)
mg = pd.read_csv("events/adcvd_margins.csv").set_index("document_number").rate
docs0 = [[d for d in ds.split(";") if pubm.get(d, 10 ** 9) <= b0]
         for ds, b0 in zip(ep.docs, ep.b)]
ep["crit"] = [any(crit.get(d, False) for d in ds) for ds in docs0]
ep["rate"] = [np.nansum([mg.get(d, np.nan) for d in ds])
              if any(pd.notna(mg.get(d, np.nan)) for d in ds) else np.nan for ds in docs0]
ep["both"] = ep.ad & ep.cvd
ep["china"] = ep.cty == "5700"

d = pairs.merge(f, on=["sid", "hs8"], how="left")
for c in ["crit", "both", "china"]:
    d[c] = d.sid.map(ep[c]).astype(float)
d["rate_missing"] = d.sid.map(ep.rate).isna().astype(float)
d["log_rate"] = np.log1p(d.sid.map(ep.rate).fillna(0.0))
d["b"] = d.sid.map(ep.b)
d["w"] = 1.0 / d.groupby("sid").sid.transform("size")
FEAT = ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals", "both", "crit",
        "log_rate", "rate_missing", "china"]
d = d.dropna(subset=FEAT).reset_index(drop=True)
print(f"pairs {len(d):,}, episodes {d.sid.nunique()}, groups {d.cluster.nunique()}, "
      f"bad share (episode-weighted) {np.average(d.bad, weights=d.w):.3f}")


def fit(tr):
    best, bc = None, None
    gkf = GroupKFold(n_splits=min(5, tr.cluster.nunique()))
    for C in [0.01, 0.03, 0.1, 0.3, 1.0]:
        sc = []
        for a, b in gkf.split(tr, groups=tr.cluster):
            m = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=2000))
            m.fit(tr.loc[a, FEAT], tr.bad[a], logisticregression__sample_weight=tr.w[a])
            p = m.predict_proba(tr.loc[b, FEAT])[:, 1]
            sc.append(brier_score_loss(tr.bad[b], p, sample_weight=tr.w[b]))
        if best is None or np.mean(sc) < best:
            best, bc = np.mean(sc), C
    m = make_pipeline(StandardScaler(), LogisticRegression(C=bc, max_iter=2000))
    m.fit(tr[FEAT], tr.bad, logisticregression__sample_weight=tr.w)
    return m, bc


rows, preds = [], []
for Y in sorted(d.year.unique()):
    te = d[d.year == Y]
    tr = d[(d.b + K_HI) < Y * 12].reset_index(drop=True)
    if len(te) < 30 or tr.sid.nunique() < 60 or te.bad.nunique() < 2:
        continue
    m, C = fit(tr)
    p_m = m.predict_proba(te[FEAT])[:, 1]
    base = np.average(tr.bad, weights=tr.w)
    p_b = np.full(len(te), base)
    w = te.w
    rows.append(dict(year=Y, train_episodes=tr.sid.nunique(), test_episodes=te.sid.nunique(),
                     C=C, base_rate=base, realized=np.average(te.bad, weights=w),
                     brier_model=brier_score_loss(te.bad, p_m, sample_weight=w),
                     brier_benchmark=brier_score_loss(te.bad, p_b, sample_weight=w),
                     logloss_model=log_loss(te.bad, p_m, sample_weight=w),
                     logloss_benchmark=log_loss(te.bad, p_b, sample_weight=w),
                     auc_model=roc_auc_score(te.bad, p_m, sample_weight=w)))
    preds.append(te.assign(p_model=p_m, p_benchmark=p_b))
R = pd.DataFrame(rows)
P = pd.concat(preds)
pool = dict(year="pooled", train_episodes=np.nan, test_episodes=P.sid.nunique(), C=np.nan,
            base_rate=np.nan, realized=np.average(P.bad, weights=P.w),
            brier_model=brier_score_loss(P.bad, P.p_model, sample_weight=P.w),
            brier_benchmark=brier_score_loss(P.bad, P.p_benchmark, sample_weight=P.w),
            logloss_model=log_loss(P.bad, P.p_model, sample_weight=P.w),
            logloss_benchmark=log_loss(P.bad, P.p_benchmark, sample_weight=P.w),
            auc_model=roc_auc_score(P.bad, P.p_model, sample_weight=P.w))
R = pd.concat([R, pd.DataFrame([pool])], ignore_index=True)
print(R.round(3).to_string(index=False))

# coefficients from a fit on every complete episode, for interpretation only
m, C = fit(d)
coef = pd.Series(m[-1].coef_[0], index=FEAT).sort_values()
print(f"\nfull-sample coefficients (standardized, C = {C}); positive means more likely bad:")
print(coef.round(3).to_string())
# calibration by predicted tercile on the pooled held-out predictions
P["tercile"] = pd.qcut(P.p_model, 3, labels=["low", "mid", "high"])
cal = P.groupby("tercile", observed=True).apply(
    lambda g: pd.Series({"pairs": len(g), "episodes": g.sid.nunique(),
                         "predicted": np.average(g.p_model, weights=g.w),
                         "realized": np.average(g.bad, weights=g.w)}))
print("\nheld-out calibration by predicted tercile:")
print(cal.round(3).to_string())
passed = pool["brier_model"] < pool["brier_benchmark"]
print(f"\nmodel beats the benchmark on pooled held-out Brier: {passed}")
R.to_csv("prediction_test.csv", index=False)
coef.to_csv("prediction_test_coef.csv")
cal.to_csv("prediction_test_calibration.csv")
P.to_csv("prediction_test_heldout.csv", index=False)
print("wrote prediction_test.csv, prediction_test_coef.csv, prediction_test_calibration.csv, "
      "prediction_test_heldout.csv")

# uncertainty on the pooled improvement: bootstrap investigation groups of the held-out rows
rng = np.random.default_rng(0)
cl = P.cluster.unique()
gi = {c: np.flatnonzero(P.cluster.to_numpy() == c) for c in cl}
diffs, aucs = [], []
for _ in range(2000):
    i = np.concatenate([gi[c] for c in rng.choice(cl, len(cl), replace=True)])
    q = P.iloc[i]
    diffs.append(brier_score_loss(q.bad, q.p_benchmark, sample_weight=q.w)
                 - brier_score_loss(q.bad, q.p_model, sample_weight=q.w))
    if q.bad.nunique() == 2:
        aucs.append(roc_auc_score(q.bad, q.p_model, sample_weight=q.w))
lo, hi = np.quantile(diffs, [0.05, 0.95])
alo, ahi = np.quantile(aucs, [0.05, 0.95])
print(f"\nBrier improvement over the benchmark (benchmark minus model): {np.mean(diffs):+.4f}, "
      f"90% interval [{lo:+.4f}, {hi:+.4f}], share of draws > 0: {np.mean(np.array(diffs) > 0):.2f}")
print(f"held-out AUC 90% interval [{alo:.3f}, {ahi:.3f}]  ({len(cl)} investigation groups)")
pd.DataFrame({"brier_improvement": diffs}).to_csv("prediction_test_bootstrap.csv", index=False)
