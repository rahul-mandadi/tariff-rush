"""Rush and repayment around antidumping and countervailing duty cases.

Why these events and not the Section 232/301/IEEPA set: there are far more of them, each
names one country and an explicit product scope, and the window between a case becoming
public and duties being collected is months rather than days. Monthly import data cannot
resolve a four day window, which is the median in the other event set. It can resolve six.

The clock runs from the initiation date, which is when the case becomes public and importers
can begin buying ahead, to the preliminary determination, which is when duties start being
collected. Both come out of the preliminary notice itself.

Baseline is the same product from origins not named by the case, in the same month. Nothing
is extrapolated, because placebo tests showed a fitted baseline drifts far enough to
manufacture a result (see PHASE2_RESULTS.md).

Every number is produced twice, once for the real events and once with every event shifted
back 24 months. A result that does not separate from its own placebo is not reported as a
result.

Usage:  python3 adcvd_analysis.py [--h 9] [--min-window 60]
"""
import sys
import numpy as np
import pandas as pd

args = sys.argv
H = int(args[args.index("--h")+1]) if "--h" in args else 9
MIN_W = int(args[args.index("--min-window")+1]) if "--min-window" in args else 60
PRE, SHIFT = 12, 24

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "ym", "lv", "value"])
df["ym"] = pd.to_datetime(df.ym)

e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str, "hs8": str})
p = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
e = e[(e.stage == "preliminary") & e.window_days.notna() & (e.window_days >= MIN_W)].copy()
e["init"] = pd.to_datetime(e.initiation_date)
e["pub"] = pd.to_datetime(e.publication_date)
# month grain
e["a"] = e.init.dt.to_period("M").dt.to_timestamp()
e["b"] = e.pub.dt.to_period("M").dt.to_timestamp()
prods = {d: set(g.hs8) for d, g in p.groupby("document_number")}
e = e[e.document_number.isin(prods)]
print(f"AD/CVD preliminary determinations with window >= {MIN_W}d: "
      f"{len(e):,} doc-country rows, {e.document_number.nunique():,} documents, "
      f"{e.cty.nunique()} countries")
print(f"window days: median {e.window_days.median():.0f}  "
      f"IQR {e.window_days.quantile(.25):.0f}-{e.window_days.quantile(.75):.0f}")

# cells any case names, held out of every control group
treated_any = set()
for _, r in e.iterrows():
    treated_any |= {(h, r.cty) for h in prods[r.document_number]}
df["tc"] = [k in treated_any for k in zip(df.hs8, df.cty)]
ctrl = df[~df.tc].groupby(["hs8", "ym"], sort=False).lv.mean().rename("ctrl").reset_index()
df = df.merge(ctrl, on=["hs8", "ym"], how="left")
df = df[df.ctrl.notna()].copy()
df["gap"] = df.lv - df.ctrl
print(f"panel rows with an untreated control: {len(df):,}")
gaps = {k: g.set_index("ym").gap.sort_index() for k, g in df.groupby(["hs8", "cty"], sort=False)}
sizes = df.groupby(["hs8", "cty"]).value.mean().to_dict()


def episodes(shift):
    out = []
    for _, r in e.iterrows():
        a = r.a - pd.DateOffset(months=shift)
        b = r.b - pd.DateOffset(months=shift)
        cells = [(h, r.cty) for h in prods[r.document_number] if (h, r.cty) in gaps]
        if not cells:
            continue
        per = []
        for k in cells:
            s = gaps[k]
            base = s[(s.index >= a - pd.DateOffset(months=PRE)) & (s.index < a)]
            if len(base) < PRE - 3:
                continue
            adj = s - base.mean()
            during = adj[(adj.index >= a) & (adj.index < b)]
            after = adj[(adj.index >= b) & (adj.index < b + pd.DateOffset(months=H))]
            if len(during) < 2 or len(after) < 6:
                continue
            per.append(dict(hs8=k[0], cty=k[1], w=sizes.get(k, 1.0),
                            ed=during.mean(), ea=after.mean(),
                            sd=float(base.std(ddof=1)), n_during=len(during)))
        if not per:
            continue
        d = pd.DataFrame(per)
        w = d.w / d.w.sum()
        ed, ea = float((d.ed * w).sum()), float((d.ea * w).sum())
        sd = float((d.sd * w).sum()) / np.sqrt(len(d))
        out.append(dict(document_number=r.document_number, cty=r.cty, n_cells=len(d),
                        critical_circ=bool(r.get("critical_circ", False)),
                        excess_during=ed, excess_after=ea, sd=sd,
                        surged=ed > 1.96 * sd,
                        reversal=(-ea / ed) if ed > 0 else np.nan))
    return pd.DataFrame(out)


