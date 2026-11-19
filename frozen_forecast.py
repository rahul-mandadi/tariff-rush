"""A frozen forecast: rank the relationships whose outcome nobody knows yet, and commit the ranking.

The held-out years 2020 to 2025 have been looked at many times, so every evaluation on them is
exploratory. This makes a genuinely new test. It scores the relationships from cases that have
reached their month-4 decision point but whose month 18 is not yet in the data, writes the ranking
to frozen_forecast.csv, and records a fingerprint of that file. Committing it fixes the predictions
in time; frozen_forecast_check.py scores them as the outcomes arrive. Written 2026-11-15, with the
data harvested through August 2026.

  who        month-4 eligibility exactly as prediction_landmark.py (fall visible, not visibly back,
             inputs as of each relationship's own decision date), for pairs whose 18 months are not
             yet observed and whose month-4 decision uses only harvested months
             (panel/landmark_open.parquet, built by prediction_landmark.py)
  model      the forecast as evaluated: the same boosting model, trained once on every relationship
             whose outcome is known (all checkpoints, each case weighted once per checkpoint), tuned
             by the same grouped cross-validation; probabilities recalibrated as in
             model_recalibration.py (Platt scaling on grouped out-of-fold month-4 predictions)
  queues     one per calendar month of the month-4 checkpoint, as review_queue.py; rank 1 = most
             likely to stay down. The latest-share rank and the historical rate are recorded too,
             so the baseline comparison is fixed now as well.

Writes frozen_forecast.csv and frozen_forecast_meta.json.

Usage:  python3 frozen_forecast.py      # after prediction_landmark.py
"""
import glob
import hashlib
import json
import re

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import GroupKFold

import os  # noqa: E402

if os.path.exists("frozen_forecast_meta.json"):
    raise SystemExit("A frozen forecast already exists (frozen_forecast_meta.json). It must not be remade over: "
                     "score it with frozen_forecast_check.py.")
L_EVAL = 4
GRID = [50, 100, 200, 400]
FEAT = ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals", "log_rate", "rate_missing", "crit",
        "both", "china", "k_fall", "since_fall", "depth", "latest", "slope", "zero_months", "rush",
        "uv_change", "uv_missing", "vote_confirmed", "vote_lifted", "vote_unknown", "L"]

D = pd.read_parquet("panel/landmark_features.parquet").reset_index(drop=True)
O = pd.read_parquet("panel/landmark_open.parquet").reset_index(drop=True)
assert O.y.isna().all() and not set(zip(O.sid, O.hs8)) & set(zip(D.sid, D.hs8))


def fit(n, tr):
    m = HistGradientBoostingClassifier(max_depth=2, learning_rate=0.05, max_iter=n, l2_regularization=1.0,
                                       min_samples_leaf=40, random_state=0)
    return m.fit(tr[FEAT], tr.y, sample_weight=tr.w)


gkf = GroupKFold(n_splits=5)
best, n = None, None
for n_ in GRID:
    sc = [brier_score_loss(D.y.iloc[b], fit(n_, D.iloc[a]).predict_proba(D.iloc[b][FEAT])[:, 1],
                           sample_weight=D.w.iloc[b]) for a, b in gkf.split(D, groups=D.cluster)]
    if best is None or np.mean(sc) < best:
        best, n = np.mean(sc), n_
model = fit(n, D)
oof = np.zeros(len(D))
for a, b in gkf.split(D, groups=D.cluster):
    oof[b] = fit(n, D.iloc[a]).predict_proba(D.iloc[b][FEAT])[:, 1]


def logit(p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p)).reshape(-1, 1)


t4 = (D.L == L_EVAL).to_numpy()
cal = LogisticRegression(C=1e6, max_iter=1000).fit(logit(oof[t4]), D.y[t4], sample_weight=D.w[t4])
hist_back = float(np.average(D.y[t4], weights=D.w[t4]))

raw = model.predict_proba(O[FEAT])[:, 1]
O["p_back_raw"] = raw
O["p_back"] = cal.predict_proba(logit(raw))[:, 1]

# names, as review_queue.py
titles = {d["document_number"]: d.get("title") or "" for d in json.load(open("events/adcvd_index.json"))}
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
names = pd.read_parquet("panel/hs8/2024-06.parquet", columns=["cty", "cty_name"]).drop_duplicates().set_index("cty").cty_name


def product_of(docs):
    t = titles.get(docs.split(";")[0], "").split(" From ")[0]
    return re.sub(r"^(Certain |.*Investigations? of (Certain )?)", "", t).strip(" ,")


def month(m):
    return f"{int(m) // 12}-{int(m) % 12 + 1:02d}"


F = pd.DataFrame(dict(
    decision_month=(O.b + L_EVAL).map(month), product=O.sid.map(lambda s: product_of(ep.docs[s])),
    hs8=O.hs8.astype(str).str.zfill(8), country=O.sid.map(lambda s: names.get(ep.cty[s], ep.cty[s])).str.title(),
    p_not_back=1 - O.p_back, p_not_back_raw=1 - O.p_back_raw, latest_vs_pre=O.latest,
    historical_not_back=1 - hist_back, month_18=(O.b + 18).map(month), sid=O.sid, cluster=O.cluster,
    queue=O.b + L_EVAL))
F["queue_size"] = F.groupby("queue").sid.transform("size")
F["rank_forecast"] = F.groupby("queue").p_not_back.rank(ascending=False, method="min").astype(int)
F["rank_latest_share"] = F.groupby("queue").latest_vs_pre.rank(ascending=True, method="min").astype(int)
F = F.sort_values(["queue", "rank_forecast", "hs8", "country"]).drop(columns="queue").reset_index(drop=True)
F.to_csv("frozen_forecast.csv", index=False, float_format="%.6f")

meta = dict(made="2026-11-15", data_through=sorted(glob.glob("panel/hs8/*.parquet"))[-1][-15:-8],
            relationships=len(F), cases=int(F.sid.nunique()), groups=int(F.cluster.nunique()),
            decision_months=sorted(F.decision_month.unique().tolist()),
            outcome_months=[F.month_18.min(), F.month_18.max()], boosting_trees=int(n),
            historical_rate_not_back=round(1 - hist_back, 6),
            sha256=hashlib.sha256(open("frozen_forecast.csv", "rb").read()).hexdigest())
json.dump(meta, open("frozen_forecast_meta.json", "w"), indent=1)
pd.set_option("display.width", 220)
print(json.dumps(meta, indent=1))
print(F.groupby("decision_month").agg(relationships=("sid", "size"), cases=("sid", "nunique")).to_string())
print("wrote frozen_forecast.csv, frozen_forecast_meta.json")
