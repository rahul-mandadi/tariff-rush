"""Figure: the same chapters, ranked on dollars and on quantity.

Kylie Bemis asked for Fig. 4 in kilograms. The honest answer is not a redrawn ranking but a
comparison, because neither measure is right on its own: dollars confuse a price rise with a
volume surge (cocoa), quantity confuses a mix shift with no surge at all (pharmaceuticals).
Showing both at once is the finding.

Deliberately no colour split by "is this a tariff story". That was a judgement call in the
presentation version and it did not hold up when she looked at it. Interpretation belongs in
the text, where it can be hedged; the figure shows what was measured.

Usage:  python3 slides/fig_units.py      # from the repo root
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    "font.family": "Avenir Next", "font.size": 16, "axes.titlesize": 18,
    "axes.labelsize": 16, "xtick.labelsize": 16, "ytick.labelsize": 17,
    "axes.grid": True, "grid.alpha": .22, "grid.color": "#6E737C",
    "axes.edgecolor": "#6E737C", "text.color": "#14161A",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white",
})
INK, GREY, RED = "#14161A", "#9BA1A9", "#C8102E"

NAMES = {"01": "live animals", "05": "animal products", "09": "coffee & spices",
         "12": "oil seeds", "18": "cocoa", "29": "organic chemicals", "30": "pharmaceuticals",
         "41": "hides & leather", "43": "furskins", "45": "cork", "48": "paper", "50": "silk",
         "74": "copper", "78": "lead", "80": "tin", "84": "machinery", "91": "clocks"}


def expected(s, cut="2024-12"):
    pre = np.log(s[:cut])
    me = pre.groupby(pre.index.month).mean() - pre.mean()
    t = np.arange(len(pre))
    slope, intercept = np.polyfit(t[-36:], pre.values[-36:], 1)
    pred = np.exp(pre.values[-1] + slope * (np.arange(len(s)) - (len(pre) - 1))
                  + s.index.month.map(me).values)
    resid = pre.values - (intercept + slope * t) - pre.index.month.map(me).values
    return pd.Series(pred, index=s.index), float(np.std(resid, ddof=1))


def ratios(df, col):
    out = {}
    for ch, g in df.groupby("chapter"):
        s = g.set_index("ym")[col].sort_index()
        s = s[s > 0]
        if len(s) < 100 or s[:"2024-12"].min() <= 0:
            continue
        if str(ch).zfill(2) in ('98', '99'):
            continue   # customs special provisions, not product categories
        pred, sd = expected(s)
        # Deviation in logs so it is on the same scale as sd, which is a log-residual standard
        # deviation: a score of 1.0 now means the month touched the upper edge of the historical
        # variability band drawn around the expected line (1.96 x residual sd; not a validated
        # forecast interval). The earlier (s / pred - 1) divided a percentage
        # by a log quantity; ranks barely move (Spearman 0.998) but the scores were inflated.
        dev = (np.log(s) - np.log(pred)).loc["2025-01":"2025-08"]
        if dev.empty or sd == 0:
            continue
        out[ch] = dev.max() / (1.96 * sd)
    return pd.Series(out)


d = pd.read_csv("eda/chapter_month_qty.csv", parse_dates=["ym"])
d["chapter"] = d.chapter.astype(str).str.zfill(2)
cmp = pd.DataFrame({"qty": ratios(d, "qty"), "dollars": ratios(d, "value")}).dropna()

# show the chapters that reach the top on either measure, so the reversals are visible
keep = sorted(set(cmp.nlargest(7, "qty").index) | set(cmp.nlargest(7, "dollars").index))
c = cmp.loc[keep].sort_values("qty")
lab = [NAMES.get(i, i) for i in c.index]
y = np.arange(len(c))

fig, ax = plt.subplots(figsize=(13.5, 5.4))
ax.hlines(y, c.dollars, c.qty, color="#D4D8DC", lw=3, zorder=1)
ax.scatter(c.dollars, y, s=95, color=GREY, zorder=3, label="measured in dollars")
ax.scatter(c.qty, y, s=95, color=INK, zorder=3, label="measured in quantity")
ax.axvline(1, color=RED, ls=":", lw=1.6, zorder=2)
# the x-axis label already says 1.0 is the edge of normal; a label here sat on copper's dots
ax.set_yticks(y); ax.set_yticklabels(lab)
ax.set_xlabel("how far outside its own normal range the chapter went in 2025\n"
              "(1.0 = just reaching the edge of normal)")
ax.set_title("Dollars and quantity disagree about which chapters moved")
# the rightmost point is pharmaceuticals on dollars, so the legend cannot sit bottom-right
ax.legend(fontsize=14, loc="center right", frameon=True, framealpha=.95)
fig.savefig("slides/fig/08_units.png")
print("wrote slides/fig/08_units.png")

print(f"\nchapters shown: {len(c)}")
print("largest disagreements:")
c2 = cmp.assign(gap=(cmp.qty - cmp.dollars)).reindex(keep)
for i, r in c2.reindex(c2.gap.abs().sort_values(ascending=False).index).head(6).iterrows():
    print(f"  {NAMES.get(i,i):<18} dollars {r.dollars:+.2f}   quantity {r.qty:+.2f}   gap {r.gap:+.2f}")
