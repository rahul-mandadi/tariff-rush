"""The monthly forecast: at months 3 to 14 after a duty, which falling products will come back?

One model is trained across all months, tested year by year on later cases, and compared with the
historical rate and a model of the latest share alone. Inputs use only data released by each
decision date.

Reads:  recovery_pairs_decision_fall20.csv, panel/adcvd_stacks_decision.parquet, panel/hs8/,
        adcvd_episodes_collapsed.csv, events/adcvd_events.csv, events/adcvd_margins.csv,
        census_release_calendar.csv
Writes: prediction_landmark.csv, prediction_landmark_heldout.csv, prediction_landmark_coef.csv,
        prediction_landmark_counts.csv, panel/landmark_features.parquet, panel/landmark_open.parquet
Run:    python3 forecast/prediction_landmark.py
        (after measure/build_decision_stacks.py; about 80 seconds)
"""
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, ".")  # the shared modules are at the repo root
import modeling as M  # noqa: E402
import recovery_lib as RL  # noqa: E402

K_HI, LAG, LANDMARKS = 18, 2, list(range(3, 15))
REL = pd.read_csv("census_release_calendar.csv", parse_dates=["release"])
rng = np.random.default_rng(0)
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
BOTH = RL.both_programs_known(ep)
fs = RL.final_stage(ep)
ev = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str}).drop_duplicates("document_number")
pubd = pd.to_datetime(ev.set_index("document_number").publication_date)
mg = pd.read_csv("events/adcvd_margins.csv").set_index("document_number").rate
crit_doc = RL.crit_flags()  # per notice and country
CCS = RL.cc_side_dates(ep)

pairs = pd.read_csv("recovery_pairs_decision_fall20.csv", dtype={"hs8": str})
pairs["hs8"] = pairs.hs8.str.zfill(8)
# open pairs: month 18 not yet in the data; scored only by frozen_forecast.py, never trained or tested on
pairs_open = pairs[(pairs.category == "censored") & pairs.fell_at.notna()].reset_index(drop=True)
pairs = pairs[(pairs.category != "censored") & pairs.fell_at.notna()].reset_index(drop=True)
st = pd.read_parquet("panel/adcvd_stacks_decision.parquet")
st = st[st.sid.isin(set(pairs.sid) | set(pairs_open.sid))]
paths = RL.share_paths(st)
q = RL.load_raw(set(pairs.hs8) | set(pairs_open.hs8), int(ep.b.min()) - 18, int(ep.b.max()) + 16, qty=True)
raw = {h: g[["cty", "m", "value"]] for h, g in q.groupby("hs8")}
uvq = RL.one_unit_qty(q)


def case_facts(s, upto):
    ds = [d for d in ep.docs[s].split(";") if pubd[d] <= upto]
    rates = [mg.get(d, np.nan) for d in ds]
    rate = np.nansum(rates) if any(pd.notna(r) for r in rates) else np.nan
    return dict(log_rate=float(np.log1p(rate)) if pd.notna(rate) else 0.0, rate_missing=float(pd.isna(rate)),
                crit=float(RL.crit_known([(d, ep.cty[s]) for d in ds], crit_doc, CCS[s], upto)), both=float(BOTH[s]),
                china=float(ep.cty[s] == "5700"))


M_DATA = int(q.m.max())  # the last month in the harvested panel


