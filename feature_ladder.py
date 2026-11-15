"""Retrain the month-4 model five times, adding one group of inputs each time (methodology item 1).

Steps: (a) facts about the case, (b) plus the latest share, (c) plus how the fall has gone (the
current model), (d) plus other countries' pickup, (e) plus rivals already under a duty. Each step
is scored on the review list, Brier score and AUC, on the held-out years.

Reads:  panel/landmark_features.parquet, panel/hs8/, adcvd_episodes_collapsed.csv,
        prediction_landmark_heldout.csv
Writes: feature_ladder.csv, feature_ladder_heldout.csv
Run:    python3 feature_ladder.py      (after prediction_landmark.py; stops if step c does not
        reproduce prediction_landmark_heldout.csv)
"""
import re

import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

import modeling as M
import recovery_lib as RL

K_HI, LAG, L_EVAL, CAP, B = 18, 2, 4, 0.2, 1000
rng = np.random.default_rng(0)

CTX = ["vote_confirmed", "vote_lifted", "vote_unknown", "L"]
A = ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals", "log_rate", "rate_missing", "crit",
     "both", "china"]
BB = ["latest"]
C = ["k_fall", "since_fall", "depth", "slope", "zero_months", "rush", "uv_change", "uv_missing"]
DD = ["rival_growth", "total_growth"]
E = ["dutied_rivals"]
STEPS = {"a case facts": A, "b + latest share": A + BB, "c + how the fall has gone": A + BB + C,
         "d + other countries' pickup": A + BB + C + DD, "e + rivals already under duty": A + BB + C + DD + E}

D = pd.read_parquet("panel/landmark_features.parquet")
D["hs8"] = D.hs8.astype(str).str.zfill(8)
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str, "P0": str}, parse_dates=["first_date"])

# ---------------------------------------------------------------- new inputs (steps d and e)
q = RL.load_raw(set(D.hs8), int(D.b.min()) - 18, int(D.b.max()) + 16)
by_h = {h: g.groupby(["m", "cty"]).value.sum() for h, g in q.groupby("hs8")}
named = {}
for r in ep.itertuples():
    # P0 is written as the text of a Python set ("frozenset({'94042100', ...})"): read the codes out
    for h in re.findall(r"\d{8}", str(r.P0)):
        named.setdefault(h, []).append((r.cty, r.first_date))
tcty = ep.cty


def new_inputs(r):
    g = by_h.get(r.hs8)
    tc, b0, kv = tcty[r.sid], int(r.b), int(r.kv)
    if g is None:
        return 0.0, 0.0, 0.0
    v = g.unstack(fill_value=0.0)
    post = v.reindex(range(b0, b0 + kv + 1), fill_value=0.0).sum()
    prior = v.reindex(range(b0 - 12, b0 - 12 + kv + 1), fill_value=0.0).sum()
    t_post, t_prior = post.get(tc, 0.0), prior.get(tc, 0.0)
    r_post, r_prior = post.sum() - t_post, prior.sum() - t_prior
    rival_growth = float(np.clip(np.log((r_post + 1.0) / (r_prior + 1.0)), -5, 5))
    total_growth = float(np.clip(np.log((post.sum() + 1.0) / (prior.sum() + 1.0)), -5, 5))
    pre = v.reindex(range(b0 - 18, b0 - 6), fill_value=0.0).sum().drop(tc, errors="ignore")
    pre = pre[pre > 0]
    hit = {c for c, fd in named.get(r.hs8, []) if c != tc and fd <= r.dec}
    dutied = float(pre[pre.index.isin(hit)].sum() / pre.sum()) if pre.sum() > 0 else 0.0
    return rival_growth, total_growth, dutied


vals = [new_inputs(r) for r in D.itertuples()]
D["rival_growth"], D["total_growth"], D["dutied_rivals"] = map(list, zip(*vals))
m4 = D[D.L == L_EVAL]
print(f"month-4 rows {len(m4):,}: rival_growth median {m4.rival_growth.median():+.2f}, total_growth median "
      f"{m4.total_growth.median():+.2f}, rows with any rival already under duty {(m4.dutied_rivals > 0).mean():.2f}")


