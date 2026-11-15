"""Check whether the month-4 forecast's chances match what happened, and where it errs (item 3).

Reads:  prediction_landmark_heldout.csv, panel/landmark_features.parquet
Writes: model_calibration.csv, model_errors.csv, slides/fig/23_reliability.png
Run:    python3 model_calibration.py      (after prediction_landmark.py)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import brier_score_loss, roc_auc_score  # noqa: E402

L_EVAL, B = 4, 1000
rng = np.random.default_rng(0)
H = pd.read_csv("prediction_landmark_heldout.csv", dtype={"hs8": str})
F = pd.read_parquet("panel/landmark_features.parquet", columns=["sid", "hs8", "L", "log_pre_value"])
F["hs8"] = F.hs8.astype(str).str.zfill(8)
H["hs8"] = H.hs8.str.zfill(8)
G = H[H.L == L_EVAL].merge(F[F.L == L_EVAL].drop(columns="L"), on=["sid", "hs8"], how="left").reset_index(drop=True)
assert len(G) == (H.L == L_EVAL).sum() and G.log_pre_value.notna().all()
BIG = G.cluster.value_counts().index[0]

SECTIONS = [((25, 27), "minerals and fuels"), ((28, 38), "chemicals"), ((39, 40), "plastics and rubber"),
            ((44, 49), "wood and paper"), ((50, 63), "textiles"), ((68, 71), "stone, glass, ceramics"),
            ((72, 83), "metals"), ((84, 85), "machinery and electrical"), ((86, 89), "vehicles"),
            ((94, 96), "furniture and other")]


def section(h):
    c = int(h[:2])
    return next((lab for (a, b), lab in SECTIONS if a <= c <= b), "other")


G["section"] = G.hs8.map(section)
G["size"] = pd.qcut(G.log_pre_value.rank(method="first"), 3, labels=["smallest third", "middle third", "largest third"])


def calib(g):
    p = np.clip(g.boosting.to_numpy(), 1e-4, 1 - 1e-4)
    lr = LogisticRegression(C=1e6, max_iter=1000).fit(np.log(p / (1 - p)).reshape(-1, 1), g.y, sample_weight=g.w)
    return dict(mean_pred=np.average(g.boosting, weights=g.w), realized=np.average(g.y, weights=g.w),
                slope=lr.coef_[0][0], brier=brier_score_loss(g.y, g.boosting, sample_weight=g.w),
                brier_history=brier_score_loss(g.y, g.history, sample_weight=g.w),
                auc=roc_auc_score(g.y, g.boosting, sample_weight=g.w) if g.y.nunique() > 1 else np.nan)


def boot(g, fn):
    cl = g.cluster.unique()
    idx = {c: np.flatnonzero(g.cluster.values == c) for c in cl}
    return [fn(g.iloc[np.concatenate([idx[c] for c in rng.choice(cl, len(cl), replace=True)])]) for _ in range(B)]


rows = []
for label, g in [("all", G), ("without the largest group", G[G.cluster != BIG])]:
    g = g.reset_index(drop=True)
    pt = calib(g)
    bs = boot(g, calib)
    row = dict(sample=label, relationships=len(g), cases=g.sid.nunique(), groups=g.cluster.nunique(), **pt)
    for k in ["slope", "brier", "auc"]:
        v = np.array([b[k] for b in bs])
        row[f"{k}_lo"], row[f"{k}_hi"] = np.nanquantile(v, [0.05, 0.95])
    rows.append(row)
    # reliability bins of equal weight
    o = g.sort_values("boosting").reset_index(drop=True)
    cw = o.w.cumsum() / o.w.sum()
    o["bin"] = np.minimum((cw * 5).clip(upper=4.999).astype(int), 4)
    for b_, h in o.groupby("bin"):
        rows.append(dict(sample=f"{label}: bin {b_ + 1} of 5", relationships=len(h), cases=h.sid.nunique(),
                         mean_pred=np.average(h.boosting, weights=h.w), realized=np.average(h.y, weights=h.w)))
C = pd.DataFrame(rows)
C.to_csv("model_calibration.csv", index=False)

err = []
for by in ["section", "size", "year"]:
    for k, g in G.groupby(by, observed=True):
        if len(g) < 30:
            continue
        g = g.reset_index(drop=True)
        pt = calib(g)
        err.append(dict(by=by, group=str(k), relationships=len(g), cases=g.sid.nunique(), groups=g.cluster.nunique(),
                        largest_group_share=(g.cluster == BIG).mean(), **pt,
                        brier_gain=pt["brier_history"] - pt["brier"]))
E = pd.DataFrame(err)
E.to_csv("model_errors.csv", index=False)

pd.set_option("display.width", 220)
print(f"month 4, held out: {len(G)} relationships, {G.sid.nunique()} cases, {G.cluster.nunique()} groups; "
      f"largest group {BIG} holds {(G.cluster == BIG).mean():.3f}")
print("\ncalibration:")
print(C.round(3).to_string(index=False))
print("\nerrors by group (brier_gain = history minus forecast; positive = forecast better):")
print(E.drop(columns=["slope"]).round(3).to_string(index=False))

plt.rcParams.update({
    "font.family": "Avenir Next", "font.size": 13, "axes.grid": True, "grid.alpha": .22,
    "grid.color": "#6E737C", "axes.edgecolor": "#6E737C", "text.color": "#14161A",
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 200,
    "savefig.bbox": "tight", "savefig.facecolor": "white"})
RED, GREY = "#C8102E", "#6E737C"
fig, ax = plt.subplots(figsize=(6.2, 5.2))
ax.plot([0, 100], [0, 100], color=GREY, ls=":", lw=1.2)
for label, c, mk in [("all", RED, "o"), ("without the largest group", GREY, "s")]:
    b_ = C[C["sample"].str.startswith(label + ": bin")]
    ax.plot(100 * b_.mean_pred, 100 * b_.realized, color=c, marker=mk, ms=7, lw=2, label=label)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_xlabel("predicted chance of coming back (%)")
ax.set_ylabel("share that came back (%)")
ax.legend(frameon=False, loc="upper left")
ax.set_title("Month 4, held out: predicted against actual\n(five bins of equal weight; dotted line = perfect)",
             loc="left", fontweight="600", fontsize=13)
fig.savefig("slides/fig/23_reliability.png")
print("wrote model_calibration.csv, model_errors.csv, slides/fig/23_reliability.png")
