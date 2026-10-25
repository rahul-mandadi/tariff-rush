"""Figure: what happens to the named country's imports around an antidumping case.

673 events. k = 0 is the month duties start being collected; the baseline is k in [-18,-13], so
every point is read against the level eighteen months to just over a year before duties.

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
lo = 100 * ((1 + d.coef - 1.96 * d.se).clip(lower=0.01) - 1)
hi = 100 * ((1 + d.coef + 1.96 * d.se) - 1)

fig, ax = plt.subplots(figsize=(10, 4.8))
ax.axhspan(-100, 200, xmin=0, xmax=0, color="none")
ax.fill_between(d.k, lo, hi, color=PALE, alpha=.75, lw=0)
ax.plot(d.k, d.pct, lw=2.6, color=INK)
ax.axhline(0, color=GREY, lw=1.2)
ax.axvline(0, color=RED, ls="--", lw=1.6)
ax.annotate("duties start\nbeing collected", (0, 46), xytext=(6, 0),
            textcoords="offset points", color=RED, fontsize=12, fontweight="600", va="top")
ax.annotate("already 37% above baseline\na year before duties", (-12, 36.8), xytext=(10, -34),
            textcoords="offset points", color=INK, fontsize=11.5, fontweight="600")
ax.set_xlabel("months relative to the month duties start being collected")
ax.set_ylabel("imports from the named\ncountry, % vs baseline")
ax.set_title("Antidumping duties: the fall begins long before the duty, and does not reverse")
ax.set_xlim(-12.5, 18.5); ax.set_ylim(-18, 55)
fig.savefig("slides/fig/10_event.png")
print("wrote slides/fig/10_event.png")
print(f"k=-12 {d.pct.iloc[0]:+.1f}%   k=0 {d[d.k==0].pct.iloc[0]:+.1f}%   "
      f"k=+6 {d[d.k==6].pct.iloc[0]:+.1f}%   k=+18 {d[d.k==18].pct.iloc[0]:+.1f}%")
