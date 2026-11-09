"""Counterfactual for tariff front-loading.

Method: work in logs (multiplicative seasonality). Fit robust STL on the
PRE-treatment window only, so the treatment cannot leak into the trend or
seasonal components. Extrapolate trend linearly from its recent slope and
carry the seasonal profile forward. Anomaly = actual / counterfactual - 1,
with a prediction band from pre-period residual dispersion.
"""
import pandas as pd, numpy as np
from statsmodels.tsa.seasonal import STL

CUT = "2024-12"          # tariff announcements begin early 2025
TREND_WIN = 36           # months of trend used to extrapolate the slope

def load(metric="kg"):
    df = pd.read_csv("panel/imports_hs2_panel.csv",
                     dtype={"chapter":str,"cty_name":str})
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.month, day=1))
    df["kg"] = df.air_kg + df.ves_kg
    df["val"] = df.value_usd
    return df

def series(df, chapter, partner=None, metric="kg"):
    d = df[df.chapter == chapter]
    if partner: d = d[d.cty_name == partner]
    s = d.groupby("date")[metric].sum().sort_index()
    return s.asfreq("MS")

def counterfactual(s):
    """Return (pred, resid_sd) indexed over the whole span of s."""
    s = s.replace(0, np.nan).dropna()
    pre = s[:CUT]
    if len(pre) < 72: return None, None
    ln = np.log(pre)
    stl = STL(ln, period=12, robust=True).fit()
    trend, seas = stl.trend, stl.seasonal
    # extrapolate trend from its recent slope
    t = np.arange(len(trend))
    k = TREND_WIN
    b, a = np.polyfit(t[-k:], trend.values[-k:], 1)
    # seasonal profile by calendar month, averaged over last 3 cycles
    prof = (pd.DataFrame({"m": seas.index.month, "s": seas.values})
              .groupby("m")["s"].apply(lambda x: x.tail(3).mean()))
    idx = s.index
    steps = np.arange(len(idx)) - (len(pre) - 1)
    pred_ln = (trend.values[-1] + b * steps) + idx.month.map(prof).values
    resid_sd = float(np.std(ln.values - (trend + seas).values, ddof=1))
    return pd.Series(np.exp(pred_ln), index=idx), resid_sd

NAMES = {"30":"pharma","72":"iron & steel","73":"steel articles",
         "76":"aluminum","94":"furniture","87":"vehicles"}
df = load()
print(f"{'ch':<4}{'chapter':<16}{'Mar-25 anomaly':>17}{'band':>14}{'Apr-Jun':>10}{'2025 net':>11}")
print("-"*76)
out={}
for ch in NAMES:
    s = series(df, ch, metric="kg")
    pred, sd = counterfactual(s)
    if pred is None: print(f"{ch:<4}{NAMES[ch]:<16} insufficient history"); continue
    an = (s / pred - 1) * 100
    mar = an.get(pd.Timestamp("2025-03-01"), np.nan)
    aprjun = an.loc["2025-04":"2025-06"].mean()
    # cumulative excess kg over calendar 2025 as % of counterfactual 2025 total
    act25 = s.loc["2025-01":"2025-12"].sum(); cf25 = pred.loc["2025-01":"2025-12"].sum()
    net = (act25/cf25 - 1) * 100
    band = 1.96*sd*100
    print(f"{ch:<4}{NAMES[ch]:<16}{mar:>+16.0f}%{'+/-'+format(band,'.0f')+'%':>14}"
          f"{aprjun:>+9.0f}%{net:>+10.0f}%")
    out[ch]=an
pd.DataFrame(out).to_csv("panel/anomalies_kg.csv")
print("\nsaved panel/anomalies_kg.csv")