# ---------------------------------------------------------------- models, exactly as prediction_landmark.py
MODELS = {"logistic": (M.logistic, M.LOGISTIC_GRID), "boosting": (M.boosting, M.BOOSTING_GRID)}
preds = []
for Y in sorted(D.year.unique()):
    te = D[D.year == Y]
    tr = D[(D.b + K_HI + LAG) < Y * 12].reset_index(drop=True)
    if te.sid.nunique() < 5 or tr.sid.nunique() < 40 or te.y.nunique() < 2:
        continue
    p = te[["sid", "hs8", "cluster", "year", "b", "L", "y", "latest"]].copy()
    p["w"] = 1.0 / te.groupby(["sid", "L"]).sid.transform("size")
    for step, cols in STEPS.items():
        feat = cols + CTX
        for name, (maker, grid) in MODELS.items():
            make = maker(feat)
            p[f"{step} | {name}"] = make(M.tune(tr, grid, make), tr)(te)
    preds.append(p)
    print(f"  test {Y}: {te.sid.nunique()} cases, {len(te):,} rows")
P = pd.concat(preds, ignore_index=True)
P.to_csv("feature_ladder_heldout.csv", index=False)

# step c must be the current model, prediction for prediction
ref = pd.read_csv("prediction_landmark_heldout.csv", dtype={"hs8": str})
assert len(ref) == len(P)
for name in MODELS:
    diff = np.abs(ref[name].to_numpy() - P[f"c + how the fall has gone | {name}"].to_numpy()).max()
    assert diff < 1e-9, f"step c {name} differs from prediction_landmark by {diff}"
print("check passed: step c reproduces prediction_landmark_heldout.csv")


# ---------------------------------------------------------------- scoring at month 4
def queue_measures(g, col):
    """(share of reviewed not back, share of all not-back reviewed) at CAP; col scored higher = review first."""
    down = 1 - g.y.to_numpy()
    r = np.zeros(len(g))
    for _, ix in g.groupby("queue").indices.items():
        r[ix] = M.review_shares(g[col].to_numpy()[ix], CAP)
    return (r * down).sum() / r.sum(), (r * down).sum() / down.sum()


G = P[P.L == L_EVAL].reset_index(drop=True)
G["queue"] = G.b + L_EVAL
G["s_latest"] = -G.latest
cols = [c for c in G.columns if " | " in c]
for c in cols:
    G["s_" + c] = 1 - G[c]


def score_all(g):
    out = {"latest share": queue_measures(g, "s_latest")}
    for c in cols:
        prec, cap = queue_measures(g, "s_" + c)
        out[c] = (prec, cap, brier_score_loss(g.y, g[c], sample_weight=g.w),
                  roc_auc_score(g.y, g[c], sample_weight=g.w))
    return out


point = score_all(G)
cl = G.cluster.unique()
idx = {c_: np.flatnonzero(G.cluster.values == c_) for c_ in cl}
boot = [score_all(G.iloc[np.concatenate([idx[c_] for c_ in rng.choice(cl, len(cl), replace=True)])]
                  .reset_index(drop=True)) for _ in range(B)]


def rng90(x):
    return np.quantile(x, [0.05, 0.95])


rows = []
steps = list(STEPS)
for name in MODELS:
    for i, step in enumerate(steps):
        c = f"{step} | {name}"
        prec, capt, br, auc = point[c]
        bp = np.array([b[c][0] for b in boot])
        dl = bp - np.array([b["latest share"][0] for b in boot])
        row = dict(model=name, step=step, inputs=len(STEPS[step]), precision20=prec,
                   lo=rng90(bp)[0], hi=rng90(bp)[1], capture20=capt, brier=br, auc=auc,
                   vs_latest=prec - point["latest share"][0], vs_latest_lo=rng90(dl)[0], vs_latest_hi=rng90(dl)[1])
        if i:
            prev = f"{steps[i - 1]} | {name}"
            dp = bp - np.array([b[prev][0] for b in boot])
            dbr = np.array([b[prev][2] for b in boot]) - np.array([b[c][2] for b in boot])
            row.update(vs_prev=prec - point[prev][0], vs_prev_lo=rng90(dp)[0], vs_prev_hi=rng90(dp)[1],
                       brier_gain_vs_prev=point[prev][2] - br, brier_gain_lo=rng90(dbr)[0], brier_gain_hi=rng90(dbr)[1])
        rows.append(row)
T = pd.DataFrame(rows)
T.to_csv("feature_ladder.csv", index=False)
pd.set_option("display.width", 250)
print(f"\nmonth 4, held-out {len(G)} relationships, {G.sid.nunique()} cases, {G.cluster.nunique()} groups; "
      f"latest-share ranking at 20%: {point['latest share'][0]:.3f}; random: {1 - G.y.mean():.3f}")
print(T.round(3).to_string(index=False))
print("wrote feature_ladder.csv, feature_ladder_heldout.csv")
