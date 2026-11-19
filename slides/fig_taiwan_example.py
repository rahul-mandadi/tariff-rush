"""Figure: one relationship, Taiwan epoxy resins (3907.30.00), as an analyst could see it in January 2025.

Reads:  panel/adcvd_stacks_decision.parquet, recovery_pairs_decision_fall20.csv, results/review_queue_watchlist.csv
Writes: slides/fig/26_taiwan_example.png
Run:    python3 slides/fig_taiwan_example.py      (after forecast/review_queue.py)
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, ".")  # the shared modules are at the repo root
import modeling as M  # noqa: E402

SID, HS8, MONTH, SEEN = 468, "39073000", "2025-01", 2  # month-4 list; Census data through month 2

# the share path, as the outcome rules compute it: Taiwan's share of the product's imports among the
# compared countries, 3-month average, against its average share 18 to 13 months before the duty
d = pd.read_parquet("panel/adcvd_stacks_decision.parquet")
d = d[(d.sid == SID) & (d.hs8.astype(str).str.zfill(8) == HS8)]
tot = d.groupby("k").value.sum()
tw = d[d.treated].groupby("k").value.sum().reindex(tot.index, fill_value=0)
share = (tw / tot).reindex(range(-18, 19))
avg3 = share.rolling(3, min_periods=3).mean()
pairs = pd.read_csv("recovery_pairs_decision_fall20.csv", dtype={"hs8": str})
pairs["hs8"] = pairs.hs8.str.zfill(8)
pr = pairs[(pairs.sid == SID) & (pairs.hs8 == HS8)].iloc[0]
pre = pr.bench
rel = 100 * avg3 / pre

# the January 2025 list and the two orderings
w = pd.read_csv("results/review_queue_watchlist.csv", dtype={"hs8": str})
w["hs8"] = w.hs8.str.zfill(8)
q = w[w.decision_month == MONTH].reset_index(drop=True)
i = q.index[(q.sid == SID) & (q.hs8 == HS8)][0]
n, cap = len(q), 0.2 * len(q)
rank_model = int(q["rank"][i])
rank_latest = int(q.latest_vs_pre.rank(method="min")[i])
reviewed_model = M.review_shares(q.p_not_recovered.to_numpy(), 0.2)[i]
reviewed_latest = M.review_shares(-q.latest_vs_pre.to_numpy(), 0.2)[i]
assert (n, rank_model, rank_latest, reviewed_model, reviewed_latest) == (36, 2, 20, 1.0, 0.0)
assert pd.isna(pr.rec_at) and round(rel[SEEN]) == 42 and round(rel[18]) == 26

plt.rcParams.update({
    "font.family": "Avenir Next", "font.size": 13, "text.color": "#14161A", "axes.edgecolor": "#6E737C",
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 200,
    "savefig.bbox": "tight", "savefig.facecolor": "white"})
RED, GREY, INK, LIGHT = "#C8102E", "#6E737C", "#14161A", "#D9DBDF"
fig, (ax, ar) = plt.subplots(1, 2, figsize=(10, 4.4), gridspec_kw={"width_ratios": [1.9, 1]})

# left: the share path, seen and later
ax.axhline(100, color=GREY, lw=1, ls=":")
ax.text(-9.5, 104, "pre-duty level", color=GREY, fontsize=11)
ax.axvspan(SEEN + 0.5, 18.5, color=LIGHT, alpha=0.45, lw=0)
ax.text(10.5, 125, "not yet published\nin January 2025", color=GREY, fontsize=11, ha="center")
ax.plot(rel.loc[:SEEN].index, rel.loc[:SEEN], color=RED, lw=2.4)
ax.plot(rel.loc[SEEN:].index, rel.loc[SEEN:], color=GREY, lw=2, ls="--")
ax.plot([SEEN], [rel[SEEN]], "o", color=RED, ms=7)
ax.annotate(f"Nov 2024, last published:\n{rel[SEEN]:.0f}% of its pre-duty share\n"
            f"({100 * avg3[SEEN]:.1f}% of imports,\nagainst {100 * pre:.1f}% before)",
            (SEEN, rel[SEEN]), xytext=(-17.8, 37), textcoords="data", va="top", fontsize=11, color=RED,
            arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
ax.plot([18], [rel[18]], "o", color=GREY, ms=7)
ax.annotate(f"month 18: {rel[18]:.0f}%,\nnot recovered", (18, rel[18]), xytext=(-12, -38),
            textcoords="offset points", fontsize=11, color=GREY, ha="right")
ax.axvline(0, color=INK, lw=0.8)
ax.text(-0.4, 132, "duty starts", fontsize=11, ha="right")
ax.set_xlim(-18.5, 18.5)
ax.set_ylim(0, 140)
ax.set_xlabel("months from the duty (0 = September 2024)")
ax.set_ylabel("Taiwan's share, % of its pre-duty share")
ax.set_title("Taiwan epoxy resins: the share an analyst could see", loc="left",
             fontsize=13.5, fontweight="600")

# right: the same list of 36 ranked two ways; the shaded band is what 20 percent capacity reviews
for x, label, r in [(0, "latest share,\nlowest first", rank_latest), (1, "model", rank_model)]:
    ar.scatter([x] * n, range(1, n + 1), s=18, color=LIGHT, zorder=2)
    ar.scatter([x], [r], s=70, color=RED, zorder=3)
    ar.text(x + 0.12, r, f"Taiwan: {r}{'nd' if r == 2 else 'th'}", va="center", fontsize=12,
            color=RED, fontweight="600")
    ar.text(x, n + 1.5, label, ha="center", va="top", fontsize=11)
ar.axhspan(0.5, cap + 0.5, color=RED, alpha=0.08, lw=0)
ar.text(1.15, cap + 1.6, f"reviewed at 20%\n(first {cap:.1f} places)", ha="left", va="top",
        fontsize=11, color=GREY)
ar.set_ylim(n + 5, 0)
ar.set_xlim(-0.45, 2.05)
ar.set_xticks([])
ar.set_yticks([1, 10, 20, 30, 36])
ar.set_ylabel("rank in the January 2025 list")
ar.spines["bottom"].set_visible(False)
ar.set_title("Its place in the list", loc="left", fontsize=13.5, fontweight="600", pad=10)
fig.tight_layout()
fig.savefig("slides/fig/26_taiwan_example.png")
print(f"wrote slides/fig/26_taiwan_example.png; {rel[SEEN]:.1f}% at month {SEEN}, {rel[18]:.1f}% at month 18; "
      f"ranks: latest share {rank_latest}, model {rank_model} of {n}")
