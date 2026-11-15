"""The review-list test at every capacity from 5 to 50 percent, and at months 6 and 8 (items 4 and 6).

Reads:  prediction_landmark_heldout.csv, review_queue_eval.csv
Writes: review_queue_capacity.csv, review_queue_checkpoints.csv, slides/fig/21_capacity_curve.png
Run:    python3 forecast/review_queue_curves.py
        (after forecast/review_queue.py; stops if it does not reproduce review_queue_eval.csv
        at 20 percent)
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, ".")  # the shared modules are at the repo root
import modeling as M  # noqa: E402

B = 1000
CAPS = [round(0.05 * i, 2) for i in range(1, 11)]
CHECKPOINTS = [4, 6, 8]
rng = np.random.default_rng(0)

H = pd.read_csv("prediction_landmark_heldout.csv", dtype={"hs8": str})
RANKS = {"forecast (boosting)": lambda g: 1 - g.boosting, "logistic": lambda g: 1 - g.logistic,
         "latest share": lambda g: -g.latest, "historical rate": lambda g: 1 - g.history}


def measures(g, caps):
    """{(ranking, cap): (share of reviewed not back, share of not-back reviewed)} plus the ceiling."""
    down = 1 - g.y.to_numpy()
    qi = list(g.groupby("queue").indices.values())
    out = {}
    for name, f in RANKS.items():
        s = f(g).to_numpy()
        for cap in caps:
            r = np.zeros(len(g))
            for ix in qi:
                r[ix] = M.review_shares(s[ix], cap)
            out[(name, cap)] = ((r * down).sum() / r.sum(), (r * down).sum() / down.sum())
    for cap in caps:
        out[("ceiling", cap)] = (np.nan, sum(min(cap * len(ix), down[ix].sum()) for ix in qi) / down.sum())
    return out


def run(L, caps):
    g = H[H.L == L].reset_index(drop=True)
    g["queue"] = g.b + L
    pt = measures(g, caps)
    cl = g.cluster.unique()
    idx = {c: np.flatnonzero(g.cluster.values == c) for c in cl}
    boot = [measures(g.iloc[np.concatenate([idx[c] for c in rng.choice(cl, len(cl), replace=True)])]
                     .reset_index(drop=True), caps) for _ in range(B)]
    rows = []
    for cap in caps:
        for name in RANKS:
            p = np.array([b[(name, cap)][0] for b in boot])
            row = dict(L=L, capacity=cap, ranking=name, precision=pt[(name, cap)][0], lo=np.quantile(p, 0.05),
                       hi=np.quantile(p, 0.95), capture=pt[(name, cap)][1], ceiling=pt[("ceiling", cap)][1],
                       relationships=len(g), cases=g.sid.nunique(), groups=g.cluster.nunique(),
                       not_back=1 - g.y.mean())
            if name != "latest share":
                d = p - np.array([b[("latest share", cap)][0] for b in boot])
                row.update(vs_latest=pt[(name, cap)][0] - pt[("latest share", cap)][0],
                           vs_latest_lo=np.quantile(d, 0.05), vs_latest_hi=np.quantile(d, 0.95))
            rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- item 4: capacity curve at month 4
C4 = run(4, CAPS)
ref = pd.read_csv("review_queue_eval.csv")
ref = ref[(ref.weighting == "relationship") & (ref.capacity == 0.2) & (ref.measure == "precision")].set_index("ranking")
for name in RANKS:
    got = C4[(C4.capacity == 0.2) & (C4.ranking == name)].precision.iloc[0]
    assert abs(got - ref.value[name]) < 1e-12, (name, got, ref.value[name])
print("check passed: 20 percent at month 4 reproduces review_queue_eval.csv")
C4.to_csv("review_queue_capacity.csv", index=False)

# ---------------------------------------------------------------- item 6: months 6 and 8 at 20 percent
CK = pd.concat([run(L, [0.2]) for L in CHECKPOINTS], ignore_index=True)
CK.to_csv("review_queue_checkpoints.csv", index=False)

pd.set_option("display.width", 220)
show = ["capacity", "ranking", "precision", "lo", "hi", "capture", "ceiling", "vs_latest", "vs_latest_lo", "vs_latest_hi"]
print("\nitem 4, month 4, by capacity:")
print(C4[C4.ranking.isin(["forecast (boosting)", "latest share", "historical rate"])][show].round(3).to_string(index=False))
print("\nitem 6, at 20 percent, by checkpoint:")
print(CK[["L", "relationships", "cases", "groups", "not_back"] + show[1:]].round(3).to_string(index=False))

# ---------------------------------------------------------------- figure
plt.rcParams.update({
    "font.family": "Avenir Next", "font.size": 14, "axes.titlesize": 16, "axes.labelsize": 14,
    "xtick.labelsize": 13, "ytick.labelsize": 13, "axes.grid": True, "grid.alpha": .22,
    "grid.color": "#6E737C", "axes.edgecolor": "#6E737C", "text.color": "#14161A",
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 200,
    "savefig.bbox": "tight", "savefig.facecolor": "white"})
INK, GREY, RED, LGREY = "#14161A", "#6E737C", "#C8102E", "#C9CDD2"
fig, ax = plt.subplots(figsize=(11, 4.4))
for name, c, ls, lab in [("forecast (boosting)", RED, "-", "forecast"), ("latest share", GREY, "--", "latest share"),
                         ("historical rate", LGREY, ":", "random order (historical rate)")]:
    v = C4[C4.ranking == name]
    x = 100 * v.capacity
    if name != "historical rate":
        ax.fill_between(x, 100 * v.lo, 100 * v.hi, color=c, alpha=0.12, lw=0)
    ax.plot(x, 100 * v.precision, color=c, ls=ls, lw=2.4, marker="o", ms=5)
    ax.annotate(lab, (x.iloc[-1], 100 * v.precision.iloc[-1]), xytext=(8, 0), textcoords="offset points",
                va="center", color=c if name != "historical rate" else GREY, fontweight="600", fontsize=12)
ax.axvline(20, color=GREY, lw=1, ls=":")
ax.text(20.5, 51, "main (20%)", color=GREY, fontsize=11)
ax.set_xlim(4, 66)
ax.set_ylim(50, 100)
ax.set_xticks(100 * np.array(CAPS))
ax.set_xlabel("share of each month's list the team reviews (assumed)")
ax.set_ylabel("reviewed relationships that\nstayed down by month 18 (%)")
ax.set_title("Month 4, held out 2020 to 2025: the forecast stays ahead at every capacity (90% ranges shaded)",
             loc="left", fontweight="600", fontsize=13)
fig.savefig("slides/fig/21_capacity_curve.png")
print("wrote review_queue_capacity.csv, review_queue_checkpoints.csv, slides/fig/21_capacity_curve.png")
