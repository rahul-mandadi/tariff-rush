"""Sankey: what a tariff action actually names inside the chapter it touches.

Kylie Bemis suggested this in the presentation on 2026-10-16, to show "what these different
chapters are and what things are actually affected". Copper is the right case because it is the
example the deck already uses, and because the answer is counter-intuitive: the 50 percent duty
missed two thirds of the chapter by value.

The split comes from Proclamation 10962 itself, not from a parsed annex. Paragraph 1 applies the
duty to "semi-finished copper products and intensive copper derivative products, as set forth in
the Annex". Paragraph 8 handles "copper input materials and high-quality copper scrap"
separately, under the Defense Production Act, with no tariff. The annex table is not in the
Federal Register text we hold, so headings are assigned to those two categories by their standard
meaning and the figure says so. Treat the shares as close, not exact.

Usage:  python3 slides/fig_sankey.py      # from the repo root
"""
import glob

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle

plt.rcParams.update({"font.family": "Avenir Next", "font.size": 12,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white"})
INK, GREY, RED, PALE = "#14161A", "#6E737C", "#C8102E", "#D4D8DC"

LABEL = {"7401": "mattes", "7402": "unrefined", "7403": "refined copper and cathodes",
         "7404": "waste and scrap", "7405": "master alloys", "7406": "powders",
         "7407": "bars and rods", "7408": "wire", "7409": "plates and sheets",
         "7410": "foil", "7411": "tubes and pipes", "7412": "fittings",
         "7413": "stranded wire", "7415": "fasteners", "7418": "household articles",
         "7419": "other articles"}
# paragraph 8 of the proclamation: input materials and scrap, no duty
INPUTS = {"7401", "7402", "7403", "7404", "7405", "7406"}

rows = [pd.read_parquet(f, columns=["hs8", "value"]) for f in sorted(glob.glob("panel/hs8/2025-*.parquet"))]
cu = pd.concat(rows)
cu = cu[cu.hs8.astype(str).str.startswith("74")]
cu["hd"] = cu.hs8.astype(str).str[:4]
g = cu.groupby("hd").value.sum().sort_values(ascending=False)
g = g[g > 0]
# order the left column named-first, then inputs, so the ribbons run parallel instead of
# crossing: the right column is in the same order
g = pd.concat([g[[h for h in g.index if h not in INPUTS]],
               g[[h for h in g.index if h in INPUTS]]])
tot = g.sum()
named = g[[h for h in g.index if h not in INPUTS]].sum()

def ribbon(ax, x0, y0, x1, y1, h0, h1, color, alpha):
    """A bezier flow from (x0,y0) of thickness h0 to (x1,y1) of thickness h1."""
    xm = (x0 + x1) / 2
    verts = [(x0, y0), (xm, y0), (xm, y1), (x1, y1),
             (x1, y1 - h1), (xm, y1 - h1), (xm, y0 - h0), (x0, y0 - h0), (x0, y0)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="none", alpha=alpha))

fig, ax = plt.subplots(figsize=(11, 4.4))
GAP, XL, XR, W = 0.012, 0.06, 0.74, 0.035

# left column: one block per heading, biggest first
ytop = 1.0
left = {}
for hd, v in g.items():
    h = v / tot * (1 - GAP * (len(g) - 1))
    left[hd] = (ytop, h)
    ax.add_patch(Rectangle((XL, ytop - h), W, h,
                           facecolor=GREY if hd in INPUTS else RED, edgecolor="none"))
    if v / tot > 0.012:
        ax.text(XL - 0.012, ytop - h / 2, f"{LABEL.get(hd, hd)}  {100*v/tot:.0f}%",
                ha="right", va="center", fontsize=12,
                color=INK, fontweight="600" if hd not in INPUTS else "normal")
    ytop -= h + GAP

# right column: two destinations
rt = {}
y = 1.0
for key, val, col in [("named", named, RED), ("not", tot - named, GREY)]:
    h = val / tot * (1 - GAP)
    rt[key] = [y, h, y]
    ax.add_patch(Rectangle((XR, y - h), W, h, facecolor=col, edgecolor="none"))
    y -= h + GAP

ax.text(XR + W + 0.015, rt["named"][0] - rt["named"][1] / 2,
        f"named by the 50% duty\n{100*named/tot:.0f}% of the chapter",
        ha="left", va="center", fontsize=12, color=RED, fontweight="600")
ax.text(XR + W + 0.015, rt["not"][0] - rt["not"][1] / 2,
        f"not named: inputs and scrap\n{100*(tot-named)/tot:.0f}% of the chapter",
        ha="left", va="center", fontsize=12, color=GREY, fontweight="600")

for hd, v in g.items():
    y0, h0 = left[hd]
    key = "not" if hd in INPUTS else "named"
    col = GREY if hd in INPUTS else RED
    h1 = v / tot * (1 - GAP)
    ribbon(ax, XL + W, y0, XR, rt[key][2], h0, h1, col, 0.30)
    rt[key][2] -= h1

ax.set_xlim(-0.22, 1.16); ax.set_ylim(-0.02, 1.10); ax.axis("off")
ax.set_title("Copper, 2025: the tariff named less than a third of the chapter by value",
             fontsize=15, fontweight="600", loc="left", x=-0.20)
# the provenance note lives in the report figcaption, not burned into the image at 3pt
fig.savefig("slides/fig/09_sankey.png")
print(f"wrote slides/fig/09_sankey.png")
print(f"chapter 74 2025: ${tot/1e9:.1f}bn, named {100*named/tot:.1f}%, not named {100*(tot-named)/tot:.1f}%")
