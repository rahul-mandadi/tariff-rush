"""Comparison panels limited to what was known on each decision date, for the forecasts.

A rival country is left out only if its own duty was public by the case's first preliminary, and
products count only if named by then.

Reads:  everything measure/adcvd_stacked.py reads (it imports that script)
Writes: panel/adcvd_stacks_decision.parquet, recovery_pairs_decision_fall20.csv,
        s301_adcvd_pairs_h16_decision.csv
Run:    python3 measure/build_decision_stacks.py      (after measure/adcvd_stacked.py)
"""
import sys

sys.argv = ["adcvd_stacked.py"]
import adcvd_stacked as S  # noqa: E402  (loads events, episodes and the panel)
import pandas as pd  # noqa: E402

sys.path.insert(0, ".")  # the shared modules are at the repo root
import recovery_lib as RL  # noqa: E402

d = S.build(0, decision=True)

# checks that fail loudly if the rule is ever broken
ep = S.ep
cells = d[["sid", "hs8", "cty"]].drop_duplicates()
for s_, g in cells.groupby("sid"):
    assert set(g.hs8) <= set(ep.P0[s_]), f"episode {s_}: a product not named by its first preliminary"
    tc = ep.cty[s_]
    for h, c in g[g.cty != tc][["hs8", "cty"]].itertuples(index=False):
        assert not any(S.ep.b[s_] - 36 <= bb and fd <= ep["first_date"][s_]
                       for bb, fd in S.named_date.get((h, c), [])), f"episode {s_}: rival {c} on {h}"
print(f"checks passed: every product named by the first preliminary; no kept rival had a case "
      f"published on or before it (episodes whose companion notices add products later: "
      f"{(ep.P0 != ep.P).sum()})")
d.to_parquet("panel/adcvd_stacks_decision.parquet", index=False)
ref = pd.read_parquet("panel/adcvd_stacks_real.parquet", columns=["sid", "hs8", "cty"]).drop_duplicates()
now = d[["sid", "hs8", "cty"]].drop_duplicates()
print(f"decision-time panels: {now.sid.nunique()} episodes, {len(now):,} product-country cells "
      f"(hindsight panels: {ref.sid.nunique()}, {len(ref):,})")
b_of, last = S.ep.b.to_dict(), int(d.m.max())
for H, out in [(18, "recovery_pairs_decision_fall20.csv"), (16, "s301_adcvd_pairs_h16_decision.csv")]:
    p = RL.categorize(d, H, b_of, last)
    p["cluster"] = p.sid.map(S.ep.cluster)
    p["year"] = p.sid.map(S.ep.b) // 12
    p.to_csv(out, index=False)
    c = p[p.category != "censored"]
    w = 1.0 / c.groupby("sid").sid.transform("size")
    print(f"H = {H}: complete pairs {len(c):,}, episodes {c.sid.nunique()}; shares "
          + ", ".join(f"{k} {v:.3f}" for k, v in (w.groupby(c.category).sum() / w.sum()).items()))
print("wrote panel/adcvd_stacks_decision.parquet, recovery_pairs_decision_fall20.csv, "
      "s301_adcvd_pairs_h16_decision.csv")
