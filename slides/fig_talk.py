"""Talk-size figures for Presentation 2 v3: one message per chart, labels readable from the back of a room.

Each chart is redrawn from the same CSVs as the report figures (slides/fig_stacked.py,
slides/fig_copper_split.py, slides/fig_taiwan_example.py), with larger type, fewer lines and
direct labels instead of legends. The report figures are unchanged.

Reads:  eda/chapter_month.csv, panel/hs8/, itc_compare_paths.csv, adcvd_stacked_paths.csv,
        recovery_benchmark_fall20.csv, panel/adcvd_stacks_decision.parquet,
        recovery_pairs_decision_fall20.csv, review_queue_watchlist.csv, review_queue_eval.csv
Writes: slides/fig/t1_copper_total.png to slides/fig/t7_review_result.png
Run:    python3 slides/fig_talk.py      (from the repo root, after the analysis)
"""
import glob
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, ".")  # the shared modules are at the repo root
import modeling as M  # noqa: E402

plt.rcParams.update({
    "font.family": "Avenir Next", "font.size": 20, "axes.labelsize": 20,
    "xtick.labelsize": 19, "ytick.labelsize": 19, "axes.edgecolor": "#6E737C",
    "axes.spines.top": False, "axes.spines.right": False, "text.color": "#14161A",
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white"})
INK, GREY, RED, LRED, LGREY = "#14161A", "#6E737C", "#C8102E", "#E8A0AB", "#C9CDD2"
SIZE = (12, 4.6)
pct = lambda b: 100 * (np.exp(b) - 1)  # noqa: E731


def grid(ax):
    ax.grid(axis="y", color="#E3E5E8", lw=1)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(f"slides/fig/{name}.png")
    plt.close(fig)
    print(f"wrote slides/fig/{name}.png")


# ---------------------------------------------------------------- t1: copper's total came back
cm = pd.read_csv("eda/chapter_month.csv", dtype={"chapter": str}, parse_dates=["ym"])
s = cm[cm.chapter == "74"].set_index("ym").value.sort_index().loc["2023-01":] / 1e9
fig, ax = plt.subplots(figsize=SIZE)
ax.plot(s.index, s.values, lw=3.2, color=INK)
ax.axvline(pd.Timestamp("2025-08-01"), color=RED, ls="--", lw=2)
ax.text(pd.Timestamp("2025-08-01"), s.max() * 1.02, "50% duty starts ", color=RED, fontweight="600",
        ha="right", va="bottom")
ax.set_ylim(0, s.max() * 1.15)
ax.set_ylabel("$ billion a month")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
grid(ax)
save(fig, "t1_copper_total")

# ---------------------------------------------------------------- t2: only the untaxed part came back
SEMI = ["7407", "7408", "7409", "7410", "7411", "7412", "7413"]
rows = []
for f in sorted(glob.glob("panel/hs8/*.parquet")):
    d = pd.read_parquet(f, columns=["hs8", "qty", "unit"])
    d = d[d.unit == "KG"]
    h = d[d.hs8.astype(str).str.startswith("74")]
    rows.append(dict(ym=pd.Timestamp(f.split("/")[-1][:7] + "-01"),
                     taxed=h[h.hs8.astype(str).str[:4].isin(SEMI)].qty.sum() / 1e6,
                     untaxed=h[h.hs8.astype(str) == "74031100"].qty.sum() / 1e6))
c = pd.DataFrame(rows).set_index("ym").loc["2023-01":]
fig, ax = plt.subplots(figsize=SIZE)
ax.plot(c.index, c.untaxed, color=GREY, lw=3.2)
ax.plot(c.index, c.taxed, color=RED, lw=3.2)
last = c.index[-1]
ax.annotate("not taxed: refined copper", (last, c.untaxed.iloc[-1]), xytext=(10, 0),
            textcoords="offset points", va="center", color=GREY, fontweight="600")
ax.annotate("taxed: wire, tubes, sheets", (last, c.taxed.iloc[-1]), xytext=(10, 0),
            textcoords="offset points", va="center", color=RED, fontweight="600")
ax.axvline(pd.Timestamp("2025-08-01"), color=INK, ls="--", lw=2)
ax.text(pd.Timestamp("2025-08-01"), c.max().max() * 1.02, "50% duty starts ", ha="right", va="bottom",
        fontweight="600")
ax.set_ylim(0, c.max().max() * 1.15)
ax.set_ylabel("thousand tonnes a month")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
grid(ax)
save(fig, "t2_copper_split")

# ---------------------------------------------------------------- t4: where the duty stayed
p = pd.read_csv("itc_compare_paths.csv")
o = p[(p.outcome == "PPML value, zeros in") & (p["sample"] == "final stage: order")].set_index("k")
q = pd.read_csv("adcvd_stacked_paths.csv")
fk = q[(q.outcome == "PPML value, zeros in") & (q["sample"] == "placebo, 24 months earlier")].set_index("k")
fig, ax = plt.subplots(figsize=SIZE)
ax.axhline(0, color=GREY, lw=1.2)
ax.axvline(0, color=INK, ls="--", lw=1.6)
ax.text(0.3, 27, "duty starts", fontweight="600", va="top")
ax.fill_between(o.index, pct(o.coef - 1.96 * o.se), pct(o.coef + 1.96 * o.se), color=RED, alpha=.12, lw=0)
ax.plot(fk.index, pct(fk.coef), color=GREY, lw=2.6, ls="--")
ax.plot(o.index, pct(o.coef), color=RED, lw=3.4)
end = o.index.max()
ax.annotate("duty became permanent", (end, pct(o.coef[end])), xytext=(10, 0), textcoords="offset points",
            va="center", color=RED, fontweight="600")
ax.annotate("fake date, 2 years earlier", (end, pct(fk.coef[end])), xytext=(10, 6), textcoords="offset points",
            va="center", color=GREY, fontweight="600")
ax.set_xlim(-12.5, 18.5)
ax.set_ylim(-56, 30)
ax.set_xticks([-12, -6, 0, 6, 12, 18])
ax.set_xlabel("months from the duty")
ax.set_ylabel("% vs other countries\nselling the same product")
grid(ax)
save(fig, "t4_aftermath")

# ---------------------------------------------------------------- t5: what happened within 18 months
b = pd.read_csv("recovery_benchmark_fall20.csv").set_index(["sample", "measure"]).value
cats = [("no fall", "did not fall", LGREY, INK), ("recovered", "fell, came back", "#9BA1A9", INK),
        ("not recovered", "fell, still down", LRED, INK), ("exited", "fell, no imports\na year later", RED, "white")]
fig, ax = plt.subplots(figsize=(12, 3.6))
for i, (s_, lab) in enumerate([("real", "real cases"), ("placebo", "fake date")]):
    left = 0
    for key, _, col, tc in cats:
        v = 100 * b[(s_, key)]
        ax.barh(i, v - 0.5, left=left + 0.25, color=col, height=0.6, lw=0)
        if v >= 6:
            ax.text(left + v / 2, i, f"{v:.0f}%", ha="center", va="center", color=tc, fontweight="600",
                    fontsize=21)
        left += v
    gone = 100 * (b[(s_, "not recovered")] + b[(s_, "exited")])
    ax.text(101.5, i, f"{gone:.0f}% did not\ncome back", va="center", fontweight="600",
            color=RED if s_ == "real" else GREY, fontsize=19)
x = 0
for key, lab, _, _ in cats:
    v = 100 * b[("real", key)]
    ax.text(x + v / 2, -0.42, lab, ha="center", va="bottom", fontsize=17)
    x += v
ax.set_yticks([0, 1])
ax.set_yticklabels(["real cases", "fake date"])
ax.invert_yaxis()
ax.set_xlim(0, 100)
ax.set_ylim(1.45, -0.95)
ax.set_xticks([])
for sp in ["left", "bottom"]:
    ax.spines[sp].set_visible(False)
ax.tick_params(left=False)
save(fig, "t5_outcomes")

# ---------------------------------------------------------------- t6: Taiwan, known then and later
SID, HS8, MONTH, SEEN = 468, "39073000", "2025-01", 2
d = pd.read_parquet("panel/adcvd_stacks_decision.parquet")
d = d[(d.sid == SID) & (d.hs8.astype(str).str.zfill(8) == HS8)]
tot = d.groupby("k").value.sum()
tw = d[d.treated].groupby("k").value.sum().reindex(tot.index, fill_value=0)
avg3 = (tw / tot).reindex(range(-18, 19)).rolling(3, min_periods=3).mean()
pairs = pd.read_csv("recovery_pairs_decision_fall20.csv", dtype={"hs8": str})
pairs["hs8"] = pairs.hs8.str.zfill(8)
pr = pairs[(pairs.sid == SID) & (pairs.hs8 == HS8)].iloc[0]
rel = 100 * avg3 / pr.bench
w = pd.read_csv("review_queue_watchlist.csv", dtype={"hs8": str})
w["hs8"] = w.hs8.str.zfill(8)
ql = w[w.decision_month == MONTH].reset_index(drop=True)
i = ql.index[(ql.sid == SID) & (ql.hs8 == HS8)][0]
ranks = (len(ql), int(ql["rank"][i]), int(ql.latest_vs_pre.rank(method="min")[i]),
         M.review_shares(ql.p_not_recovered.to_numpy(), 0.2)[i], M.review_shares(-ql.latest_vs_pre.to_numpy(), 0.2)[i])
assert ranks == (36, 2, 20, 1.0, 0.0), ranks
assert pd.isna(pr.rec_at) and round(rel[SEEN]) == 42 and round(rel[18]) == 26


def taiwan(later, name):
    fig, ax = plt.subplots(figsize=(7.6, 4.6) if not later else SIZE)
    ax.axhline(100, color=GREY, lw=1.4, ls=":")
    ax.text(3, 104, "pre-duty level", color=GREY, fontsize=18)
    ax.axvline(0, color=INK, ls="--", lw=1.6)
    ax.text(-0.4, 136, "duty starts", ha="right", va="top", fontsize=18, fontweight="600")
    ax.plot(rel.loc[:SEEN].index, rel.loc[:SEEN], color=RED, lw=3.4)
    ax.plot([SEEN], [rel[SEEN]], "o", color=RED, ms=11)
    if later:
        ax.plot(rel.loc[SEEN:].index, rel.loc[SEEN:], color=GREY, lw=3, ls="--")
        ax.plot([18], [rel[18]], "o", color=INK, ms=11)
        ax.annotate(f"Jan 2025, what the\nanalyst saw: {rel[SEEN]:.0f}%", (SEEN, rel[SEEN]), xytext=(-17.5, 30),
                    textcoords="data", color=RED, fontweight="600", fontsize=18,
                    arrowprops=dict(arrowstyle="-", color=RED, lw=1))
        ax.annotate(f"month 18, March 2026:\n{rel[18]:.0f}%, not recovered", (18, rel[18]), xytext=(-20, 40),
                    textcoords="offset points", ha="right", va="bottom", fontweight="600", fontsize=18,
                    arrowprops=dict(arrowstyle="-", color=INK, lw=1))
        ax.text(10, 126, "published later", color=GREY, ha="center", fontsize=18, fontweight="600")
    else:
        ax.axvspan(SEEN + 0.5, 18.5, color="#EEEFF2", lw=0)
        ax.text(10.5, 70, "not yet\npublished", color=GREY, ha="center", va="center", fontsize=19,
                fontweight="600")
        ax.annotate(f"latest published\n(Nov 2024): {rel[SEEN]:.0f}%", (SEEN, rel[SEEN]), xytext=(-17.5, 30),
                    textcoords="data", color=RED, fontweight="600", fontsize=18,
                    arrowprops=dict(arrowstyle="-", color=RED, lw=1))
    ax.set_xlim(-18.5, 18.5)
    ax.set_ylim(0, 140)
    ax.set_xticks([-18, -12, -6, 0, 6, 12, 18])
    ax.set_xlabel("months from the duty (0 = Sep 2024)")
    ax.set_ylabel("Taiwan's share, % of\nits pre-duty share")
    grid(ax)
    save(fig, name)


taiwan(False, "t6_taiwan_known")
taiwan(True, "t6_taiwan_later")

# ---------------------------------------------------------------- t7: the review result, 20 percent
E = pd.read_csv("review_queue_eval.csv")
E = E[(E.weighting == "relationship") & (E.measure == "precision") & (E.capacity == 0.2)].set_index("ranking").value
bars = [("forecast (boosting)", "model's order", RED, "white"),
        ("latest share", "biggest drop first", GREY, "white"),
        ("historical rate", "random order", LGREY, INK)]
fig, ax = plt.subplots(figsize=(10, 4.8))
for j, (key, lab, col, tc) in enumerate(bars):
    v = 100 * E[key]
    ax.bar(j, v, width=0.62, color=col, zorder=2)
    ax.text(j, v + 2, f"{v:.0f}%", ha="center", va="bottom", fontsize=26, fontweight="700",
            color=RED if j == 0 else INK)
ax.set_xticks(range(3))
ax.set_xticklabels([b_[1] for b_ in bars], fontsize=21)
ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_ylabel("checked relationships\nnot recovered by month 18, %", fontsize=19)
grid(ax)
save(fig, "t7_review_result")
