"""The reversal ratio measured per event rather than per cell.

reversal_control.py showed the ratio cannot be read one cell at a time: fake events shifted
24 months back produced MORE surges than the real ones, because the ratio is two noisy sums
divided by each other. Averaging across the cells an event touches before taking the ratio
should cancel that noise, at the cost of a much smaller sample: one number per event, not
per cell.

Baseline is still untreated origins of the same product, so nothing is extrapolated:

    gap(cell,t)  = log(cell) - mean log(untreated origins, same product, same month)
    gap(event,t) = value-weighted mean of gap over the cells the event treats
    adj          = gap(event,t) - mean gap over the 12 months before announcement

    excess_during  sum of adj over announcement..effective
    excess_after   sum of adj over the H months after it took effect
    reversal       -excess_after / excess_during

Every run is paired with a placebo that shifts each event back 24 months. If the real
events do not separate from their own placebos, the measure does not work at this level
either, and that is the finding.

Usage:  python3 event_reversal.py
"""
import numpy as np
import pandas as pd
from scipy import stats

H, PRE, SHIFT = 9, 12, 24
REDUCING = {"REVOKE", "DECREASE", "SUSPEND"}

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "ym", "lv", "value"])
df["ym"] = pd.to_datetime(df.ym)

ev = pd.read_csv("events_resolved.csv", dtype={"cty": str})
ep = pd.read_csv("event_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in ep.groupby("document_number")}
ev = ev[(ev.window_days >= 7) & (~ev.action_kind.isin(REDUCING))].copy()
ev["a"] = pd.to_datetime(ev.announcement_date).dt.to_period("M").dt.to_timestamp()
ev["e"] = pd.to_datetime(ev.effective_date).dt.to_period("M").dt.to_timestamp()

all_hs8 = df.hs8.unique()
treated_any = set()
for _, e in ev.iterrows():
    if e.mechanism == "ENUMERATED":
        treated_any |= {(h, e.cty) for h in prods.get(e.document_number, set())}
    elif e.mechanism == "MATERIAL_CLASS":
        chs = set(str(e.chapters).split(";"))
        treated_any |= {(h, e.cty) for h in all_hs8 if h[:2] in chs}
    else:
        treated_any |= {(h, e.cty) for h in all_hs8}

df["tc"] = [k in treated_any for k in zip(df.hs8, df.cty)]
ctrl = df[~df.tc].groupby(["hs8", "ym"], sort=False).lv.mean().rename("ctrl").reset_index()
df = df.merge(ctrl, on=["hs8", "ym"], how="left")
df = df[df.ctrl.notna()].copy()
df["gap"] = df.lv - df.ctrl
print(f"rows with a usable control: {len(df):,}")

cells_of = {}
for _, e in ev.iterrows():
    if e.mechanism == "ENUMERATED":
        cells_of[e.name] = prods.get(e.document_number, set())
    elif e.mechanism == "MATERIAL_CLASS":
        chs = set(str(e.chapters).split(";"))
        cells_of[e.name] = {h for h in all_hs8 if h[:2] in chs}
    else:
        cells_of[e.name] = set(all_hs8)


def run(shift_months):
    out = []
    for i, e in ev.iterrows():
        a = e.a - pd.DateOffset(months=shift_months)
        eff = e.e - pd.DateOffset(months=shift_months)
        d = df[(df.cty == e.cty) & (df.hs8.isin(cells_of[i]))]
        if d.empty:
            continue
        d = d[(d.ym >= a - pd.DateOffset(months=PRE)) & (d.ym <= eff + pd.DateOffset(months=H))]
        if d.empty:
            continue
        # weight each cell by its own pre-window size so big cells carry more
        w = d[d.ym < a].groupby(["hs8", "cty"]).value.mean().rename("w")
        d = d.merge(w, on=["hs8", "cty"], how="inner")
        if d.empty:
            continue
        g = (d.assign(wx=d.gap * d.w).groupby("ym")
               .apply(lambda x: x.wx.sum() / x.w.sum(), include_groups=False)
               .sort_index())
        base = g[g.index < a]
        if len(base) < PRE - 3:
            continue
        adj = g - base.mean()
        during = adj[(adj.index >= a) & (adj.index <= eff)]
        after = adj[(adj.index > eff) & (adj.index <= eff + pd.DateOffset(months=H))]
        if len(during) == 0 or len(after) < 6:
            continue
        ed, ea = during.sum(), after.sum()
        out.append(dict(document_number=e.document_number, mechanism=e.mechanism,
                        cty=e.cty, n_cells=d.groupby(["hs8", "cty"]).ngroups,
                        excess_during=ed, excess_after=ea, base_sd=float(base.std(ddof=1)),
                        surged=ed > 1.96 * float(base.std(ddof=1)) * np.sqrt(len(during)),
                        reversal=(-ea / ed) if ed > 0 else np.nan))
    return pd.DataFrame(out)


real = run(0)
plac = run(SHIFT)
real.to_csv("event_reversal_real.csv", index=False)
plac.to_csv("event_reversal_placebo.csv", index=False)

for lbl, r in [("REAL", real), (f"PLACEBO (-{SHIFT}m)", plac)]:
    s = r[r.surged]
    print(f"\n{lbl}: {len(r)} event-partner groups, {len(s)} with a surge above the band")
    if len(s):
        print(f"  excess_during  median {s.excess_during.median():+.3f}")
        print(f"  reversal       median {s.reversal.median():+.2f}   "
              f"n with ratio {s.reversal.notna().sum()}")

print("\n--- does the real set separate from its own placebo? ---")
a, b = real[real.surged].excess_during, plac[plac.surged].excess_during
print(f"surge rate        real {real.surged.mean():.1%}  placebo {plac.surged.mean():.1%}")
if len(a) > 2 and len(b) > 2:
    u = stats.mannwhitneyu(a, b, alternative="greater")
    print(f"excess_during     real median {a.median():+.3f} vs placebo {b.median():+.3f}"
          f"   Mann-Whitney p = {u.pvalue:.3f}")
ra, rb = real[real.surged].reversal.dropna(), plac[plac.surged].reversal.dropna()
if len(ra) > 2 and len(rb) > 2:
    u = stats.mannwhitneyu(ra, rb, alternative="greater")
    print(f"reversal          real median {ra.median():+.2f} vs placebo {rb.median():+.2f}"
          f"   Mann-Whitney p = {u.pvalue:.3f}")

print("\nper-event detail (real, surged only):")
s = real[real.surged].sort_values("reversal")
if len(s):
    print(s[["document_number", "mechanism", "cty", "n_cells",
             "excess_during", "excess_after", "reversal"]].round(2).to_string(index=False))
