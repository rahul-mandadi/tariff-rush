"""Per-cell counterfactual at HS8, and the reversal ratio Q2 is defined against.

The fixed-effects tests answer "did treated imports move relative to untreated ones".
They cannot answer Q2, which asks how much of a surge came back afterwards, because
that is a ratio against a level the series would have reached anyway. That needs a
fitted baseline per cell.

Method follows decomp.py, which is the baseline the project settled on: work in logs,
fit robust STL on the pre-announcement window only so the tariff cannot leak into the
trend or the seasonal profile, extrapolate the trend from its recent slope, carry the
seasonal profile forward.

The one change is that the pre-window ends at each event's own announcement rather than
at a single hardcoded date, so events from 2018 and 2025 are treated the same way. This
also retires the second, incompatible baseline in surges.py, which used a rolling
trailing geometric mean; everything now runs off this one.

  excess_during   sum of log(actual) - log(counterfactual) over announcement..effective
  excess_after    the same over the H months after the tariff took effect
  reversal        -excess_after / excess_during
                  0 means nothing came back, 1 means all of it did

Usage:  python3 counterfactual_hs8.py [--metric value|qty] [--limit N]
"""
import sys, warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL

warnings.filterwarnings("ignore")
args = sys.argv
METRIC = args[args.index("--metric")+1] if "--metric" in args else "value"
LIMIT = int(args[args.index("--limit")+1]) if "--limit" in args else None
MIN_PRE, TREND_WIN, H = 36, 36, 9
REDUCING = {"REVOKE", "DECREASE", "SUSPEND"}

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "chapter", "ym", METRIC])
df["ym"] = pd.to_datetime(df.ym)
df = df[df[METRIC] > 0]

ev = pd.read_csv("events_resolved.csv", dtype={"cty": str})
ep = pd.read_csv("event_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in ep.groupby("document_number")}
ev = ev[(ev.window_days >= 7) & (~ev.action_kind.isin(REDUCING))].copy()
ev["a"] = pd.to_datetime(ev.announcement_date).dt.to_period("M").dt.to_timestamp()
ev["e"] = pd.to_datetime(ev.effective_date).dt.to_period("M").dt.to_timestamp()
print(f"metric={METRIC}  events={ev.document_number.nunique()}  panel={len(df):,} rows")

lookup = {k: g.set_index("ym")[METRIC].sort_index()
          for k, g in df.groupby(["hs8", "cty"], sort=False)}
print(f"cells indexed: {len(lookup):,}")


def counterfactual(s, cut):
    """Baseline fitted on months strictly before `cut`, projected over all of s."""
    pre = s[s.index < cut]
    if len(pre) < MIN_PRE:
        return None, None
    ln = np.log(pre.asfreq("MS").interpolate().dropna())
    if len(ln) < MIN_PRE:
        return None, None
    try:
        stl = STL(ln, period=12, robust=True).fit()
    except Exception:
        return None, None
    trend, seas = stl.trend, stl.seasonal
    k = min(TREND_WIN, len(trend))
    t = np.arange(len(trend))
    b, _ = np.polyfit(t[-k:], trend.values[-k:], 1)
    prof = (pd.DataFrame({"m": seas.index.month, "s": seas.values})
            .groupby("m")["s"].apply(lambda x: x.tail(3).mean()))
    steps = ((s.index.year - ln.index[-1].year) * 12 +
             (s.index.month - ln.index[-1].month)).to_numpy()
    pred_ln = trend.values[-1] + b * steps + s.index.month.map(prof).to_numpy()
    resid_sd = float(np.std(ln.values - (trend + seas).values, ddof=1))
    return pd.Series(pred_ln, index=s.index), resid_sd


rows = []
for _, e in ev.iterrows():
    if e.mechanism == "ENUMERATED":
        cells = [(h, e.cty) for h in prods.get(e.document_number, set())]
    elif e.mechanism == "MATERIAL_CLASS":
        chs = set(str(e.chapters).split(";"))
        cells = [k for k in lookup if k[1] == e.cty and k[0][:2] in chs]
    else:
        cells = [k for k in lookup if k[1] == e.cty]
    if LIMIT:
        cells = cells[:LIMIT]
    after_end = e.e + pd.DateOffset(months=H)
    for key in cells:
        s = lookup.get(key)
        if s is None or len(s) < MIN_PRE + 3:
            continue
        pred_ln, sd = counterfactual(s, e.a)
        if pred_ln is None:
            continue
        ln = np.log(s)
        gap = ln - pred_ln
        during = gap[(s.index >= e.a) & (s.index <= e.e)]
        after = gap[(s.index > e.e) & (s.index <= after_end)]
        if len(during) == 0 or len(after) < 3:
            continue
        ed, ea = during.sum(), after.sum()
        rows.append(dict(document_number=e.document_number, mechanism=e.mechanism,
                         hs8=key[0], cty=key[1], announcement=e.a, effective=e.e,
                         n_during=len(during), n_after=len(after),
                         excess_during=ed, excess_after=ea,
                         reversal=(-ea / ed) if ed > 0 else np.nan,
                         band_sd=sd, surged=ed > 1.96 * sd))

r = pd.DataFrame(rows)
r.to_csv(f"counterfactual_episodes_{METRIC}.csv", index=False)
print(f"\ncell-episodes fitted: {len(r):,}  over {r.document_number.nunique()} events")
print(f"  with a surge above the 95% band: {r.surged.sum():,} ({100*r.surged.mean():.1f}%)")

sur = r[r.surged & r.reversal.notna()]
print(f"\nreversal ratio among surges (n={len(sur):,}):")
print(sur.reversal.describe(percentiles=[.1, .25, .5, .75, .9]).round(2).to_string())
print("\nby mechanism:")
print(sur.groupby("mechanism").reversal.agg(["size", "median"]).round(2).to_string())
print(f"\nwrote counterfactual_episodes_{METRIC}.csv")
