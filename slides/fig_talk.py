"""Talk-size figures for Presentation 2 v3: one message per chart, labels readable from the back of a room.

Each chart is redrawn from the same CSVs as the report figures (slides/fig_stacked.py,
slides/fig_copper_split.py, slides/fig_taiwan_example.py), with larger type, fewer lines and
direct labels instead of legends. The report figures are unchanged.

Reads:  eda/chapter_month.csv, panel/hs8/, results/itc_compare_paths.csv, results/adcvd_stacked_paths.csv,
        results/recovery_benchmark_fall20.csv, panel/adcvd_stacks_decision.parquet,
        recovery_pairs_decision_fall20.csv, results/review_queue_watchlist.csv, results/review_queue_eval.csv,
        results/review_queue_capacity.csv
Writes: slides/fig/t1_copper_total.png to slides/fig/t7_review_result.png, slides/fig/t9_two_orders.png
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
p = pd.read_csv("results/itc_compare_paths.csv")
o = p[(p.outcome == "PPML value, zeros in") & (p["sample"] == "final stage: order")].set_index("k")
q = pd.read_csv("results/adcvd_stacked_paths.csv")
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
b = pd.read_csv("results/recovery_benchmark_fall20.csv").set_index(["sample", "measure"]).value
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
w = pd.read_csv("results/review_queue_watchlist.csv", dtype={"hs8": str})
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
    ax.text(3, 104, "earlier level", color=GREY, fontsize=18)
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
        ax.annotate(f"month 18, March 2026:\n{rel[18]:.0f}%, not back", (18, rel[18]), xytext=(-20, 40),
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
    ax.set_ylabel("Taiwan's share, % of\nits earlier level")
    grid(ax)
    save(fig, name)


taiwan(False, "t6_taiwan_known")
taiwan(True, "t6_taiwan_later")

# ---------------------------------------------------------------- t7: the review result, at every checking share
E = pd.read_csv("results/review_queue_eval.csv")
E = E[(E.weighting == "relationship") & (E.measure == "precision") & (E.capacity == 0.2)].set_index("ranking").value
C = pd.read_csv("results/review_queue_capacity.csv")
C = C[C.L == 4]
cp = C.pivot(index="capacity", columns="ranking", values="precision")
gap_lo = C[C.ranking == "forecast (boosting)"].set_index("capacity").vs_latest_lo
assert (gap_lo > 0).all() and len(cp) == 10  # the gap over the latest share stays above zero at every share
lines = [("forecast (boosting)", "model's order", RED, "-", 3.6),
         ("latest share", "biggest drop first", GREY, "-", 3.0),
         ("historical rate", "random order", LGREY, ":", 3.0)]
fig, ax = plt.subplots(figsize=(11, 4.8))
ax.axvline(20, color=INK, lw=1.2, ls="--", zorder=1)
ax.text(20.8, 94.5, "1 in 5, the share we assume", fontsize=16, color=INK, va="top")
for key, lab, col, ls, lw in lines:
    x, y = 100 * cp.index.to_numpy(), 100 * cp[key].to_numpy()
    assert round(100 * E[key]) == round(100 * cp.loc[0.2, key])
    ax.plot(x, y, color=col, ls=ls, lw=lw, marker="o" if ls == "-" else None, ms=7, zorder=3)
    ax.text(51.5, y[-1], lab, color=col if col != LGREY else GREY, fontsize=18, fontweight="600", va="center")
    ax.text(19.2, 100 * cp.loc[0.2, key] + (1.6 if key != "historical rate" else 1.4), f"{100 * cp.loc[0.2, key]:.0f}%",
            ha="right", va="bottom", fontsize=20, fontweight="700", color=RED if col == RED else INK)
ax.set_xlim(3, 67)
ax.set_ylim(55, 95)
ax.set_xticks([5, 10, 20, 30, 40, 50])
ax.set_xlabel("share of each month's list the analyst checks, %")
ax.set_ylabel("checked declines that did\nnot come back by month 18, %", fontsize=18)
grid(ax)
save(fig, "t7_review_result")

# ---------------------------------------------------------------- t9: January 2025's list, two ways to pick 7
jl = w[w.decision_month == MONTH].reset_index(drop=True)
jl["now"] = 100 * jl.latest_vs_pre
jl["taiwan"] = (jl.sid == SID) & (jl.hs8 == HS8)
assert len(jl) == 36 and (jl.now == 0).sum() == 10 and (jl.now > 120).sum() == 1
CAP = 112

xx = np.minimum(jl.now, CAP)
t_ = jl[jl.taiwan].index[0]

fig, ax = plt.subplots(figsize=(11, 4.7))
top7 = jl["rank"] <= 7
down = jl.remained_down == 1
for m_, face in [(down, INK), (~down, "white")]:
    ax.scatter(xx[m_], 100 * jl.p_not_recovered[m_], s=140, facecolor=face, edgecolor=INK, lw=1.6, zorder=3)
ax.scatter(xx[top7], 100 * jl.p_not_recovered[top7], s=420, facecolor="none", edgecolor=RED, lw=2.4, zorder=4)
ax.axvspan(-4, 4, color=GREY, alpha=0.12, lw=0)
ax.text(64, 99, "red rings: the model's top 7", color=RED, fontsize=16, fontweight="600", va="top")
ax.text(CAP, 100 * jl.p_not_recovered[jl.now > 120].iloc[0] + 4, "279%", color=GREY, fontsize=12, ha="center")
ax.text(5.5, 4, "biggest drop first\npicks from here", color=GREY, fontsize=15, fontweight="600", va="bottom")
ax.annotate("Taiwan", (xx[t_], 100 * jl.p_not_recovered[t_]), xytext=(52, 70), color=RED, fontsize=16,
            fontweight="600", arrowprops=dict(arrowstyle="-", color=RED, lw=1))
ax.set_xlim(-6, 118)
ax.set_ylim(0, 101)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xlabel("share now, % of its earlier level (100 = no change)")
ax.set_ylabel("model's chance it\nstays down, %")
grid(ax)
save(fig, "t9_two_orders")
