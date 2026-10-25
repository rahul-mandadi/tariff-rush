"""Figure: what happens to the named country's imports around an antidumping case.

k = 0 is the month duties start being collected; the baseline is k in [-18,-13]. Product-month
and product-origin fixed effects mean each point is the named country relative to other suppliers
of the same product in the same month, not a level series.

The shape matters more than any single number, and it is not the one we expected. Imports from
the named country are already about 37 percent above baseline a year out and still climbing to
k = -5. They then fall steadily, cross baseline two months after duties start, and stay there.

Two readings follow. There is no rush: the decline begins long before the duty, which fits the
fact that these duties can be applied retroactively to the initiation notice, so buying ahead
buys nothing. And the elevated pre-period is not noise, it is part of the story, because a surge
in imports is often what triggers the petition in the first place.

Usage:  python3 slides/fig_event.py      # from the repo root
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    "font.family": "Avenir Next", "font.size": 13, "axes.titlesize": 15,
    "axes.labelsize": 12, "xtick.labelsize": 12, "ytick.labelsize": 12,
    "axes.grid": True, "grid.alpha": .22, "grid.color": "#6E737C",
    "axes.edgecolor": "#6E737C", "text.color": "#14161A",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white",
})
INK, GREY, RED, PALE = "#14161A", "#6E737C", "#C8102E", "#D4D8DC"

d = pd.read_csv("adcvd_event_study.csv")
q = pd.read_csv("adcvd_event_study_placebo.csv")
# the point estimates are 100*(exp(coef)-1), so the interval has to be transformed the same way
lo = 100 * (np.exp(d.coef - 1.96 * d.se) - 1)
hi = 100 * (np.exp(d.coef + 1.96 * d.se) - 1)

fig, ax = plt.subplots(figsize=(10, 4.6))
ax.fill_between(d.k, lo, hi, color=PALE, alpha=.75, lw=0)
ax.plot(q.k, q.pct, lw=2.0, color=GREY, ls="--", label="placebo, same events 24 months earlier")
ax.plot(d.k, d.pct, lw=2.6, color=INK, label="real events")
ax.axhline(0, color=GREY, lw=1.0)
ax.axvline(0, color=RED, ls="--", lw=1.6)
ax.annotate("duties start", (0, 62), xytext=(6, 0), textcoords="offset points",
            color=RED, fontsize=12, fontweight="600", va="top")
ax.set_xlabel("months relative to the month duties start being collected")
ax.set_ylabel("named country vs other suppliers\nof the same product, %")
ax.set_title("The named country loses ground after a duty; the placebo does not")
ax.set_xlim(-12.5, 18.5); ax.set_ylim(-20, 68)
ax.legend(fontsize=11, loc="lower left", frameon=True, framealpha=.95)
fig.savefig("slides/fig/10_event.png")
print("wrote slides/fig/10_event.png")
pre = lambda x: x[x.k.between(-12,-4)].pct.mean()
post = lambda x: x[x.k.between(0,18)].pct.mean()
print(f"real    {pre(d):+.0f}% before -> {post(d):+.0f}% after")
print(f"placebo {pre(q):+.0f}% before -> {post(q):+.0f}% after")
