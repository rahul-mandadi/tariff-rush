"""Why does the month-4 forecast flag what it flags? (docs/SCOPE.md, item 2)

The forecast is the boosting model of prediction_landmark.py, unchanged. Fixed before running
(2026-11-10); exploratory, because the held-out years have been looked at before.

  importance    permutation importance on held-out data: for each test year, the model trained for
                that year is scored on that year's month-4 relationships with one input shuffled
                (20 shuffles); importance = how much worse the Brier score gets, pooled over years,
                each case weighted once. 90 percent ranges from 1,000 resamples of investigation
                groups of the per-relationship change. The refit models must reproduce
                prediction_landmark_heldout.csv, or the script stops.
  dependence    partial dependence of the chance of coming back on the most important inputs and on
                the duty rate, from one boosting model fitted on all cases (tuned the same way),
                evaluated on the month-4 rows.

Inputs that move together (the latest share, the depth of the fall and the months since it) share
credit under permutation, so a small importance for one of them does not mean the information is
unused.

Writes model_importance.csv, model_partial_dependence.csv and slides/fig/22_model_explain.png.

Usage:  python3 model_explain.py      # after prediction_landmark.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402
from sklearn.inspection import partial_dependence  # noqa: E402
from sklearn.metrics import brier_score_loss  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402

K_HI, LAG, L_EVAL, REPEATS, B = 18, 2, 4, 20, 1000
rng = np.random.default_rng(0)
FEAT = ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals", "log_rate", "rate_missing", "crit",
        "both", "china", "k_fall", "since_fall", "depth", "latest", "slope", "zero_months", "rush",
        "uv_change", "uv_missing", "vote_confirmed", "vote_lifted", "vote_unknown", "L"]
LABEL = {"pre_share": "pre-case share", "pre_trend": "pre-case trend", "log_pre_value": "pre-case size",
         "hhi": "market concentration", "n_rivals": "number of rivals", "log_rate": "duty rate",
         "rate_missing": "rate missing", "crit": "retroactive duties", "both": "both kinds of duty",
         "china": "China", "k_fall": "month of the fall", "since_fall": "months since the fall",
         "depth": "depth of the fall", "latest": "latest share", "slope": "recent direction",
         "zero_months": "months with no imports", "rush": "pre-case rush", "uv_change": "price-per-unit change",
         "uv_missing": "price change missing", "vote_confirmed": "vote: duty confirmed",
         "vote_lifted": "vote: duty lifted", "vote_unknown": "vote: not yet", "L": "checkpoint month"}

D = pd.read_parquet("panel/landmark_features.parquet")


def cv_pick(tr, grid):
    gkf = GroupKFold(n_splits=min(5, tr.cluster.nunique()))
    best, bp = None, None
    for n in grid:
        sc = []
        for a, b in gkf.split(tr, groups=tr.cluster):
            m = fit(n, tr.iloc[a])
            sc.append(brier_score_loss(tr.y.iloc[b], m.predict_proba(tr.iloc[b][FEAT])[:, 1],
                                       sample_weight=tr.w.iloc[b]))
        if best is None or np.mean(sc) < best:
            best, bp = np.mean(sc), n
    return bp


def fit(n, tr):
    m = HistGradientBoostingClassifier(max_depth=2, learning_rate=0.05, max_iter=n, l2_regularization=1.0,
                                       min_samples_leaf=40, random_state=0)
    return m.fit(tr[FEAT], tr.y, sample_weight=tr.w)


GRID = [50, 100, 200, 400]
ref = pd.read_csv("prediction_landmark_heldout.csv", dtype={"hs8": str})
rows, base_all = [], []
for Y in sorted(D.year.unique()):
    te = D[D.year == Y]
    tr = D[(D.b + K_HI + LAG) < Y * 12].reset_index(drop=True)
    if te.sid.nunique() < 5 or tr.sid.nunique() < 40 or te.y.nunique() < 2:
        continue
    m = fit(cv_pick(tr, GRID), tr)
    full = m.predict_proba(te[FEAT])[:, 1]
    r_ = ref[ref.year == Y].boosting.to_numpy()
    assert np.abs(full - r_).max() < 1e-9, f"refit for {Y} does not reproduce prediction_landmark"
    w = 1.0 / te.groupby(["sid", "L"]).sid.transform("size").to_numpy()
    t4 = (te.L == L_EVAL).to_numpy()
    X4 = te[t4][FEAT].reset_index(drop=True)
    y4, w4, p4 = te.y.to_numpy()[t4], w[t4], full[t4]
    se_base = (p4 - y4) ** 2
    for f in FEAT:
        se = np.zeros(len(X4))
        for _ in range(REPEATS):
            Xp = X4.copy()
            Xp[f] = rng.permutation(Xp[f].to_numpy())
            se += (m.predict_proba(Xp)[:, 1] - y4) ** 2
        rows.append(pd.DataFrame(dict(feature=f, year=Y, cluster=te.cluster.to_numpy()[t4], w=w4,
                                      d=se / REPEATS - se_base)))
    print(f"  {Y}: {t4.sum()} month-4 rows scored")
print("check passed: refit yearly models reproduce prediction_landmark_heldout.csv")
R = pd.concat(rows, ignore_index=True)

out = []
for f, g in R.groupby("feature"):
    g = g.reset_index(drop=True)
    est = np.average(g.d, weights=g.w)
    cl = g.cluster.unique()
    idx = {c: np.flatnonzero(g.cluster.values == c) for c in cl}
    bs = []
    for _ in range(B):
        ii = np.concatenate([idx[c] for c in rng.choice(cl, len(cl), replace=True)])
        bs.append(np.average(g.d.values[ii], weights=g.w.values[ii]))
    out.append(dict(feature=f, label=LABEL[f], brier_increase=est, lo=np.quantile(bs, 0.05), hi=np.quantile(bs, 0.95)))
I = pd.DataFrame(out).sort_values("brier_increase", ascending=False)
I.to_csv("model_importance.csv", index=False)
print("\npermutation importance at month 4 (held out; Brier increase when shuffled):")
print(I.round(4).to_string(index=False))

# ---------------------------------------------------------------- partial dependence, one model on all cases
mall = fit(cv_pick(D.reset_index(drop=True), GRID), D)
X4 = D[D.L == L_EVAL][FEAT]
show = [f for f in I.feature if f not in ("L", "vote_unknown", "vote_confirmed", "vote_lifted")][:5]
if "log_rate" not in show:
    show.append("log_rate")
pdrows = []
for f in show:
    pdp = partial_dependence(mall, X4, [f], kind="average", grid_resolution=20, percentiles=(0.05, 0.95),
                             method="brute")
    for x, v in zip(pdp["grid_values"][0], pdp["average"][0]):
        pdrows.append(dict(feature=f, label=LABEL[f], x=x, chance_back=v))
PD = pd.DataFrame(pdrows)
PD.to_csv("model_partial_dependence.csv", index=False)

plt.rcParams.update({
    "font.family": "Avenir Next", "font.size": 12, "axes.titlesize": 13, "axes.grid": True,
    "grid.alpha": .22, "grid.color": "#6E737C", "axes.edgecolor": "#6E737C", "text.color": "#14161A",
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 200,
    "savefig.bbox": "tight", "savefig.facecolor": "white"})
RED, GREY, INK = "#C8102E", "#6E737C", "#14161A"
# axes in units a reader can follow; the inputs themselves stay as the model uses them
AXES = {
    "latest": ("latest share, as a share of its pre-case level", [0, 0.25, 0.5, 0.75, 1.0, 1.25],
               lambda v: f"{100 * v:.0f}%"),
    "rush": ("share just before the case, against its usual level", [0, 0.5, 1, 1.5, 2, 2.5],
             lambda v: f"{v:g}x"),
    "log_pre_value": ("imports from the country in the year before the case", np.log1p([1e4, 1e5, 1e6, 1e7]),
                      lambda v: {4: "$10k", 5: "$100k", 6: "$1M", 7: "$10M"}[round(np.log10(np.expm1(v)))]),
    "hhi": ("market concentration (0 = many suppliers, 1 = one)", [0.1, 0.3, 0.5, 0.7], lambda v: f"{v:g}"),
    "log_rate": ("preliminary duty rate", np.log1p([0, 10, 30, 100, 300]),
                 lambda v: f"{np.expm1(v):.0f}%"),
}
panels = [f for f in show if f in AXES][:5]
fig, axes = plt.subplots(2, 3, figsize=(15, 8.2))
ax0 = axes[0, 0]
top = I[~I.feature.isin(["L"])].head(8).iloc[::-1]
ax0.barh(top.label, top.brier_increase, color=RED, height=0.6)
ax0.errorbar(top.brier_increase, top.label, xerr=[top.brier_increase - top.lo, top.hi - top.brier_increase],
             fmt="none", ecolor=INK, elinewidth=1, capsize=2)
ax0.set_title("Which inputs matter", loc="left", fontweight="600")
ax0.set_xlabel("how much worse it predicts when shuffled\n(Brier score increase, 90% ranges)")
ax0.grid(axis="y", visible=False)
for ax, f in zip(axes.flat[1:], panels):
    g = PD[PD.feature == f]
    xlabel, ticks, fmt = AXES[f]
    ax.plot(g.x, 100 * g.chance_back, color=RED, lw=2.4)
    lo, hi = g.x.min(), g.x.max()
    t = [v for v in ticks if lo - 1e-9 <= v <= hi + 1e-9]
    ax.set_xticks(t)
    ax.set_xticklabels([fmt(v) for v in t])
    ax.set_xlabel(xlabel)
    ax.set_ylabel("chance of coming back (%)")
    ax.set_ylim(15, 85)  # one scale for every input, so the size of each effect compares honestly
    ax.set_title(LABEL[f][0].upper() + LABEL[f][1:], loc="left", fontweight="600")
for ax in axes.flat[1 + len(panels):]:
    ax.axis("off")
fig.suptitle("Month-4 forecast: what drives it (held out) and how the chance of coming back moves with each input",
             x=0.01, ha="left", fontweight="600", fontsize=14)
fig.tight_layout()
fig.savefig("slides/fig/22_model_explain.png")
print("wrote model_importance.csv, model_partial_dependence.csv, slides/fig/22_model_explain.png")