def build_rows(pairs_, landmarks, open_=False):
    rows = []
    for r in pairs_.itertuples():
        s, h, b0 = r.sid, r.hs8, int(ep.b[r.sid])
        pf = RL.pre_features(raw, h, b0, ep.cty[s])
        if pf is None or (s, h) not in paths:
            continue
        sh, sm, v = paths[(s, h)]
        for L in landmarks:
            # data through L - 2, or less if Census had not released it by the end of month L
            seen = REL[REL.release < pd.Timestamp(year=(b0 + L + 1) // 12, month=(b0 + L + 1) % 12 + 1, day=1)].m.max()
            if open_ and int(seen) > M_DATA:
                continue  # the decision would use a released month we have not harvested
            kv = min(L - LAG, int(seen) - b0)
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
            rows.append(dict(sid=s, hs8=h, cluster=r.cluster, year=b0 // 12, b=b0, L=L, kv=kv, dec=dec,
                             y=np.nan if open_ else int(pd.notna(r.rec_at)),
                             **pf, **case_facts(s, dec),
                             k_fall=float(r.fell_at), since_fall=float(kv - r.fell_at),
                             depth=float(post.min() / r.bench), latest=float(post.iloc[-1] / r.bench),
                             slope=float((recent.iloc[-1] - recent.iloc[0]) / r.bench) if len(recent) > 1 else 0.0,
                             zero_months=float((vv == 0).mean()), rush=float(sh.loc[-6:-1].mean() / r.bench),
                             uv_change=0.0 if pd.isna(uvc) else float(np.clip(uvc, -3, 3)), uv_missing=float(pd.isna(uvc)),
                             vote_confirmed=float(vote == "order"), vote_lifted=float(vote == "negative"),
                             vote_unknown=float(vote == "not yet")))
    return pd.DataFrame(rows)


D = build_rows(pairs, LANDMARKS)
# open relationships at month 4, inputs as of their own decision date (frozen_forecast.py)
build_rows(pairs_open, [4], open_=True).to_parquet("panel/landmark_open.parquet")
D = D.dropna().reset_index(drop=True)
# each case counts once at each landmark (the same weights used for scoring), so the training
# rate at a landmark is not tilted toward products that stay eligible longer
D["w"] = 1.0 / D.groupby(["sid", "L"]).sid.transform("size")
# the feature table, with each row's last visible month (kv) and decision date, for feature_ladder.py
D.to_parquet("panel/landmark_features.parquet")
FEAT = ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals", "log_rate", "rate_missing", "crit",
        "both", "china", "k_fall", "since_fall", "depth", "latest", "slope", "zero_months", "rush",
        "uv_change", "uv_missing", "vote_confirmed", "vote_lifted", "vote_unknown", "L"]
print(f"product-landmark rows {len(D):,}; products {D[['sid', 'hs8']].drop_duplicates().shape[0]:,}; "
      f"cases {D.sid.nunique()}; groups {D.cluster.nunique()}")
print("eligible products by landmark:", D.groupby("L").size().to_dict())
# eligible counts over all years (products, cases, groups) by landmark, for the report tables
D.groupby("L").agg(products=("hs8", "size"), cases=("sid", "nunique"), groups=("cluster", "nunique")) \
    .to_csv("prediction_landmark_counts.csv")


# the benchmark: only the latest published share and the landmark month, what a team could read off
# the published data without a model
MODELS = {"logistic": (M.logistic(FEAT), M.LOGISTIC_GRID), "boosting": (M.boosting(FEAT), M.BOOSTING_GRID),
          "share only": (M.logistic(["latest", "L"]), [0.1, 1.0])}
preds = []
for Y in sorted(D.year.unique()):
    te = D[D.year == Y]
    tr = D[(D.b + K_HI + LAG) < Y * 12].reset_index(drop=True)
    if te.sid.nunique() < 5 or tr.sid.nunique() < 40 or te.y.nunique() < 2:
        continue
    # b (month of k = 0) and latest (published share over pre-case) are carried for the review queue
    p = te[["sid", "hs8", "cluster", "year", "b", "L", "y", "latest"]].copy()
    # per-landmark weights for scoring: each case counts once at each landmark
    p["w"] = 1.0 / te.groupby(["sid", "L"]).sid.transform("size")
    base = tr.groupby("L").apply(lambda g: np.average(g.y, weights=g.w), include_groups=False)
    p["history"] = te.L.map(base).fillna(np.average(tr.y, weights=tr.w)).values
    for name, (make, grid) in MODELS.items():
        p[name] = make(M.tune(tr, grid, make), tr)(te)
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
# simultaneous one-sided 90 percent lower bounds over all landmark months (max-t), resampling
# investigation groups jointly across months, so "ahead in some month" is tested as one claim
cl = P.cluster.unique()
idx = {c: np.flatnonzero(P.cluster.values == c) for c in cl}
Ls = sorted(P.L.unique())
for m in ["boosting", "logistic"]:
    est = R.set_index("L").loc[Ls, f"over_share_{m}"].to_numpy()
    draws = np.empty((1000, len(Ls)))
    for b_ in range(1000):
        q_ = P.iloc[np.concatenate([idx[c] for c in rng.choice(cl, len(cl), replace=True)])]
        for j, L in enumerate(Ls):
            g = q_[q_.L == L]
            draws[b_, j] = (brier_score_loss(g.y, g["share only"], sample_weight=g.w)
                            - brier_score_loss(g.y, g[m], sample_weight=g.w))
    sd = draws.std(axis=0, ddof=1)
    c90 = np.quantile(((draws - est) / sd).max(axis=1), 0.90)
    R[f"simlo_os_{m}"] = est - c90 * sd
    print(f"{m} over share-only, simultaneous over months {Ls[0]}-{Ls[-1]}: critical value {c90:.2f}; "
          f"months with bound above zero: {[L for L, v in zip(Ls, est - c90 * sd) if v > 0] or 'none'}")
R.to_csv("prediction_landmark.csv", index=False)
pd.set_option("display.width", 220)
print("\nby landmark month (held-out):")
print(R.round(3).to_string(index=False))
# importance: drop-column-group effect on pooled held-out Brier would need refits; report the
# full-sample logistic coefficients for reading instead
mk, grid = MODELS["logistic"]
m = make_pipeline(StandardScaler(), LogisticRegression(C=M.tune(D, grid, mk), max_iter=3000))
m.fit(D[FEAT], D.y, logisticregression__sample_weight=D.w)
co = pd.Series(m[-1].coef_[0], index=FEAT).sort_values()
print("\nfull-sample logistic coefficients (standardized; positive = more likely back):")
print(co.round(3).to_string())
co.to_csv("prediction_landmark_coef.csv")
print("wrote prediction_landmark.csv, prediction_landmark_heldout.csv, prediction_landmark_coef.csv, "
      "prediction_landmark_counts.csv")
