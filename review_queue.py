"""A review queue for a sourcing analyst: which tariff-hit product-country relationships to look at first?

Proposed use (not validated with users). A sourcing analyst can review only some of the product-country
relationships hit by antidumping or countervailing duties, and wants to start with those whose trade
decline is likely to persist. The output ranks relationships for review alongside the company's own
supplier information. It predicts the supplier country's recovery in the product (its share of U.S.
imports of that product), not whether any one supplier fails.

Rules, fixed before the results were seen (2026-11-09)

  checkpoint   month 4 after the duty starts (landmark L = 4 of prediction_landmark.py). Data visible
               through month 2, or less when a Census release slipped (census_release_calendar.csv).
  population   the landmark model's eligible products at L = 4: the fall is already visible (share
               below four-fifths of its pre-case level, smoothed, by the last visible month) and the
               product has not visibly come back. Products that never fell, or fell and were already
               back by then, are not in the queue.
  queue        one queue per decision month (the calendar month k = 4): only relationships at their
               month-4 checkpoint in that same month are ranked against each other. No later case
               enters an earlier queue.
  predictions  the held-out predictions in prediction_landmark_heldout.csv, unchanged: forward-chained
               by year of k = 0, each model trained only on cases whose month 18 was published before
               the test year, features limited to what was published by the decision date.
  target       remains down: not back at or above the pre-case share for three months running by
               month 18 (y = 0 in the held-out file).
  rankings     forecast   gradient boosting, the month-4 model of Table 3 (primary); logistic is
                          reported alongside it, not used to choose.
               latest     the latest published share over its pre-case level, lowest first: what an
                          analyst reads off Census data without a model (the landmark "share only"
                          benchmark is a monotone function of it at a fixed landmark).
               history    the training cases' recovery rate at month 4. It is one number for every
                          relationship in a queue, so ranking by it is a random order: its expected
                          result is the queue's own rate of persistent declines.
  capacity     20 percent of each queue (primary); 10 and 30 percent as sensitivity checks. These
               are assumed review capacities, not documented company budgets. A queue of n gets
               c x n reviews; where the boundary falls inside one relationship, that relationship
               counts as reviewed in part (the expected value of a random tie-break).
  ties         relationships with equal scores share the remaining capacity equally (a block of
               k tied relationships with m reviews left gives each m / k). This matters for the
               latest share, where several relationships can sit at exactly zero.
  weighting    each relationship counts once: it is the unit an analyst reviews. One case naming
               many products can dominate a queue, so intervals resample whole investigation groups.
               A case-weighted version (each case's eligible products share one unit) is reported as
               a check, and so (added after the first results) is a run without the largest
               investigation group, which holds nearly half the relationships.
  measures     precision: share of reviewed relationships that remain down. Capture: share of all
               persistent declines in the queues that were reviewed. Differences between rankings
               with 90 percent intervals from 1,000 resamples of investigation groups (whole groups
               drawn with replacement, queues rebuilt, fitted predictions held fixed).
  decision     the forecast replaces the latest share as the ranking only if, at 20 percent capacity,
               its precision is higher with the 90 percent interval above zero. Otherwise the latest
               share is the ranking, and the historical rate is reported as the benchmark it is.

Writes review_queue_eval.csv and review_queue_watchlist.csv (every held-out month-4 queue, ranked
by the chosen method; the report shows one month as an example).

Usage:  python3 review_queue.py      # after prediction_landmark.py
"""
import json
import re

import numpy as np
import pandas as pd

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


def reviewed(score, w, cap):
    """Review share in [0, 1] for each row of one queue: fill c x total weight in score order;
    tied scores share what is left equally."""
    score, w = np.asarray(score, float), np.asarray(w, float)
    left = cap * w.sum()
    r = np.zeros(len(score))
    for v in np.unique(score)[::-1]:
        idx = np.where(score == v)[0]
        need = w[idx].sum()
        if left <= 0:
            break
        take = min(1.0, left / need)
        r[idx] = take
        left -= take * need
    return r


def evaluate(D, cap, wcol=None):
    out = {}
    w_all = D[wcol].to_numpy() if wcol else np.ones(len(D))
    for name, col in RANKS.items():
        r = np.zeros(len(D))
        for _, ix in D.groupby("queue").indices.items():
            r[ix] = reviewed(D[col].to_numpy()[ix], w_all[ix], cap)
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
