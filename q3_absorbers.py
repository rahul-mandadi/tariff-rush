"""When a tariff displaces volume from one origin, which origins absorb it?

This decides the project's stakeholder. If a few named origins absorb the volume, there is a
lane story: same US port, different ocean leg, different transit time and service string, and
carriers and forwarders plan exactly that. If absorption is spread thinly across dozens of
origins, no single lane changes enough to matter and the exposure sits with suppliers and
lenders instead.

For each AD/CVD case, within the products it names:
  share(origin) before = that origin's share of the product basket, 12 months pre-initiation
  share(origin) after  = the same, 12 months from the preliminary determination
  delta                = after - before, so the treated origin's loss is spread over the rest

Concentration of the positive deltas is the whole question:
  top1, top3   fraction of all gains taken by the largest one and three absorbers
  1/HHI        effective number of absorbers. Near 1 means one country took it, near 20
               means it dissolved into the background.

Paired with the usual 24 month placebo, because share churn happens anyway. The placebo is the
benchmark for "how concentrated do share shifts look when nothing happened".

Usage:  python3 q3_absorbers.py [--h 12]
"""
import sys
import numpy as np
import pandas as pd
from scipy import stats

args = sys.argv
H = int(args[args.index("--h")+1]) if "--h" in args else 12
PRE, SHIFT, MIN_W, MIN_LOSS = 12, 24, 60, 0.02

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "ym", "value"])
df["ym"] = pd.to_datetime(df.ym)
# analysis.parquet drops the partner name, so take the lookup from the HS8 panel
_n = pd.read_parquet("panel/hs8/2024-06.parquet", columns=["cty", "cty_name"]).drop_duplicates()
names = dict(zip(_n.cty, _n.cty_name))

e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
p = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in p.groupby("document_number")}
e = e[(e.stage == "preliminary") & e.window_days.notna() & (e.window_days >= MIN_W)]
e = e[e.document_number.isin(prods)].drop_duplicates(["cty", "initiation_date", "publication_date"]).copy()
e["a"] = pd.to_datetime(e.initiation_date).dt.to_period("M").dt.to_timestamp()
e["b"] = pd.to_datetime(e.publication_date).dt.to_period("M").dt.to_timestamp()
print(f"distinct cases: {len(e)}")

by_prod = {h: g for h, g in df.groupby("hs8", sort=False)}


def run(shift):
    out, gain_rows = [], []
    for _, r in e.iterrows():
        a = r.a - pd.DateOffset(months=shift)
        b = r.b - pd.DateOffset(months=shift)
        hs = [h for h in prods[r.document_number] if h in by_prod]
        if not hs:
            continue
        sub = pd.concat([by_prod[h] for h in hs], ignore_index=True)
        pre = sub[(sub.ym >= a - pd.DateOffset(months=PRE)) & (sub.ym < a)]
        post = sub[(sub.ym >= b) & (sub.ym < b + pd.DateOffset(months=H))]
        if pre.empty or post.empty or pre.value.sum() <= 0 or post.value.sum() <= 0:
            continue
        s_pre = pre.groupby("cty").value.sum() / pre.value.sum()
        s_post = post.groupby("cty").value.sum() / post.value.sum()
        idx = s_pre.index.union(s_post.index)
        d = s_post.reindex(idx, fill_value=0) - s_pre.reindex(idx, fill_value=0)
        loss = -d.get(r.cty, 0.0)
        if loss < MIN_LOSS:          # the treated origin has to actually lose share
            continue
        gains = d[(d > 0) & (d.index != r.cty)]
        if gains.sum() <= 0:
            continue
        w = gains / gains.sum()
        out.append(dict(case=r.document_number, treated=r.cty,
                        treated_name=names.get(r.cty, r.cty), loss=loss,
                        n_origins=len(idx), n_gainers=int((d > 0).sum()),
                        top1=float(w.max()), top3=float(w.nlargest(3).sum()),
                        eff_absorbers=float(1 / (w ** 2).sum()),
                        top_gainer=gains.idxmax(),
                        top_gainer_name=names.get(gains.idxmax(), gains.idxmax())))
        for c, g in gains.nlargest(5).items():
            gain_rows.append(dict(case=r.document_number, treated=r.cty,
                                  gainer=c, gainer_name=names.get(c, c),
                                  share_gain=float(g), frac_of_loss=float(g / loss)))
    return pd.DataFrame(out), pd.DataFrame(gain_rows)


real, gains_real = run(0)
plac, _ = run(SHIFT)
real.to_csv("q3_absorbers.csv", index=False)
gains_real.to_csv("q3_top_gainers.csv", index=False)

print(f"\nepisodes where the treated origin lost >= {MIN_LOSS:.0%} share: "
      f"real {len(real)}, placebo {len(plac)}\n")
print(f"  {'metric':<22}{'real':>10}{'placebo':>10}{'p':>10}")
for c, lbl in [("top1", "top absorber share"), ("top3", "top 3 share"),
               ("eff_absorbers", "effective absorbers"), ("n_gainers", "origins gaining")]:
    a, b = real[c].dropna(), plac[c].dropna()
    pv = stats.mannwhitneyu(a, b, alternative="two-sided").pvalue if min(len(a), len(b)) > 5 else np.nan
    print(f"  {lbl:<22}{a.median():>10.3f}{b.median():>10.3f}{pv:>10.4f}")

print("\nreading: effective absorbers near 1 means one country took it;")
print("         above about 5 means it dissolved into the background.")

print("\n--- who absorbs, overall (top gainer counts) ---")
print(real.top_gainer_name.value_counts().head(10).to_string())

print("\n--- conditional on who was tariffed ---")
for t, g in real.groupby("treated_name"):
    if len(g) < 8:
        continue
    top = g.top_gainer_name.value_counts()
    share = top.iloc[0] / len(g)
    print(f"  {t:<14} n={len(g):>3}  most frequent absorber: {top.index[0]:<16} "
          f"{share:.0%} of cases   median eff_absorbers {g.eff_absorbers.median():.1f}")

print("\n--- how much of the loss does the single top absorber cover? ---")
if len(gains_real):
    t1 = gains_real.sort_values("share_gain", ascending=False).groupby("case").head(1)
    print(f"  median fraction of the treated origin's lost share "
          f"covered by the top absorber: {t1.frac_of_loss.median():.2f}")
