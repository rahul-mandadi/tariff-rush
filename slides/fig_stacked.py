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
