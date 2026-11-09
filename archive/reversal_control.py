"""The reversal ratio, measured against untreated origins instead of an extrapolated trend.

counterfactual_hs8.py fits a baseline per cell and projects it forward. A placebo test at
dates with no tariff shows that baseline drifts: the median cell sits 0.115 log points
BELOW its own projection after twelve months, and only 39.7% sit above it, against 50% if
it were unbiased. Worse, selecting episodes on "excess above the band" preferentially picks
cells whose baseline happened to drift low, and that error carries straight into the after
period. That is enough to manufacture a reversal ratio out of nothing.

So the baseline here is not extrapolated at all. For a treated cell it is the same product
from origins that were not treated, in the same month, which is the comparison the rest of
phase two already uses:

    gap(t)  = log(cell) - mean log(untreated origins of the same product, same month)
    gap_adj = gap(t) - mean gap over the 12 months before announcement

A tariff moves the treated origin relative to the others; a price shock moves them together
and cancels. Nothing is projected, so nothing can drift.

    excess_during  sum of gap_adj over announcement..effective
    excess_after   sum of gap_adj over the H months after it took effect
    reversal       -excess_after / excess_during

Bands come from label_bands.py, unchanged.

Usage:  python3 reversal_control.py [--placebo]
"""
import sys
import numpy as np
import pandas as pd
from label_bands import assign, BANDS

PLACEBO = "--placebo" in sys.argv
H, PRE = 9, 12
REDUCING = {"REVOKE", "DECREASE", "SUSPEND"}

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "chapter", "ym", "lv"])
df["ym"] = pd.to_datetime(df.ym)

ev = pd.read_csv("events_resolved.csv", dtype={"cty": str})
ep = pd.read_csv("event_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in ep.groupby("document_number")}
ev = ev[(ev.window_days >= 7) & (~ev.action_kind.isin(REDUCING))].copy()
ev["a"] = pd.to_datetime(ev.announcement_date).dt.to_period("M").dt.to_timestamp()
ev["e"] = pd.to_datetime(ev.effective_date).dt.to_period("M").dt.to_timestamp()

# every cell that any event touches, so it can be held out of its own control group
treated_any = set()
for _, e in ev.iterrows():
    if e.mechanism == "ENUMERATED":
        treated_any |= {(h, e.cty) for h in prods.get(e.document_number, set())}
    elif e.mechanism == "MATERIAL_CLASS":
        chs = set(str(e.chapters).split(";"))
        treated_any |= {(h, e.cty) for h in df.hs8.unique() if h[:2] in chs}
    else:
        treated_any |= {(h, e.cty) for h in df.hs8.unique()}

key = list(zip(df.hs8, df.cty))
df["is_treated_cell"] = [k in treated_any for k in key]
ctrl = (df[~df.is_treated_cell].groupby(["hs8", "ym"], sort=False).lv.mean()
        .rename("ctrl").reset_index())
df = df.merge(ctrl, on=["hs8", "ym"], how="left")
df["gap"] = df.lv - df.ctrl
df = df[df.gap.notna()]
print(f"rows with an untreated control for the same product-month: {len(df):,}")

gaps = {k: g.set_index("ym").gap.sort_index() for k, g in df.groupby(["hs8", "cty"], sort=False)}

if PLACEBO:
    ev = ev.copy()
    ev["a"] = ev.a - pd.DateOffset(months=24)
    ev["e"] = ev.e - pd.DateOffset(months=24)
    print("PLACEBO: every event shifted 24 months earlier\n")

rows = []
for _, e in ev.iterrows():
    if e.mechanism == "ENUMERATED":
        cells = [(h, e.cty) for h in prods.get(e.document_number, set())]
    elif e.mechanism == "MATERIAL_CLASS":
        chs = set(str(e.chapters).split(";"))
        cells = [k for k in gaps if k[1] == e.cty and k[0][:2] in chs]
    else:
        cells = [k for k in gaps if k[1] == e.cty]
    end = e.e + pd.DateOffset(months=H)
    start = e.a - pd.DateOffset(months=PRE)
    for k in cells:
        s = gaps.get(k)
        if s is None:
            continue
        base = s[(s.index >= start) & (s.index < e.a)]
        if len(base) < PRE - 3:
            continue
        adj = s - base.mean()
        during = adj[(adj.index >= e.a) & (adj.index <= e.e)]
        after = adj[(adj.index > e.e) & (adj.index <= end)]
        if len(during) == 0 or len(after) < 6:
            continue
        ed, ea = during.sum(), after.sum()
        sd = float(base.std(ddof=1))
        rows.append(dict(document_number=e.document_number, mechanism=e.mechanism,
                         hs8=k[0], cty=k[1], excess_during=ed, excess_after=ea,
                         base_sd=sd, surged=ed > 1.96 * sd * np.sqrt(len(during)),
                         reversal=(-ea / ed) if ed > 0 else np.nan))

r = pd.DataFrame(rows)
tag = "_placebo" if PLACEBO else ""
r.to_csv(f"reversal_episodes{tag}.csv", index=False)
print(f"cell-episodes: {len(r):,} over {r.document_number.nunique()} events")
print(f"  surged above the 95% band: {r.surged.sum():,} ({100*r.surged.mean():.1f}%)")
print(f"  (a placebo run should sit near 2.5%)")

sur = r[r.surged & r.reversal.notna()]
if len(sur) < 10:
    print("\ntoo few surges to band"); sys.exit()
print(f"\nreversal ratio among surges (n={len(sur):,}):")
print(sur.reversal.describe(percentiles=[.25, .5, .75]).round(2).to_string())
sur = sur.copy(); sur["band"] = assign(sur.reversal)
print("\nordinal bands:")
for b in BANDS:
    g = sur[sur.band == b]
    print(f"  {b:<24}{len(g):>6,}{len(g)/len(sur):>7.0%}")
print("\nmedian reversal by mechanism:")
print(sur.groupby("mechanism").reversal.agg(["size", "median"]).round(2).to_string())
