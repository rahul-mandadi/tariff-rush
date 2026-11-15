"""Rank each month's falling, not-yet-back relationships for review, and test the ranking.

Each calendar month's month-4 relationships form one list. A team reviews an assumed 20 percent
(also 10 and 30). Measures: the share of reviewed relationships still not back at month 18, and
the share of all of those it caught, for the forecast, the latest share and a random order.

Reads:  prediction_landmark_heldout.csv, adcvd_episodes_collapsed.csv, events/adcvd_index.json,
        panel/hs8/2024-06.parquet (country names)
Writes: review_queue_eval.csv, review_queue_watchlist.csv
Run:    python3 forecast/review_queue.py      (after forecast/prediction_landmark.py)
"""
import json
import re
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, ".")  # the shared modules are at the repo root
import modeling as M  # noqa: E402

L, CAPS, PRIMARY, B = 4, [0.2, 0.1, 0.3], 0.2, 1000
rng = np.random.default_rng(0)

P = pd.read_csv("prediction_landmark_heldout.csv", dtype={"hs8": str})
P = P[P.L == L].reset_index(drop=True)
P["hs8"] = P.hs8.str.zfill(8)
P["down"] = 1 - P.y
P["queue"] = P.b + L                                   # calendar month of the checkpoint
P["case_w"] = 1.0 / P.groupby("sid").sid.transform("size")
# higher score = review first
P["s_forecast"] = 1 - P.boosting
P["s_logistic"] = 1 - P.logistic
P["s_latest"] = -P.latest
P["s_history"] = 1 - P.history                         # constant within a queue: all tied
RANKS = {"forecast (boosting)": "s_forecast", "logistic": "s_logistic", "latest share": "s_latest",
         "historical rate": "s_history"}


def evaluate(D, cap, wcol=None):
    out = {}
    w_all = D[wcol].to_numpy() if wcol else np.ones(len(D))
    for name, col in RANKS.items():
        r = np.zeros(len(D))
        for _, ix in D.groupby("queue").indices.items():
            r[ix] = M.review_shares(D[col].to_numpy()[ix], cap, w_all[ix])
        rw, dn = r * w_all, D.down.to_numpy()
        out[name] = (float((rw * dn).sum() / rw.sum()), float((rw * dn).sum() / (w_all * dn).sum()))
    return out


# Check added after the results were first seen: one investigation group (aluminum extrusions,
# 2024, 14 countries) holds nearly half the relationships, so every comparison is also run
# without it. It does not change the decision rule above.
BIG = P.cluster.value_counts().index[0]
VARIANTS = {"relationship": (P, None), "case": (P, "case_w"),
            "relationship, largest group left out": (P[P.cluster != BIG].reset_index(drop=True), None)}


def run(D0, wc):
    groups = D0.cluster.unique()
    by_group = {g: ix for g, ix in D0.groupby("cluster").indices.items()}
    boot = []
    for _ in range(B):
        pick = rng.choice(groups, size=len(groups), replace=True)
        D = D0.iloc[np.concatenate([by_group[g] for g in pick])].reset_index(drop=True)
        boot.append({cap: evaluate(D, cap, wc) for cap in CAPS})
    return boot


rows = []
for label, (D0, wc) in VARIANTS.items():
    boot = run(D0, wc)
    for cap in CAPS:
        pt = evaluate(D0, cap, wc)
        for name in RANKS:
            for k, meas in enumerate(["precision", "capture"]):
                draws = np.array([b[cap][name][k] for b in boot])
                row = dict(capacity=cap, weighting=label, ranking=name, measure=meas, value=pt[name][k],
                           lo=np.quantile(draws, 0.05), hi=np.quantile(draws, 0.95))
                for base in ["latest share", "historical rate"]:
                    if base != name:
                        dd = draws - np.array([b[cap][base][k] for b in boot])
                        row[f"diff_vs_{base}"] = pt[name][k] - pt[base][k]
                        row[f"lo_vs_{base}"], row[f"hi_vs_{base}"] = np.quantile(dd, [0.05, 0.95])
                rows.append(row)
E = pd.DataFrame(rows)
E.to_csv("review_queue_eval.csv", index=False)

n_q = P.groupby("queue").size()
print(f"month-4 queues: {len(n_q)} decision months, {len(P)} relationships, {P.sid.nunique()} cases, "
      f"{P.cluster.nunique()} investigation groups; held-out years {sorted(P.year.unique())}")
print(f"queue size: median {n_q.median():.0f}, max {n_q.max()}, single-relationship queues {(n_q == 1).sum()}")
print(f"persistent declines among eligible relationships: {P.down.mean():.3f}")
print(f"largest investigation group ({BIG}): {(P.cluster == BIG).mean():.3f} of relationships, "
      f"{P[P.cluster == BIG].sid.nunique()} cases")
# the most a ranking can capture at each capacity: every reviewed relationship remains down
for cap in CAPS:
    best = sum(min(cap * len(g), g.down.sum()) for _, g in P.groupby("queue")) / P.down.sum()
    print(f"  capacity {cap:.0%}: the most any ranking can capture is {best:.3f} of persistent declines")
show = E[E.measure.isin(["precision", "capture"])].copy()
pd.set_option("display.width", 220)
print(show.round(3).to_string(index=False))

prim = E[(E.capacity == PRIMARY) & (E.weighting == "relationship") & (E.ranking == "forecast (boosting)")
         & (E.measure == "precision")].iloc[0]
use_forecast = prim["lo_vs_latest share"] > 0
method = "forecast (boosting)" if use_forecast else "latest share"
print(f"\nprimary test (20%, relationships): forecast minus latest share precision "
      f"{prim['diff_vs_latest share']:+.3f} [{prim['lo_vs_latest share']:+.3f}, {prim['hi_vs_latest share']:+.3f}]"
      f" -> ranking method: {method}")

# ---------------------------------------------------------------- the watchlist, ranked by the chosen method
titles = {d["document_number"]: d.get("title") or "" for d in json.load(open("events/adcvd_index.json"))}
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
names = pd.read_parquet("panel/hs8/2024-06.parquet", columns=["cty", "cty_name"]).drop_duplicates() \
    .set_index("cty").cty_name


def product_of(docs):
    t = titles.get(docs.split(";")[0], "").split(" From ")[0]
    return re.sub(r"^(Certain |.*Investigations? of (Certain )?)", "", t).strip(" ,")


col = RANKS[method]
W = P.copy()
W["product"] = W.sid.map(lambda s: product_of(ep.docs[s]))
W["country"] = W.sid.map(lambda s: names.get(ep.cty[s], ep.cty[s])).str.title()
W["decision_month"] = W.queue.map(lambda m: f"{m // 12}-{m % 12 + 1:02d}")
W["p_not_recovered"] = 1 - W.boosting
W["latest_vs_pre"] = W.latest
W["history_not_recovered"] = 1 - W.history
W["rank"] = W.groupby("queue")[col].rank(ascending=False, method="min").astype(int)
W["queue_size"] = W.groupby("queue").sid.transform("size")
W["remained_down"] = W.down
W = W.sort_values(["queue", "rank", "hs8"])
W[["decision_month", "queue_size", "rank", "product", "hs8", "country", "p_not_recovered", "latest_vs_pre",
   "history_not_recovered", "remained_down", "sid", "cluster"]].to_csv("review_queue_watchlist.csv", index=False)
print(f"wrote review_queue_eval.csv, review_queue_watchlist.csv (ranked by {method})")
