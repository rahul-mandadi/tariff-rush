"""A forecast that updates every month: how soon can a sourcing team tell which products come back?

prediction_stage2.py scores two fixed moments. A team sees new trade data every month, so this
re-scores the question at every landmark month L = 3, 4, ..., 14 after the duty starts.

At landmark L (data visible through k = L - 2, the Census release lag), the eligible products are
those whose fall is already visible (fall month <= L - 2) and that are not yet visibly back (no
completed three-month run at or above the pre-case share by L - 2). Target: back by month 18.
Comparison panels, outcomes and products are the decision-time ones (build_decision_stacks.py).

Features at L, all public by then:
  day one        pre-case share, trend, size, rival count and concentration; duty rate from notices
                 published by L, missing flag; critical circumstances; both AD and CVD; China
  trade so far   month of the fall, months since it, deepest and latest smoothed share (ratio to
                 pre-case), change in the smoothed share over the last three visible months, share
                 of months with no trade, share in k -6..-1, unit-value change against rivals
  ITC vote       duty confirmed / lifted / not yet public by the decision date (the last day
                 before landmark month L, the same date used for notices)
  landmark       L itself
One model pools all landmarks (a "landmark supermodel"); each product-landmark row is weighted
1 / (eligible products in its case at that landmark), so each case counts once at each landmark.
At the fall itself the deepest and latest smoothed share are equal by construction, and since_fall
is L - 2 - k_fall, so those coefficients cannot be read separately.

Validation: forward-chaining by year of k = 0, training only on cases whose month 18 was published
before the test year (as prediction_stage2.py). Models: L2 logistic regression, shallow gradient
boosting, and a benchmark using only the latest published share and the landmark month (what a team
could read off the data without a model). Baseline at each landmark: the training cases' recovery rate among products eligible at
that same landmark. Scored per landmark (Brier, AUC) with 90 percent intervals from 1,000 resamples
of investigation groups, holding fitted models fixed.

Usage:  python3 prediction_landmark.py      # after build_decision_stacks.py
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import recovery_lib as RL

K_HI, LAG, LANDMARKS = 18, 2, list(range(3, 15))
rng = np.random.default_rng(0)
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
fs = RL.final_stage(ep)
ev = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str}).drop_duplicates("document_number")
pubd = pd.to_datetime(ev.set_index("document_number").publication_date)
mg = pd.read_csv("events/adcvd_margins.csv").set_index("document_number").rate
crit_doc = ev.set_index("document_number").critical_affirm.fillna(False).astype(bool)

pairs = pd.read_csv("recovery_pairs_decision_fall20.csv", dtype={"hs8": str})
pairs["hs8"] = pairs.hs8.str.zfill(8)
pairs = pairs[(pairs.category != "censored") & pairs.fell_at.notna()].reset_index(drop=True)
st = pd.read_parquet("panel/adcvd_stacks_decision.parquet")
st = st[st.sid.isin(set(pairs.sid))]
paths = RL.share_paths(st)
q = RL.load_raw(set(pairs.hs8), int(ep.b.min()) - 18, int(ep.b.max()) + 16, qty=True)
raw = {h: g[["cty", "m", "value"]] for h, g in q.groupby("hs8")}
uvq = RL.one_unit_qty(q)


def case_facts(s, upto):
    ds = [d for d in ep.docs[s].split(";") if pubd[d] <= upto]
    rates = [mg.get(d, np.nan) for d in ds]
    rate = np.nansum(rates) if any(pd.notna(r) for r in rates) else np.nan
    return dict(log_rate=float(np.log1p(rate)) if pd.notna(rate) else 0.0, rate_missing=float(pd.isna(rate)),
                crit=float(any(crit_doc.get(d, False) for d in ds)), both=float(ep.ad[s] and ep.cvd[s]),
                china=float(ep.cty[s] == "5700"))


rows = []
for r in pairs.itertuples():
    s, h, b0 = r.sid, r.hs8, int(ep.b[r.sid])
    pf = RL.pre_features(raw, h, b0, ep.cty[s])
    if pf is None or (s, h) not in paths:
        continue
    sh, sm, v = paths[(s, h)]
    for L in LANDMARKS:
        kv = L - LAG
        if r.fell_at > kv or (pd.notna(r.rec_at) and r.rec_at + 2 <= kv):
            continue
        post = sm.loc[0:kv].dropna()
        if post.empty:
            continue
        recent = sm.loc[kv - 3:kv].dropna()
        vv = v.reindex(range(0, kv + 1), fill_value=0)
        uvc = RL.uv_change(uvq, h, b0, ep.cty[s], kv)
        dec = pd.Timestamp(year=(b0 + L) // 12, month=(b0 + L) % 12 + 1, day=1) - pd.Timedelta(days=1)
        # the vote counts as known only if its notice was published by the decision date
        df_, stg = fs.d_final[s], fs.stage[s]
        vote = stg if (df_ is not None and pd.notna(df_) and df_ <= dec and stg in ("order", "negative")) \
            else "not yet"
        rows.append(dict(sid=s, hs8=h, cluster=r.cluster, year=b0 // 12, b=b0, L=L, y=int(pd.notna(r.rec_at)),
                         **pf, **case_facts(s, dec),
                         k_fall=float(r.fell_at), since_fall=float(kv - r.fell_at),
                         depth=float(post.min() / r.bench), latest=float(post.iloc[-1] / r.bench),
                         slope=float((recent.iloc[-1] - recent.iloc[0]) / r.bench) if len(recent) > 1 else 0.0,
                         zero_months=float((vv == 0).mean()), rush=float(sh.loc[-6:-1].mean() / r.bench),
                         uv_change=0.0 if pd.isna(uvc) else float(np.clip(uvc, -3, 3)), uv_missing=float(pd.isna(uvc)),
                         vote_confirmed=float(vote == "order"), vote_lifted=float(vote == "negative"),
                         vote_unknown=float(vote == "not yet")))
D = pd.DataFrame(rows)
D = D.dropna().reset_index(drop=True)
# each case counts once at each landmark (the same weights used for scoring), so the training
# rate at a landmark is not tilted toward products that stay eligible longer
D["w"] = 1.0 / D.groupby(["sid", "L"]).sid.transform("size")
FEAT = ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals", "log_rate", "rate_missing", "crit",
        "both", "china", "k_fall", "since_fall", "depth", "latest", "slope", "zero_months", "rush",
        "uv_change", "uv_missing", "vote_confirmed", "vote_lifted", "vote_unknown", "L"]
print(f"product-landmark rows {len(D):,}; products {D[['sid', 'hs8']].drop_duplicates().shape[0]:,}; "
      f"cases {D.sid.nunique()}; groups {D.cluster.nunique()}")
print("eligible products by landmark:", D.groupby("L").size().to_dict())


def cv_pick(tr, grid, make):
    gkf = GroupKFold(n_splits=min(5, tr.cluster.nunique()))
    best, bp = None, None
    for p in grid:
        sc = []
        for a, b in gkf.split(tr, groups=tr.cluster):
            pr = make(p, tr.iloc[a])(tr.iloc[b])
            sc.append(brier_score_loss(tr.y.iloc[b], pr, sample_weight=tr.w.iloc[b]))
        if best is None or np.mean(sc) < best:
            best, bp = np.mean(sc), p
    return bp


def logit_make(C, tr):
    m = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=3000))
    m.fit(tr[FEAT], tr.y, logisticregression__sample_weight=tr.w)
    return lambda te: m.predict_proba(te[FEAT])[:, 1]


def gbm_make(n, tr):
    m = HistGradientBoostingClassifier(max_depth=2, learning_rate=0.05, max_iter=n, l2_regularization=1.0,
                                       min_samples_leaf=40, random_state=0)
    m.fit(tr[FEAT], tr.y, sample_weight=tr.w)
    return lambda te: m.predict_proba(te[FEAT])[:, 1]


def share_only_make(C, tr):
    """Benchmark: only the latest published share and the landmark month, what a team could read
    off the published data without a model."""
    f = ["latest", "L"]
    m = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=3000))
    m.fit(tr[f], tr.y, logisticregression__sample_weight=tr.w)
    return lambda te: m.predict_proba(te[f])[:, 1]


MODELS = {"logistic": (logit_make, [0.03, 0.1, 0.3, 1.0]), "boosting": (gbm_make, [50, 100, 200, 400]),
          "share only": (share_only_make, [0.1, 1.0])}
preds = []
for Y in sorted(D.year.unique()):
    te = D[D.year == Y]
    tr = D[(D.b + K_HI + LAG) < Y * 12].reset_index(drop=True)
    if te.sid.nunique() < 5 or tr.sid.nunique() < 40 or te.y.nunique() < 2:
        continue
    p = te[["sid", "hs8", "cluster", "year", "L", "y"]].copy()
    # per-landmark weights for scoring: each case counts once at each landmark
    p["w"] = 1.0 / te.groupby(["sid", "L"]).sid.transform("size")
    base = tr.groupby("L").apply(lambda g: np.average(g.y, weights=g.w), include_groups=False)
    p["history"] = te.L.map(base).fillna(np.average(tr.y, weights=tr.w)).values
    for name, (make, grid) in MODELS.items():
        p[name] = make(cv_pick(tr, grid, make), tr)(te)
    preds.append(p)
    print(f"  test {Y}: train cases {tr.sid.nunique()}, test cases {te.sid.nunique()}, rows {len(te):,}")
P = pd.concat(preds, ignore_index=True)
P.to_csv("prediction_landmark_heldout.csv", index=False)

out = []
for L, g in P.groupby("L"):
    g = g.reset_index(drop=True)
    cl = g.cluster.unique()
    idx = {c: np.flatnonzero(g.cluster.values == c) for c in cl}
    row = dict(L=L, products=len(g), cases=g.sid.nunique(), came_back=np.average(g.y, weights=g.w),
               brier_history=brier_score_loss(g.y, g.history, sample_weight=g.w))
    for m in MODELS:
        row[f"brier_{m}"] = brier_score_loss(g.y, g[m], sample_weight=g.w)
        row[f"auc_{m}"] = roc_auc_score(g.y, g[m], sample_weight=g.w) if g.y.nunique() > 1 else np.nan
        gains, over_share = [], []
        for _ in range(1000):
            ii = np.concatenate([idx[c] for c in rng.choice(cl, len(cl), replace=True)])
            q_ = g.iloc[ii]
            bm = brier_score_loss(q_.y, q_[m], sample_weight=q_.w)
            gains.append(brier_score_loss(q_.y, q_.history, sample_weight=q_.w) - bm)
            over_share.append(brier_score_loss(q_.y, q_["share only"], sample_weight=q_.w) - bm)
        row[f"gain_{m}"] = row["brier_history"] - row[f"brier_{m}"]
        row[f"lo_{m}"], row[f"hi_{m}"] = np.quantile(gains, [0.05, 0.95])
        if m != "share only":
            row[f"over_share_{m}"] = brier_score_loss(g.y, g["share only"], sample_weight=g.w) - row[f"brier_{m}"]
            row[f"lo_os_{m}"], row[f"hi_os_{m}"] = np.quantile(over_share, [0.05, 0.95])
    out.append(row)
R = pd.DataFrame(out)
R.to_csv("prediction_landmark.csv", index=False)
pd.set_option("display.width", 220)
print("\nby landmark month (held-out):")
print(R.round(3).to_string(index=False))
# importance: drop-column-group effect on pooled held-out Brier would need refits; report the
# full-sample logistic coefficients for reading instead
mk, grid = MODELS["logistic"]
m = make_pipeline(StandardScaler(), LogisticRegression(C=cv_pick(D, grid, mk), max_iter=3000))
m.fit(D[FEAT], D.y, logisticregression__sample_weight=D.w)
co = pd.Series(m[-1].coef_[0], index=FEAT).sort_values()
print("\nfull-sample logistic coefficients (standardized; positive = more likely back):")
print(co.round(3).to_string())
co.to_csv("prediction_landmark_coef.csv")
print("wrote prediction_landmark.csv, prediction_landmark_heldout.csv, prediction_landmark_coef.csv")
