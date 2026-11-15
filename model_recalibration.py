"""Can the month-4 forecast's probabilities be fixed using earlier years only? (calibration fix)

model_calibration.py found the forecast too pessimistic at month 4: it predicts a 19 percent chance of
coming back on average where 26 percent came back, most of the gap in the middle of the range. This
recalibrates it without touching the test years. Fixed before running (2026-11-15); exploratory,
because the held-out years have been looked at before.

  method      for each test year, the boosting model of prediction_landmark.py (same training cases,
              same tuning, same settings) makes out-of-fold predictions on its own training cases
              (grouped 5-fold by investigation group, the number of trees fixed at the value tuned on
              the whole training set). A logistic recalibration (Platt scaling: the outcome on the
              log-odds of the prediction, each case weighted once) is fitted to those out-of-fold
              predictions and applied to the test year's predictions.
              primary    fitted on the training cases' month-4 rows
              secondary  fitted on all checkpoints 3 to 14 (reported, not used to choose)
  scored      at month 4, held out 2020 to 2025: mean predicted against realized, calibration slope,
              Brier score (and its change from the raw model), AUC, reliability in five bins, and the
              same by thirds of pre-case size; 90 percent ranges from 1,000 resamples of
              investigation groups. The recalibration preserves the order of predictions within a test
              year, and every review queue lies within one year, so the review ranking cannot change.
              AUC, which pools all years, can move slightly, because each year gets its own
              recalibration. (Corrected after the first run, which showed AUC 0.795 to 0.790.)
  check       the raw predictions must reproduce prediction_landmark_heldout.csv, or the script stops.

Writes model_recalibration.csv, model_recalibration_heldout.csv and slides/fig/24_recalibration.png.

Usage:  python3 model_recalibration.py      # after prediction_landmark.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import brier_score_loss, roc_auc_score  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402

K_HI, LAG, L_EVAL, B = 18, 2, 4, 1000
GRID = [50, 100, 200, 400]
rng = np.random.default_rng(0)
FEAT = ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals", "log_rate", "rate_missing", "crit",
        "both", "china", "k_fall", "since_fall", "depth", "latest", "slope", "zero_months", "rush",
        "uv_change", "uv_missing", "vote_confirmed", "vote_lifted", "vote_unknown", "L"]
D = pd.read_parquet("panel/landmark_features.parquet")


def fit(n, tr):
    m = HistGradientBoostingClassifier(max_depth=2, learning_rate=0.05, max_iter=n, l2_regularization=1.0,
                                       min_samples_leaf=40, random_state=0)
    return m.fit(tr[FEAT], tr.y, sample_weight=tr.w)


def cv_pick(tr):
    gkf = GroupKFold(n_splits=min(5, tr.cluster.nunique()))
    best, bp = None, None
    for n in GRID:
        sc = [brier_score_loss(tr.y.iloc[b], fit(n, tr.iloc[a]).predict_proba(tr.iloc[b][FEAT])[:, 1],
                               sample_weight=tr.w.iloc[b]) for a, b in gkf.split(tr, groups=tr.cluster)]
        if best is None or np.mean(sc) < best:
            best, bp = np.mean(sc), n
    return bp


def logit(p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p)).reshape(-1, 1)


def platt(p, y, w):
    return LogisticRegression(C=1e6, max_iter=1000).fit(logit(p), y, sample_weight=w)


ref = pd.read_csv("prediction_landmark_heldout.csv")
out = []
for Y in sorted(D.year.unique()):
    te = D[D.year == Y]
    tr = D[(D.b + K_HI + LAG) < Y * 12].reset_index(drop=True)
    if te.sid.nunique() < 5 or tr.sid.nunique() < 40 or te.y.nunique() < 2:
        continue
    n = cv_pick(tr)
    raw = fit(n, tr).predict_proba(te[FEAT])[:, 1]
    assert np.abs(raw - ref[ref.year == Y].boosting.to_numpy()).max() < 1e-9, f"raw {Y} differs"
    oof = np.zeros(len(tr))
    for a, b in GroupKFold(n_splits=min(5, tr.cluster.nunique())).split(tr, groups=tr.cluster):
        oof[b] = fit(n, tr.iloc[a]).predict_proba(tr.iloc[b][FEAT])[:, 1]
    t4 = (tr.L == L_EVAL).to_numpy()
    cal4 = platt(oof[t4], tr.y[t4], tr.w[t4])
    calall = platt(oof, tr.y, tr.w)
    p = te[["sid", "hs8", "cluster", "year", "b", "L", "y", "log_pre_value"]].copy()
    p["w"] = 1.0 / te.groupby(["sid", "L"]).sid.transform("size")
    p["raw"] = raw
    p["calibrated"] = cal4.predict_proba(logit(raw))[:, 1]
    p["calibrated_all_checkpoints"] = calall.predict_proba(logit(raw))[:, 1]
    out.append(p[p.L == L_EVAL])
    print(f"  {Y}: training out-of-fold at month 4 predicted {np.average(oof[t4], weights=tr.w[t4]):.3f}, "
          f"realized {np.average(tr.y[t4], weights=tr.w[t4]):.3f}")
print("check passed: raw predictions reproduce prediction_landmark_heldout.csv")
G = pd.concat(out, ignore_index=True)
G.to_csv("model_recalibration_heldout.csv", index=False)

COLS = ["raw", "calibrated", "calibrated_all_checkpoints"]


def stats(g):
    r = {}
    for c in COLS:
        lr = LogisticRegression(C=1e6, max_iter=1000).fit(logit(g[c].to_numpy()), g.y, sample_weight=g.w)
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
R.to_csv("model_recalibration.csv", index=False)
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
print("wrote model_recalibration.csv, model_recalibration_heldout.csv, slides/fig/24_recalibration.png")
