"""Provisional counterfactual ("normal") for HS2 import weight.

Works in logs, so seasonality is multiplicative. Robust STL is fit on data up to
CUT only, so the 2025 tariffs cannot leak into the trend or seasonal components.
The trend is extrapolated from its slope over the last TREND_WIN months and the
seasonal profile is the average of the last three cycles. Anomaly = actual /
counterfactual - 1, with a band from pre-period residual dispersion.

CUT is one fixed date for every series, not each event's announcement date.
Per-event cutoffs need the tariff event table.
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL

from paths import ANOMALIES_KG, PANEL_HS2

CUT = "2024-12"     # tariff announcements begin early 2025
TREND_WIN = 36      # months of trend used to extrapolate the slope
MIN_PRE = 72        # months of pre-period history needed to fit
CHAPTERS = {"30": "pharma", "72": "iron & steel", "73": "steel articles",
            "76": "aluminum", "94": "furniture", "87": "vehicles"}


def load():
    df = pd.read_csv(PANEL_HS2, dtype={"chapter": str, "cty_name": str})
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.month, day=1))
    df["kg"] = df.air_kg + df.ves_kg    # containerized is a subset of vessel
    return df


def series(df, chapter, partner=None, metric="kg"):
    d = df[df.chapter == chapter]
    if partner:
        d = d[d.cty_name == partner]
    return d.groupby("date")[metric].sum().sort_index().asfreq("MS")


def counterfactual(s):
    """Return (pred, resid_sd) indexed over the whole span of s."""
    s = s.replace(0, np.nan).dropna()
    pre = s[:CUT]
    if len(pre) < MIN_PRE:
        return None, None
    ln = np.log(pre)
    stl = STL(ln, period=12, robust=True).fit()
    trend, seas = stl.trend, stl.seasonal
    # extrapolate trend from its recent slope
    t = np.arange(len(trend))
    b, _ = np.polyfit(t[-TREND_WIN:], trend.values[-TREND_WIN:], 1)
    # seasonal profile by calendar month, averaged over last 3 cycles
    prof = (pd.DataFrame({"m": seas.index.month, "s": seas.values})
              .groupby("m")["s"].apply(lambda x: x.tail(3).mean()))
    idx = s.index
    steps = np.arange(len(idx)) - (len(pre) - 1)
    pred_ln = (trend.values[-1] + b * steps) + idx.month.map(prof).values
    resid_sd = float(np.std(ln.values - (trend + seas).values, ddof=1))
    return pd.Series(np.exp(pred_ln), index=idx), resid_sd


def main():
    df = load()
    print(f"{'ch':<4}{'chapter':<16}{'Mar-25 anomaly':>17}{'band':>14}"
          f"{'Apr-Jun':>10}{'2025 net':>11}")
    print("-" * 76)
    out = {}
    for ch, name in CHAPTERS.items():
        s = series(df, ch)
        pred, sd = counterfactual(s)
        if pred is None:
            print(f"{ch:<4}{name:<16} insufficient history")
            continue
        an = (s / pred - 1) * 100
        mar = an.get(pd.Timestamp("2025-03-01"), np.nan)
        aprjun = an.loc["2025-04":"2025-06"].mean()
        # cumulative excess kg over calendar 2025 as % of counterfactual total
        net = (s.loc["2025-01":"2025-12"].sum()
               / pred.loc["2025-01":"2025-12"].sum() - 1) * 100
        band = 1.96 * sd * 100
        print(f"{ch:<4}{name:<16}{mar:>+16.0f}%{'+/-' + format(band, '.0f') + '%':>14}"
              f"{aprjun:>+9.0f}%{net:>+10.0f}%")
        out[ch] = an
    pd.DataFrame(out).to_csv(ANOMALIES_KG)
    print(f"\nsaved {ANOMALIES_KG}")


if __name__ == "__main__":
    main()
