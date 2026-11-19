"""Correct the month-4 chances using earlier years only (item 7).

Each test year's model is recalibrated on its own training years (Platt scaling) and scored on
the test year. The order within a year does not change, so the review list does not either.

Reads:  panel/landmark_features.parquet, results/prediction_landmark_heldout.csv
Writes: results/model_recalibration.csv, results/model_recalibration_heldout.csv, slides/fig/24_recalibration.png
Run:    python3 forecast/model_recalibration.py      (after forecast/prediction_landmark.py)
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import brier_score_loss, roc_auc_score  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402

sys.path.insert(0, ".")  # the shared modules are at the repo root
import modeling as M  # noqa: E402

K_HI, LAG, L_EVAL, B = 18, 2, 4, 1000
rng = np.random.default_rng(0)
FEAT = ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals", "log_rate", "rate_missing", "crit",
        "both", "china", "k_fall", "since_fall", "depth", "latest", "slope", "zero_months", "rush",
        "uv_change", "uv_missing", "vote_confirmed", "vote_lifted", "vote_unknown", "L"]
D = pd.read_parquet("panel/landmark_features.parquet")


def fit(n_trees, tr):
    return M.boosting_model(n_trees).fit(tr[FEAT], tr.y, sample_weight=tr.w)


ref = pd.read_csv("results/prediction_landmark_heldout.csv")
out = []
for Y in sorted(D.year.unique()):
    te = D[D.year == Y]
    tr = D[(D.b + K_HI + LAG) < Y * 12].reset_index(drop=True)
    if te.sid.nunique() < 5 or tr.sid.nunique() < 40 or te.y.nunique() < 2:
        continue
    n = M.tune(tr, M.BOOSTING_GRID, M.boosting(FEAT))
    raw = fit(n, tr).predict_proba(te[FEAT])[:, 1]
    assert np.abs(raw - ref[ref.year == Y].boosting.to_numpy()).max() < 1e-9, f"raw {Y} differs"
    oof = np.zeros(len(tr))
    for a, b in GroupKFold(n_splits=min(5, tr.cluster.nunique())).split(tr, groups=tr.cluster):
        oof[b] = fit(n, tr.iloc[a]).predict_proba(tr.iloc[b][FEAT])[:, 1]
    t4 = (tr.L == L_EVAL).to_numpy()
    cal4 = M.platt(oof[t4], tr.y[t4], tr.w[t4])
    calall = M.platt(oof, tr.y, tr.w)
    p = te[["sid", "hs8", "cluster", "year", "b", "L", "y", "log_pre_value"]].copy()
    p["w"] = 1.0 / te.groupby(["sid", "L"]).sid.transform("size")
    p["raw"] = raw
    p["calibrated"] = cal4.predict_proba(M.log_odds(raw))[:, 1]
    p["calibrated_all_checkpoints"] = calall.predict_proba(M.log_odds(raw))[:, 1]
    out.append(p[p.L == L_EVAL])
    print(f"  {Y}: training out-of-fold at month 4 predicted {np.average(oof[t4], weights=tr.w[t4]):.3f}, "
          f"realized {np.average(tr.y[t4], weights=tr.w[t4]):.3f}")
print("check passed: raw predictions reproduce results/prediction_landmark_heldout.csv")
G = pd.concat(out, ignore_index=True)
G.to_csv("results/model_recalibration_heldout.csv", index=False)

COLS = ["raw", "calibrated", "calibrated_all_checkpoints"]


def stats(g):
    r = {}
    for c in COLS:
        lr = LogisticRegression(C=1e6, max_iter=1000).fit(M.log_odds(g[c].to_numpy()), g.y, sample_weight=g.w)
        r[c] = dict(mean_pred=np.average(g[c], weights=g.w), slope=lr.coef_[0][0],
                    brier=brier_score_loss(g.y, g[c], sample_weight=g.w),
                    auc=roc_auc_score(g.y, g[c], sample_weight=g.w) if g.y.nunique() > 1 else np.nan)
    r["realized"] = np.average(g.y, weights=g.w)
    return r


G["size"] = pd.qcut(G.log_pre_value.rank(method="first"), 3, labels=["smallest third", "middle third", "largest third"])
rows = []
for label, g in [("all", G)] + [(str(k), h) for k, h in G.groupby("size", observed=True)]:
    g = g.reset_index(drop=True)
    pt = stats(g)
    cl = g.cluster.unique()
    idx = {c: np.flatnonzero(g.cluster.values == c) for c in cl}
    bs = [stats(g.iloc[np.concatenate([idx[c] for c in rng.choice(cl, len(cl), replace=True)])]) for _ in range(B)]
    for c in COLS:
        d = np.array([b["raw"]["brier"] - b[c]["brier"] for b in bs])
        gap = np.array([b[c]["mean_pred"] - b["realized"] for b in bs])
        rows.append(dict(sample=label, model=c, relationships=len(g), realized=pt["realized"], **pt[c],
                         gap=pt[c]["mean_pred"] - pt["realized"], gap_lo=np.quantile(gap, 0.05),
                         gap_hi=np.quantile(gap, 0.95), brier_gain_vs_raw=pt["raw"]["brier"] - pt[c]["brier"],
                         brier_gain_lo=np.quantile(d, 0.05), brier_gain_hi=np.quantile(d, 0.95)))
R = pd.DataFrame(rows)

bins = []
for c in COLS:
    o = G.sort_values(c).reset_index(drop=True)
    cw = o.w.cumsum() / o.w.sum()
    o["bin"] = np.minimum((cw * 5).clip(upper=4.999).astype(int), 4)
    for b_, h in o.groupby("bin"):
        bins.append(dict(sample=f"bin {b_ + 1} of 5", model=c, relationships=len(h),
                         mean_pred=np.average(h[c], weights=h.w), realized=np.average(h.y, weights=h.w)))
R = pd.concat([R, pd.DataFrame(bins)], ignore_index=True)
R.to_csv("results/model_recalibration.csv", index=False)
pd.set_option("display.width", 220)
print(R.round(3).to_string(index=False))

plt.rcParams.update({
    "font.family": "Avenir Next", "font.size": 13, "axes.grid": True, "grid.alpha": .22,
    "grid.color": "#6E737C", "axes.edgecolor": "#6E737C", "text.color": "#14161A",
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 200,
    "savefig.bbox": "tight", "savefig.facecolor": "white"})
RED, GREY = "#C8102E", "#6E737C"
fig, ax = plt.subplots(figsize=(6.2, 5.2))
ax.plot([0, 100], [0, 100], color=GREY, ls=":", lw=1.2)
for c, col, mk, lab in [("raw", GREY, "s", "as trained"), ("calibrated", RED, "o", "recalibrated on earlier years")]:
    b_ = R[(R.model == c) & R["sample"].str.startswith("bin")]
    ax.plot(100 * b_.mean_pred, 100 * b_.realized, color=col, marker=mk, ms=7, lw=2, label=lab)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_xlabel("predicted chance of coming back (%)")
ax.set_ylabel("share that came back (%)")
ax.legend(frameon=False, loc="upper left")
ax.set_title("Month 4, held out: before and after recalibration\n(five bins of equal weight; dotted line = perfect)",
             loc="left", fontweight="600", fontsize=13)
fig.savefig("slides/fig/24_recalibration.png")
print("wrote results/model_recalibration.csv, results/model_recalibration_heldout.csv, slides/fig/24_recalibration.png")
