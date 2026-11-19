"""Score the frozen forecast as its outcomes arrive. Written 2026-11-15, before any outcome was known.

frozen_forecast.csv must not change after it is committed: this script stops unless the file still
matches the fingerprint in frozen_forecast_meta.json. The rankings in it are used as they are; nothing
is refitted.

When to run: after the data are refreshed (harvest the new Census months, then rerun the pipeline up
to build_decision_stacks.py, which rewrites recovery_pairs_decision_fall20.csv). A relationship is
resolved once its 18 months are observed there (category no longer "censored"). All relationships in
one queue share a duty month, so a queue resolves all at once; only fully resolved queues are scored.

The test (the contract's main measure, fixed now): in the resolved queues, the share of relationships
the forecast puts in the top 20 percent of its month's queue that are not back by month 18, against
the same for the latest-share ranking and for a random order (the queue's own rate); review_queue.py's
rule (ties share reviews equally; each relationship counts once). 90 percent ranges from resampling
investigation groups. Interim results are reported as interim; the final result is the run in which
every queue is resolved (the last month 18 falls in 2027). Queues whose month 18 Census had already
released before the freeze (2026-11-15) are left out of the test and only counted: the outcome was
public, even though the frozen data stopped at August 2026 (this applies to the July 2025 queue,
whose month 18, September 2026, was released on 2026-11-04).

Writes frozen_forecast_result.csv.

Usage:  python3 frozen_forecast_check.py
"""
import hashlib
import json

import numpy as np
import pandas as pd

CAP, B = 0.2, 1000
rng = np.random.default_rng(0)

meta = json.load(open("frozen_forecast_meta.json"))
assert hashlib.sha256(open("frozen_forecast.csv", "rb").read()).hexdigest() == meta["sha256"], \
    "frozen_forecast.csv has changed since it was frozen"
F = pd.read_csv("frozen_forecast.csv", dtype={"hs8": str})
F["hs8"] = F.hs8.str.zfill(8)
P = pd.read_csv("recovery_pairs_decision_fall20.csv", dtype={"hs8": str})
P["hs8"] = P.hs8.str.zfill(8)
cat = P.set_index(["sid", "hs8"]).category
F["category"] = [cat.get((s, h), "missing") for s, h in zip(F.sid, F.hs8)]
F["resolved"] = ~F.category.isin(["censored", "missing"])
F["not_back"] = (F.category != "recovered").astype(float)
REL = pd.read_csv("census_release_calendar.csv", parse_dates=["release"])
released = {f"{int(m) // 12}-{int(m) % 12 + 1:02d}" for m in REL[REL.release < pd.Timestamp(meta["made"])].m}
F["outcome_public_at_freeze"] = F.month_18.isin(released)
early = F[F.outcome_public_at_freeze]
F = F[~F.outcome_public_at_freeze]
q_ok = F.groupby("decision_month").resolved.all()
R = F[F.decision_month.map(q_ok)].reset_index(drop=True)
print(f"left out of the test, outcome already public at the freeze: {len(early)} relationships in queues "
      f"{sorted(early.decision_month.unique().tolist())}")
print(f"frozen {meta['made']} on data through {meta['data_through']}: {len(F)} relationships in "
      f"{F.decision_month.nunique()} queues; resolved queues {int(q_ok.sum())}, relationships {len(R)}")


def reviewed(score, cap):
    score = np.asarray(score, float)
    left, r = cap * len(score), np.zeros(len(score))
    for v in np.unique(score)[::-1]:
        idx = np.where(score == v)[0]
        if left <= 0:
            break
        take = min(1.0, left / len(idx))
        r[idx] = take
        left -= take * len(idx)
    return r


def precision(g, score):
    r = np.zeros(len(g))
    for _, ix in g.groupby("decision_month").indices.items():
        r[ix] = reviewed(score[ix], CAP)
    return float((r * g.not_back.to_numpy()).sum() / r.sum())


def measures(g):
    return {"forecast": precision(g, -g.rank_forecast.to_numpy()),
            "latest share": precision(g, -g.rank_latest_share.to_numpy()),
            "random order": float(g.not_back.mean())}


if len(R) == 0:
    out = pd.DataFrame([dict(status="no queue resolved yet", resolved_queues=0, relationships=0)])
else:
    pt = measures(R)
    cl = R.cluster.unique()
    idx = {c: np.flatnonzero(R.cluster.values == c) for c in cl}
    bs = [measures(R.iloc[np.concatenate([idx[c] for c in rng.choice(cl, len(cl), replace=True)])].reset_index(drop=True))
          for _ in range(B)]
    rows = []
    for k, v in pt.items():
        d = np.array([b[k] for b in bs])
        row = dict(status="final" if q_ok.all() else "interim", resolved_queues=int(q_ok.sum()),
                   relationships=len(R), ranking=k, not_back_among_reviewed=v,
                   lo=np.quantile(d, 0.05), hi=np.quantile(d, 0.95))
        if k == "forecast":
            dd = d - np.array([b["latest share"] for b in bs])
            row.update(vs_latest=v - pt["latest share"], vs_latest_lo=np.quantile(dd, 0.05),
                       vs_latest_hi=np.quantile(dd, 0.95))
        rows.append(row)
    out = pd.DataFrame(rows)
out.to_csv("frozen_forecast_result.csv", index=False)
print(out.round(3).to_string(index=False))
