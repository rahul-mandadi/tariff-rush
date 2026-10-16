"""The first test that uses coverage: did tariffed products move differently from untariffed ones?

For every chapter we measure how far imports ran above or below what the pre-2025 counterfactual
predicted. We then mark each chapter-month as treated if a tariff action covering that chapter was
between announcement and effective date, and compare the two groups.
"""
import re
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
import warnings; warnings.filterwarnings("ignore")

CUT, TREND_WIN = "2024-12", 36
RED, GREY = "#C8102E", "#5B6770"
EXCLUDE = {"98", "99"}          # accounting categories, not products

def anomaly_series(s):
    s = s.replace(0, np.nan).dropna(); pre = s[:CUT]
    if len(pre) < 72: return None
    ln = np.log(pre); st = STL(ln, period=12, robust=True).fit()
    tr, se = st.trend, st.seasonal
    t = np.arange(len(tr)); b, _ = np.polyfit(t[-TREND_WIN:], tr.values[-TREND_WIN:], 1)
    prof = (pd.DataFrame({"m": se.index.month, "s": se.values})
              .groupby("m")["s"].apply(lambda x: x.tail(3).mean()))
    step = np.arange(len(s.index)) - (len(pre) - 1)
    pred = np.exp((tr.values[-1] + b*step) + s.index.month.map(prof).values)
    return (s / pd.Series(pred, index=s.index) - 1) * 100

def main():
    p = pd.read_csv("imports_hs2_panel.csv", dtype={"chapter": str, "cty_name": str})
    p["date"] = pd.to_datetime(dict(year=p.year, month=p.month, day=1))
    p["kg"] = p.air_kg + p.ves_kg

    an = {}
    for ch, d in p.groupby("chapter"):
        if ch in EXCLUDE: continue
        a = anomaly_series(d.groupby("date").kg.sum().sort_index().asfreq("MS"))
        if a is not None: an[ch] = a
    A = pd.DataFrame(an)
    print(f"chapters with a counterfactual: {A.shape[1]}")

    # treated chapter-months: inside an announcement-to-effective window
    s = pd.read_csv("coverage/event_scope.csv", dtype={"chapter": str})
    s = s[s.chapter.notna()]
    s["ann"] = pd.to_datetime(s.announcement_date, errors="coerce")
    s["eff"] = pd.to_datetime(s.effective_date, errors="coerce")
    s = s.dropna(subset=["ann"])
    s["eff"] = s.eff.fillna(s.ann + pd.Timedelta(days=30))   # typical lag when none stated

    treated = set()
    for _, r in s.iterrows():
        chs = list(A.columns) if r.chapter == "ALL" else [r.chapter]
        months = pd.date_range(r.ann.to_period("M").to_timestamp(),
                               r.eff.to_period("M").to_timestamp(), freq="MS")
        for ch in chs:
            for m in months: treated.add((ch, m))

    long = A.stack().rename("anomaly").reset_index()
    long.columns = ["date", "chapter", "anomaly"]
    long = long[long.date.between("2018-01-01", "2026-06-01")]
    long["treated"] = [(c, d) in treated for c, d in zip(long.chapter, long.date)]

    g = long.groupby("treated").anomaly
    print(f"\nchapter-months, 2018 onward")
    print(f"  treated   {g.size().get(True,0):>7,}")
    print(f"  untreated {g.size().get(False,0):>7,}")
    print(f"\n{'':<12}{'median':>9}{'mean':>9}{'p90':>9}{'share >20%':>12}")
    for t, lab in [(True,"treated"), (False,"untreated")]:
        x = long[long.treated == t].anomaly
        print(f"{lab:<12}{x.median():>+8.1f}%{x.mean():>+8.1f}%"
              f"{np.percentile(x,90):>+8.1f}%{(x>20).mean():>11.0%}")

    t_, u_ = long[long.treated].anomaly, long[~long.treated].anomaly
    from scipy import stats
    st_ = stats.mannwhitneyu(t_, u_, alternative="greater")
    print(f"\nMann-Whitney, treated greater than untreated: p = {st_.pvalue:.2g}")

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.1))
    bins = np.linspace(-60, 80, 50)
    axes[0].hist(u_, bins=bins, density=True, color=GREY, alpha=.65, label=f"untreated (n={len(u_):,})")
    axes[0].hist(t_, bins=bins, density=True, color=RED, alpha=.65, label=f"treated (n={len(t_):,})")
    axes[0].axvline(0, color="0.3", lw=.7)
    axes[0].set_xlabel("% above or below normal", fontsize=8)
    axes[0].legend(fontsize=7, frameon=False); axes[0].set_yticks([])
    axes[0].set_title("Distribution", fontsize=9, loc="left")

    mt = long[long.treated].groupby(long.date.dt.year).anomaly.median()
    mu = long[~long.treated].groupby(long.date.dt.year).anomaly.median()
    axes[1].plot(mu.index, mu.values, color=GREY, marker="o", ms=3, lw=1.1, label="untreated")
    axes[1].plot(mt.index, mt.values, color=RED, marker="o", ms=3, lw=1.1, label="treated")
    axes[1].axhline(0, color="0.3", lw=.7)
    axes[1].set_ylabel("median % vs normal", fontsize=8)
    axes[1].legend(fontsize=7, frameon=False)
    axes[1].set_title("By year", fontsize=9, loc="left")
    for ax in axes:
        ax.tick_params(labelsize=7)
        for sp in ("top","right"): ax.spines[sp].set_visible(False)
    plt.suptitle("Imports in the window between tariff announcement and effective date",
                 fontsize=10)
    plt.tight_layout(); plt.savefig("coverage/treated_vs_untreated.png", dpi=200)
    long.to_csv("coverage/chapter_month_treated.csv", index=False)
    print("\nwritten: coverage/treated_vs_untreated.png, coverage/chapter_month_treated.csv")

if __name__ == "__main__":
    main()
