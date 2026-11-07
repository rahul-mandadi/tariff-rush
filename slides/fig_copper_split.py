"""Copper, split into the part the duty taxed and the part it did not.

The total copper line (01_context.png) rushes before the 2025 Section 232 duty, crashes, then
climbs back to new highs, which reads as "borrowed": the business came back. It did not, for the
part that was taxed. Proclamation 10962 taxed semi-finished copper (headings 7407 to 7413) and,
in paragraph 8, left refined cathodes (74031100) untaxed as an input material. Split that way,
the taxed series falls to about half its old level and stays there; the untaxed series is what
recovers.

One product and one action, with no placebo, so this is an illustration of the question rather
than a result. The monthly lines are drawn in full rather than as window averages so the shape is
visible and nothing depends on the chosen windows. Kilogram-reported rows only, as in
copper_split.py, which prints the window averages quoted in REPORT1.md.

Usage:  python3 slides/fig_copper_split.py      # from the repo root
"""
import glob

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams.update({"font.family": "Avenir Next", "font.size": 13,
                     "figure.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white",
                     "axes.spines.top": False, "axes.spines.right": False})
INK, GREY, RED = "#14161A", "#6E737C", "#C8102E"

SEMI = ["7407", "7408", "7409", "7410", "7411", "7412", "7413"]
CATH = "74031100"

rows = []
for f in sorted(glob.glob("panel/hs8/*.parquet")):
    d = pd.read_parquet(f, columns=["hs8", "qty", "unit"])
    d = d[d.unit == "KG"]
    h = d[d.hs8.astype(str).str.startswith("74")]
    hd = h.hs8.astype(str).str[:4]
    rows.append(dict(ym=pd.Timestamp(f.split("/")[-1][:7] + "-01"),
                     taxed=h[hd.isin(SEMI)].qty.sum() / 1e6,
                     untaxed=h[h.hs8.astype(str) == CATH].qty.sum() / 1e6))
s = pd.DataFrame(rows).set_index("ym").loc["2023-01":]

fig, ax = plt.subplots(figsize=(11, 4.6))
ax.plot(s.index, s.untaxed, color=GREY, lw=2.6)
ax.plot(s.index, s.taxed, color=RED, lw=2.6)
last = s.index[-1]
ax.annotate("not taxed: refined cathodes", (last, s.untaxed.iloc[-1]), xytext=(8, 0),
            textcoords="offset points", va="center", color=GREY, fontweight="600")
ax.annotate("taxed: wire, tubes, sheets", (last, s.taxed.iloc[-1]), xytext=(8, 0),
            textcoords="offset points", va="center", color=RED, fontweight="600")
# the two dates are five months apart, so the labels sit on opposite sides of their lines
for d, lab, ha in [("2025-02-25", "investigation\nordered ", "right"),
                   ("2025-08-01", " 50% duty\n starts", "left")]:
    ax.axvline(pd.Timestamp(d), color=INK, ls=":", lw=1.4)
    ax.text(pd.Timestamp(d), ax.get_ylim()[1] * 0.97, lab, va="top", ha=ha, fontsize=11, color=INK)
ax.set_ylabel("thousand tonnes a month")
ax.set_ylim(0, None)
ax.set_title("Copper imports, split by whether the 2025 duty taxed them", loc="left",
             fontweight="600", fontsize=15)
ax.grid(axis="y", color="#E3E5E8", lw=0.8)
fig.savefig("slides/fig/11_copper_split.png")
print("wrote slides/fig/11_copper_split.png")
b, a = s.loc["2024-08":"2025-01"], s.loc["2026-03":"2026-08"]
print(f"taxed   {b.taxed.mean():.0f} -> {a.taxed.mean():.0f} kt/month ({a.taxed.mean()/b.taxed.mean():.2f}x)")
print(f"untaxed {b.untaxed.mean():.0f} -> {a.untaxed.mean():.0f} kt/month ({a.untaxed.mean()/b.untaxed.mean():.2f}x)")
