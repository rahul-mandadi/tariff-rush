"""Does the dollar ranking of unusual 2025 months survive deflating by import prices?

The appendix ("Dollars and quantity at the category level") ranks chapters by how far their
largest 2025 month sat above a line drawn from their own trend and seasonal pattern, the score of
slides/fig_units.py, repeated here. A dollar series mixes price and volume, so this recomputes the
score on dollars divided by the BLS import price index, for all imports (EIUIR) and for nonfuel
imports (EIUIREXFUELS), and counts how many of the top 10 chapters stay in the top 10: over every
product chapter with a full dollar history (96, the figure the appendix reports) and over the 63
that also have quantity data.

The two BLS series are fetched once from the public BLS API and kept in eda/bls_import_prices.csv,
so later runs work offline.

Writes deflation_check.csv.    Usage:  python3 deflation_check.py      # from the repo root
"""
import json
import os
import urllib.request

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

PRICES = "eda/bls_import_prices.csv"
SERIES = {"EIUIR": "all imports", "EIUIREXFUELS": "nonfuel imports"}


def fetch(series_id, a, b):
    req = urllib.request.Request(
        "https://api.bls.gov/publicAPI/v2/timeseries/data/",
        data=json.dumps({"seriesid": [series_id], "startyear": str(a), "endyear": str(b)}).encode(),
        headers={"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=30))["Results"]["series"][0]["data"]
    return {pd.Timestamp(f"{x['year']}-{x['period'][1:]}-01"): float(x["value"])
            for x in d if x["period"].startswith("M") and x["period"] != "M13"}


if not os.path.exists(PRICES):
    px = pd.DataFrame({s: pd.Series({**fetch(s, 2015, 2024), **fetch(s, 2025, 2026)})
                       for s in SERIES}).sort_index()
    px.index.name = "ym"
    px.to_csv(PRICES)
px = pd.read_csv(PRICES, parse_dates=["ym"]).set_index("ym")


def expected(s, cut="2024-12"):
    """The expected line and band of slides/fig_units.py."""
    pre = np.log(s[:cut])
    me = pre.groupby(pre.index.month).mean() - pre.mean()
    t = np.arange(len(pre))
    slope, intercept = np.polyfit(t[-36:], pre.values[-36:], 1)
    pred = np.exp(pre.values[-1] + slope * (np.arange(len(s)) - (len(pre) - 1))
                  + s.index.month.map(me).values)
    resid = pre.values - (intercept + slope * t) - pre.index.month.map(me).values
    return pd.Series(pred, index=s.index), float(np.std(resid, ddof=1))


def score(s):
    pred, sd = expected(s)
    dev = (np.log(s) - np.log(pred)).loc["2025-01":"2025-08"]
    return np.nan if dev.empty or sd == 0 else dev.max() / (1.96 * sd)


def ranks(path):
    d = pd.read_csv(path, dtype={"chapter": str}, parse_dates=["ym"])
    d["chapter"] = d.chapter.str.zfill(2)
    rows = []
    for ch, g in d.groupby("chapter"):
        s = g.set_index("ym").value.sort_index()
        s = s[s > 0]
        if len(s) < 100 or s[:"2024-12"].min() <= 0 or ch in ("98", "99"):
            continue
        r = dict(chapter=ch, dollars=score(s))
        for sid in SERIES:
            sd_ = (s / px[sid].reindex(s.index)).dropna()
            r[sid] = score(sd_) if len(sd_) >= 100 else np.nan
        rows.append(r)
    return pd.DataFrame(rows).set_index("chapter")


# the dollar ranking over every product chapter with a full dollar history (the appendix figure),
# and, as a check, over the 63 chapters that also have quantity data (slides/fig_units.py)
out = []
for label, path in [("all product chapters", "eda/chapter_month.csv"),
                    ("chapters with quantity data", "eda/chapter_month_qty.csv")]:
    R = ranks(path)
    top = set(R.dollars.nlargest(10).index)
    print(f"{label}: {len(R)} chapters")
    for sid, lab in SERIES.items():
        kept = len(top & set(R[sid].nlargest(10).index))
        rho = spearmanr(R.dollars, R[sid], nan_policy="omit").correlation
        print(f"  deflated by {lab} ({sid}): {kept} of the top 10 stay in the top 10; "
              f"rank correlation {rho:.2f}")
        out.append(dict(universe=label, chapters=len(R), index=sid, top10_kept=kept, rank_corr=rho))
pd.DataFrame(out).to_csv("deflation_check.csv", index=False)
print("wrote deflation_check.csv")
