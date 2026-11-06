"""Figures for the corrected AD/CVD results (stacked design, November 2026).

  12_order_vs_negative.png  targeted country vs rival suppliers, month by month, for cases that
                            became permanent orders, cases the ITC voted down, and the fake date
  13_recovery_km.png        of products whose position fell, the share back at the pre-case level
                            by months since the fall, real cases vs the fake date
  14_outcomes.png           what happened to each targeted product within 18 months, real vs fake

Palette is the deck's own: red for the focal series, ink for the comparison, grey dashed for the
fake-date baseline. Every line is labelled directly (grey is low-contrast on white, so it never
carries identity by colour alone).

Usage:  python3 slides/fig_stacked.py      # from the repo root, after adcvd_stacked.py,
                                           # itc_compare.py and recovery_benchmark.py
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, ".")
import recovery_benchmark as R  # noqa: E402

plt.rcParams.update({
    "font.family": "Avenir Next", "font.size": 14, "axes.titlesize": 16,
    "axes.labelsize": 14, "xtick.labelsize": 13, "ytick.labelsize": 13,
    "axes.grid": True, "grid.alpha": .22, "grid.color": "#6E737C", "grid.linewidth": 0.8,
    "axes.edgecolor": "#6E737C", "text.color": "#14161A",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white",
})
INK, GREY, RED, LRED, LGREY = "#14161A", "#6E737C", "#C8102E", "#E8A0AB", "#C9CDD2"
pct = lambda b: 100 * (np.exp(b) - 1)

# ---------------------------------------------------------------- 12: order vs negative
p = pd.read_csv("itc_compare_paths.csv")
p = p[p.outcome == "PPML value, zeros in"]
q = pd.read_csv("adcvd_stacked_paths.csv")
q = q[(q.outcome == "PPML value, zeros in") & (q["sample"] == "placebo, 24 months earlier")]
o = p[p["sample"] == "final stage: order"].set_index("k")
n = p[p["sample"] == "final stage: negative"].set_index("k")
f = q.set_index("k")

fig, ax = plt.subplots(figsize=(11, 4.8))
ax.axhline(0, color=GREY, lw=1)
ax.axvline(0, color=RED, ls=":", lw=1.4)
ax.fill_between(o.index, pct(o.coef - 1.96 * o.se), pct(o.coef + 1.96 * o.se), color=RED,
                alpha=.12, lw=0)
ax.plot(f.index, pct(f.coef), color=GREY, lw=2, ls="--")
ax.plot(n.index, pct(n.coef), color=INK, lw=2)
ax.plot(o.index, pct(o.coef), color=RED, lw=2.4)
end = o.index.max()
for s, lab, c, dy in [(o, "became a permanent duty", RED, 0), (n, "ITC found no injury", INK, 4),
                      (f, "fake date", GREY, -4)]:
    ax.annotate(lab, (end, pct(s.coef[end])), xytext=(8, dy), textcoords="offset points",
                va="center", color=c, fontweight="600", fontsize=13)
ax.annotate("duty starts", (0, 30), xytext=(5, 0), textcoords="offset points", color=RED,
            fontsize=12, fontweight="600", va="top")
ax.set_xlim(-12.5, 18.5)
ax.set_ylim(-50, 32)
ax.set_xlabel("months from the month duties start being collected")
ax.set_ylabel("targeted country vs rivals\nselling the same product, %")
ax.set_title("The targeted country loses ground in cases that became permanent duties",
             loc="left", fontweight="600")
fig.savefig("slides/fig/12_order_vs_negative.png")
plt.close(fig)
print("wrote slides/fig/12_order_vs_negative.png")

# ---------------------------------------------------------------- 13: recovery curve
real = pd.read_csv("recovery_pairs_real_fall20.csv", dtype={"hs8": str})
plac = pd.read_csv("recovery_pairs_placebo_fall20.csv", dtype={"hs8": str})
kr, kp = R.km(real), R.km(plac)
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.step(kp.index, 100 * kp.values, where="post", color=GREY, lw=2, ls="--")
ax.step(kr.index, 100 * kr.values, where="post", color=RED, lw=2.4)
for s, lab, c in [(kr, "real cases", RED), (kp, "fake date", GREY)]:
    ax.annotate(f"{lab}: {100 * s[18]:.0f}%", (18, 100 * s[18]), xytext=(8, 0),
                textcoords="offset points", va="center", color=c, fontweight="600", fontsize=13)
ax.set_xlim(0, 18.5)
ax.set_ylim(0, 70)
ax.set_xticks([0, 3, 6, 9, 12, 15, 18])
ax.set_xlabel("months since the targeted country's share first fell by a fifth")
ax.set_ylabel("share of those products back\nat their pre-case level, %")
ax.set_title("Of the products that fall, about one in four is back within 18 months of falling",
             loc="left", fontweight="600")
fig.savefig("slides/fig/13_recovery_km.png")
plt.close(fig)
print("wrote slides/fig/13_recovery_km.png")

# ---------------------------------------------------------------- 14: outcome shares
b = pd.read_csv("recovery_benchmark_fall20.csv")
cats = ["no fall", "recovered", "not recovered", "exited"]
labels = {"no fall": "did not fall", "recovered": "fell, came back",
          "not recovered": "fell, still down", "exited": "stopped trading"}
cols = {"no fall": LGREY, "recovered": "#9BA1A9", "not recovered": LRED, "exited": RED}
txt = {"no fall": INK, "recovered": INK, "not recovered": INK, "exited": "white"}
fig, ax = plt.subplots(figsize=(11, 3.2))
rows = [("real cases", "real"), ("fake date", "placebo")]
for i, (lab, s) in enumerate(rows):
    left = 0
    for c in cats:
        v = 100 * float(b[(b["sample"] == s) & (b.measure == c)].value.iloc[0])
        ax.barh(i, v - 0.4, left=left + 0.2, color=cols[c], height=0.62, edgecolor="white", lw=0)
        if v >= 3:
            ax.text(left + v / 2, i, f"{v:.0f}%", ha="center", va="center", color=txt[c],
                    fontsize=13 if v >= 6 else 11, fontweight="600")
        left += v
ax.set_yticks([0, 1])
ax.set_yticklabels([r[0] for r in rows])
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xticks([])
ax.grid(False)
for sp in ["left", "bottom"]:
    ax.spines[sp].set_visible(False)
ax.tick_params(left=False)
x = 0
for c in cats:
    v = 100 * float(b[(b["sample"] == "real") & (b.measure == c)].value.iloc[0])
    ax.text(x + v / 2, -0.42, labels[c], ha="center", va="bottom", color=INK, fontsize=12)
    x += v
ax.set_title("What happened to each targeted product within 18 months", loc="left",
             fontweight="600", pad=34)
fig.savefig("slides/fig/14_outcomes.png")
plt.close(fig)
print("wrote slides/fig/14_outcomes.png")

# ---------------------------------------------------------------- 15: decision points
# improvement over the historical rate (held-out Brier, positive = better), 90 percent interval
pt = pd.read_csv("prediction_test.csv").set_index("year").loc["pooled"]
bs = pd.read_csv("prediction_test_bootstrap.csv").brier_improvement
s2 = pd.read_csv("prediction_stage2.csv").set_index(["point", "model"])
rows = [("on the day the duty starts", pt.brier_benchmark - pt.brier_model, *bs.quantile([.05, .95]),
         pt.auc_model, "logistic"),
        ("when the fall first shows", *s2.loc[("fall", "boosting"), ["gain_vs_history", "lo_vs_history",
                                                                     "hi_vs_history", "auc"]], "boosting"),
        ("at the ITC's final vote", *s2.loc[("ITC", "logit, + vote"), ["gain_vs_history", "lo_vs_history",
                                                                       "hi_vs_history", "auc"]], "logistic")]
fig, ax = plt.subplots(figsize=(11, 3.6))
ax.axvline(0, color=GREY, lw=1)
for i, (lab, g, lo, hi, auc, mod) in enumerate(rows):
    c = RED if lo > 0 else GREY
    ax.plot([lo, hi], [i, i], color=c, lw=2.4, solid_capstyle="round")
    ax.plot(g, i, "o", ms=10, color=c, mec="white", mew=2)
    ax.annotate(f"ranks correctly {100 * auc:.0f}% of the time ({mod})", (hi, i), xytext=(10, 0),
                textcoords="offset points", va="center", color=INK, fontsize=12)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in rows])
ax.invert_yaxis()
ax.set_ylim(len(rows) - 0.5, -0.6)
ax.set_xlim(-0.01, 0.09)
ax.grid(axis="y", visible=False)
ax.tick_params(left=False)
ax.spines["left"].set_visible(False)
ax.set_xlabel("drop in Brier score against the historical rate (further right is better), 90% range")
ax.set_title("A few months in, a model beats the historical rates", loc="left", fontweight="600")
fig.savefig("slides/fig/15_decision_points.png")
plt.close(fig)
print("wrote slides/fig/15_decision_points.png")

# ---------------------------------------------------------------- 16: the lookup
from matplotlib.colors import LinearSegmentedColormap, to_rgb  # noqa: E402

L = pd.read_csv("calibrated_lookup.csv")
# neutral ramp: in this deck red means losing ground, and here a darker cell means more came back
ramp = LinearSegmentedColormap.from_list("grey", ["#FFFFFF", "#3A3F47"])
panels = [("fall", "When the fall first shows", ["under $1M", "$1M to $10M", "over $10M"],
           ["rate up to 25%", "rate over 25%", "rate not published"],
           "supplier's imports, year before", "preliminary duty rate"),
          ("ITC", "At the ITC's final vote", ["under half", "half to 4/5", "4/5 or more"],
           ["duty confirmed", "duty lifted"], "latest share against its pre-case level", "ITC vote")]
fig, axes = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [3, 2.2]})
for ax, (pt, title, rows_, cols_, rlab, clab) in zip(axes, panels):
    x = L[L.point == pt]
    for i, r in enumerate(rows_):
        for j, c in enumerate(cols_):
            v = x[(x.row == r) & (x.col == c)].iloc[0]
            val = v.came_back
            col = ramp(0.08 + 0.92 * val)
            ax.add_patch(plt.Rectangle((j + 0.03, i + 0.03), 0.94, 0.94, color=col, lw=0))
            lum = np.dot(to_rgb(col), [0.299, 0.587, 0.114])
            tc = "white" if lum < 0.55 else INK
            ax.text(j + 0.5, i + 0.42, f"{100 * val:.0f}", ha="center", va="center", fontsize=20,
                    fontweight="600", color=tc)
            ax.text(j + 0.5, i + 0.75, f"model {100 * v.expected:.0f}, {v.cases} cases", ha="center",
                    va="center", fontsize=10, color=tc)
    ax.set_xlim(0, len(cols_))
    ax.set_ylim(len(rows_), 0)
    ax.set_xticks([j + 0.5 for j in range(len(cols_))])
    ax.set_xticklabels(cols_, fontsize=11)
    ax.set_yticks([i + 0.5 for i in range(len(rows_))])
    ax.set_yticklabels([r.replace("$", r"\$") for r in rows_], fontsize=11)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xlabel(clab, fontsize=11, color=GREY)
    ax.set_ylabel(rlab, fontsize=11, color=GREY)
    ax.set_title(title, loc="left", fontsize=13, fontweight="600", pad=26)
fig.suptitle("Of 100 products that fell, how many came back by month 18 (held-out years)", x=0.01,
             ha="left", fontweight="600", fontsize=15)
fig.tight_layout()
fig.savefig("slides/fig/16_lookup.png")
plt.close(fig)
print("wrote slides/fig/16_lookup.png")

# ---------------------------------------------------------------- 17: Section 301 outcomes
B3 = pd.read_csv("s301_benchmark.csv")
rows3 = [("China, Section 301", "Section 301, real"), ("same products, fake date", "Section 301, placebo"),
         ("antidumping cases", "AD/CVD, same horizon")]
fig, ax = plt.subplots(figsize=(11, 3.6))
for i, (lab, s) in enumerate(rows3):
    left = 0
    for c in cats:
        v = 100 * float(B3[(B3["sample"] == s) & (B3.measure == c)].value.iloc[0])
        ax.barh(i, v - 0.4, left=left + 0.2, color=cols[c], height=0.62, edgecolor="white", lw=0)
        if v >= 3:
            ax.text(left + v / 2, i, f"{v:.0f}%", ha="center", va="center", color=txt[c],
                    fontsize=13 if v >= 6 else 11, fontweight="600")
        left += v
ax.set_yticks(range(len(rows3)))
ax.set_yticklabels([r[0] for r in rows3])
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_xticks([])
ax.grid(False)
for sp in ["left", "bottom"]:
    ax.spines[sp].set_visible(False)
ax.tick_params(left=False)
x = 0
lab3 = dict(labels, exited="no late imports")
for c in cats:
    v = 100 * float(B3[(B3["sample"] == "Section 301, real") & (B3.measure == c)].value.iloc[0])
    ax.text(x + v / 2, -0.42, lab3[c], ha="center", va="bottom", color=INK, fontsize=12)
    x += v
ax.set_title("What happened to each taxed product within 16 months", loc="left", fontweight="600", pad=34)
fig.savefig("slides/fig/17_s301_outcomes.png")
plt.close(fig)
print("wrote slides/fig/17_s301_outcomes.png")
