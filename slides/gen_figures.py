"""Figures for presentation 1, sized and weighted for projection.

Bigger fonts and thicker lines than the notebook versions, because a chart that reads on a
laptop disappears on a screen at the back of a room. Every number here comes from the same
eda/*.csv the notebook uses, so the slides and the notebook cannot drift apart.

Usage:  python3 slides/gen_figures.py      # from the repo root
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# palette and type taken from Mandadi_Khalsa_Team_Pitch.pptx so the decks match
plt.rcParams.update({
    "font.family": "Avenir Next",
    "font.size": 14, "axes.titlesize": 16, "axes.labelsize": 13,
    "xtick.labelsize": 13, "ytick.labelsize": 13,
    "axes.grid": True, "grid.alpha": .22, "grid.color": "#6E737C",
    "axes.edgecolor": "#6E737C", "axes.labelcolor": "#14161A",
    "xtick.color": "#14161A", "ytick.color": "#14161A",
    "text.color": "#14161A",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white",
})
INK, GREY, RED, PANEL = "#14161A", "#6E737C", "#C8102E", "#EEEFF2"
ACC, WARN = INK, RED
OUT = "slides/fig"

cm = pd.read_csv("eda/chapter_month.csv", dtype={"chapter": str}, parse_dates=["ym"])
sh = pd.read_csv("coverage/coverage_share.csv", dtype={"chapter": str})
ev = pd.read_csv("events/tariff_events.csv", parse_dates=["announcement_date"])


def series(ch):
    s = cm[cm.chapter == ch].set_index("ym").value.sort_index()
    return s[s > 0]


def expected(s, cut="2024-12"):
    pre = np.log(s[:cut])
    me = pre.groupby(pre.index.month).mean() - pre.mean()
    t = np.arange(len(pre))
    slope, intercept = np.polyfit(t[-36:], pre.values[-36:], 1)
    steps = np.arange(len(s)) - (len(pre) - 1)
    pred = np.exp(pre.values[-1] + slope * steps + s.index.month.map(me).values)
    resid = pre.values - (intercept + slope * t) - pre.index.month.map(me).values
    return pd.Series(pred, index=s.index), float(np.std(resid, ddof=1))


# --- 1. context: a tariff has an announcement and a start date -------------
s = series("74") / 1e9
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.plot(s.index, s.values, lw=2.4, color=INK)
# the two dates are three weeks apart, so one label goes left and one right or they read
# as belonging to the wrong line
for d, lab, dy, ha, off in [("2025-07-08", "announced", .99, "right", -10),
                            ("2025-08-01", "50% duty starts", .80, "left", 10)]:
    ax.axvline(pd.Timestamp(d), color=WARN, ls="--", lw=1.6)
    ax.annotate(lab, (pd.Timestamp(d), s.max() * dy), xytext=(off, 0),
                textcoords="offset points", color=WARN, fontsize=14,
                fontweight="600", ha=ha, va="center")
ax.set_xlim(pd.Timestamp("2023-01-01"), s.index.max())
ax.xaxis.set_major_locator(matplotlib.dates.YearLocator())
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y"))
ax.set_title("Copper imports into the US, billions of dollars a month")
ax.set_ylabel("$bn")
fig.savefig(f"{OUT}/01_context.png"); plt.close(fig)

# --- 2. the decision comes before the data --------------------------------
fig, ax = plt.subplots(figsize=(11, 3.6))
ax.axhline(0, color=INK, lw=2.5, zorder=1)
# palette is ink, grey and red only, matching the pitch deck. Red marks the thing
# to notice, which is that the decision lands before anything is observable.
for x, lab, col, y in [(0, "Tariff announced\nYOU DECIDE HERE", RED, 0.42),
                       (30, "Duty takes effect", INK, -0.40),
                       (65, "First data on what\nactually happened", GREY, 0.42)]:
    ax.plot([x], [0], "o", ms=15, color=col, zorder=3)
    ax.annotate(lab, (x, y), ha="center", va="center",
                color=col, fontsize=14, fontweight="600")
ax.annotate("", xy=(65, -0.80), xytext=(0, -0.80),
            arrowprops=dict(arrowstyle="<->", color="grey", lw=1.6))
ax.text(32, -0.96, "about two months of decisions already committed",
        ha="center", color="grey", fontsize=13, style="italic")
for x, lab in [(0, "day 0"), (30, "day 30"), (65, "day 65")]:
    ax.text(x, 0.10, lab, ha="center", fontsize=12, color="#5b6670")
ax.set_xlim(-14, 80); ax.set_ylim(-1.15, 0.72)
ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values():
    sp.set_visible(False)
ax.grid(False)
fig.savefig(f"{OUT}/02_timeline.png"); plt.close(fig)

# --- 3. the panel, imports per year --------------------------------------
yr = cm.groupby(cm.ym.dt.year).value.sum() / 1e12
fig, ax = plt.subplots(figsize=(11, 4.0))
cols = [INK] * len(yr); cols[-1] = GREY
ax.bar(yr.index.astype(str), yr.values, color=cols)
ax.set_title("US goods imports we cover, trillions of dollars a year")
ax.set_ylabel("$ trillion")
# sits in clear space above the part-year bar, not over the neighbouring one
# the bars are tall enough that there is no clear space for a callout, so the
# part-year caveat lives in the slide caption instead. The grey bar carries the hint.
fig.savefig(f"{OUT}/03_panel.png"); plt.close(fig)

# --- 4. what counts as normal -------------------------------------------
s = series("74")
pred, sd = expected(s)
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.plot(s.index, s.values / 1e9, lw=2.4, color=INK, label="actual")
ax.plot(pred.index, pred.values / 1e9, lw=1.8, color=RED, ls="--", label="what we expected")
ax.fill_between(pred.index, pred * np.exp(-1.96 * sd) / 1e9, pred * np.exp(1.96 * sd) / 1e9,
                color=GREY, alpha=.18, label="normal range")
ax.axvline(pd.Timestamp("2025-08-01"), color=WARN, ls="--", lw=1.6)
ax.set_xlim(pd.Timestamp("2022-06-01"), s.index.max())
ax.set_title("Copper went outside its own normal range in 2025")
ax.set_ylabel("$bn"); ax.legend(fontsize=12, loc="upper left")
fig.savefig(f"{OUT}/04_normal.png"); plt.close(fig)

# --- 5. unusual is not the same as tariffed -----------------------------
rows = []
for ch in sorted(cm.chapter.unique()):
    x = series(ch)
    if len(x) < 100 or x[:"2024-12"].min() <= 0:
        continue
    pr, sdv = expected(x)
    dev = (x / pr - 1).loc["2025-01":"2025-08"]
    if dev.empty or sdv == 0:
        continue
    rows.append(dict(chapter=ch, ratio=dev.max() / (1.96 * sdv),
                     size=x.loc["2024"].sum() / 1e9))
r = pd.DataFrame(rows).sort_values("ratio", ascending=False).head(10)
NAMES = {"29": "organic chemicals", "30": "pharmaceuticals", "89": "ships",
         "71": "gold & gems", "97": "works of art", "91": "clocks",
         "74": "copper", "50": "silk", "84": "machinery", "18": "cocoa"}
r["lab"] = r.chapter.map(NAMES).fillna(r.chapter)
flag = {"cocoa", "silk", "works of art", "clocks"}
cols = [WARN if l in flag else INK for l in r.lab]
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.barh(r.lab[::-1], r.ratio[::-1], color=cols[::-1])
ax.axvline(1, color="grey", ls=":", lw=1.5)
ax.set_title("Furthest outside their own normal range, 2025")
ax.set_xlabel("how many times outside the normal range")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=INK, label="plausibly tariff-related"),
                   Patch(color=WARN, label="not a tariff story")],
          fontsize=13, loc="lower right", frameon=True)
fig.savefig(f"{OUT}/05_chapters.png"); plt.close(fig)

# --- 6. the tariff actions ----------------------------------------------
fig, ax = plt.subplots(figsize=(11, 3.4))
order = ["SECTION_232", "SECTION_301", "IEEPA", "SECTION_201", "OTHER", "UNKNOWN"]
pal = {"SECTION_232": INK, "SECTION_301": RED, "IEEPA": "#6E737C",
       "SECTION_201": "#9BA1A9", "OTHER": "#B9BEC4", "UNKNOWN": "#D4D8DC"}
seen = [a for a in order if a in set(ev.authority)]
for i, a in enumerate(seen):
    g = ev[ev.authority == a]
    ax.scatter(g.announcement_date, [i] * len(g), s=90, alpha=.8, color=pal[a])
ax.set_yticks(range(len(seen)))
LAB = {"SECTION_232": "Section 232", "SECTION_301": "Section 301", "IEEPA": "IEEPA",
       "SECTION_201": "Section 201", "OTHER": "Other", "UNKNOWN": "Unclassified"}
ax.set_yticklabels([LAB.get(a, a) for a in seen])
ax.set_title("134 tariff actions we identified, by legal authority")
fig.savefig(f"{OUT}/06_events.png"); plt.close(fig)

# --- 7. the finding -----------------------------------------------------
bands = pd.cut(sh.share, [-.001, .01, .05, .25, .75, 1.001],
               labels=["under 1%", "1-5%", "5-25%", "25-75%", "over 75%"])
v = bands.value_counts().reindex(["under 1%", "1-5%", "5-25%", "25-75%", "over 75%"])
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.bar(v.index, v.values, color=[RED, RED, "#9BA1A9", GREY, INK])
for i, n in enumerate(v.values):
    ax.text(i, n + 6, f"{n}", ha="center", fontsize=14, fontweight="600")
ax.set_title("How much of a product chapter each tariff action actually covers")
ax.set_ylabel("number of tariff actions")
ax.set_ylim(0, v.max() * 1.16)
fig.savefig(f"{OUT}/07_coverage.png"); plt.close(fig)

print("wrote:")
import os
for f in sorted(os.listdir(OUT)):
    print(f"  {OUT}/{f}  {os.path.getsize(OUT+'/'+f)/1000:.0f} KB")