real, plac = episodes(0), episodes(SHIFT)
real.to_csv("adcvd_episodes_real.csv", index=False)
plac.to_csv("adcvd_episodes_placebo.csv", index=False)

print(f"\n{'':22}{'real':>12}{'placebo':>12}")
print(f"{'episodes':<22}{len(real):>12,}{len(plac):>12,}")
for lbl, col in [("mean excess_during", "excess_during"), ("mean excess_after", "excess_after")]:
    print(f"{lbl:<22}{real[col].mean():>12.4f}{plac[col].mean():>12.4f}")
print(f"{'surge rate':<22}{real.surged.mean():>11.1%}{plac.surged.mean():>12.1%}")

from scipy import stats
print("\n--- does the real set separate from its placebo? ---")
for lbl, col in [("excess_during", "excess_during"), ("excess_after", "excess_after")]:
    a, b = real[col].dropna(), plac[col].dropna()
    if len(a) > 5 and len(b) > 5:
        u = stats.mannwhitneyu(a, b, alternative="two-sided")
        t = stats.ttest_ind(a, b, equal_var=False)
        print(f"  {lbl:<16} real {a.median():+.4f}  placebo {b.median():+.4f}   "
              f"MWU p={u.pvalue:.4f}  t p={t.pvalue:.4f}")

print("\n--- the rush: is excess_during above zero? ---")
for lbl, r in [("real", real), ("placebo", plac)]:
    x = r.excess_during.dropna()
    if len(x) > 5:
        t = stats.ttest_1samp(x, 0)
        print(f"  {lbl:<9} n={len(x):>4}  mean {x.mean():+.4f}  "
              f"median {x.median():+.4f}  t={t.statistic:+.2f}  p={t.pvalue:.4f}")

print("\n--- repayment among real surges ---")
s = real[real.surged & real.reversal.notna()]
sp = plac[plac.surged & plac.reversal.notna()]
print(f"  real surges {len(s)}   placebo surges {len(sp)}")
if len(s) > 5:
    print(f"  reversal: median {s.reversal.median():+.2f}  "
          f"mean {s.reversal.mean():+.2f}")
    from label_bands import assign, BANDS
    for nm, g in [("real", s), ("placebo", sp)]:
        if len(g) > 2:
            b = assign(g.reversal).value_counts(normalize=True)
            print(f"  {nm:<9} " + "  ".join(f"{k}:{b.get(k,0):.0%}" for k in BANDS))


# --- does the retroactive-duty risk explain the missing rush? ---
# AD/CVD duties can reach back 90 days before suspension of liquidation, or to the
# initiation notice, whichever is later. Where Commerce raises critical circumstances the
# whole window is exposed, so buying ahead gets taxed anyway. If that provision is what
# deters front-loading, cases carrying it should rush less than cases that do not.
if "critical_circ" in real.columns and real.critical_circ.nunique() > 1:
    print("\n--- rush by retroactive-duty exposure (real events) ---")
    print(f"  {'group':<28}{'n':>6}{'mean excess_during':>21}{'median':>10}")
    for flag, g in real.groupby("critical_circ"):
        lbl = "critical circumstances" if flag else "no critical circumstances"
        print(f"  {lbl:<28}{len(g):>6}{g.excess_during.mean():>21.4f}"
              f"{g.excess_during.median():>10.4f}")
    a = real[~real.critical_circ].excess_during.dropna()
    b = real[real.critical_circ].excess_during.dropna()
    if len(a) > 5 and len(b) > 5:
        u = stats.mannwhitneyu(a, b, alternative="greater")
        t = stats.ttest_ind(a, b, equal_var=False)
        print(f"  without > with ?   MWU p={u.pvalue:.4f}   t p={t.pvalue:.4f}")
