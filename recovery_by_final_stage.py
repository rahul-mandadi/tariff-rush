"""Recovery categories (recovery_benchmark.py) split by how the case ended at the final stage.

The ITC's final injury vote comes a few months after the preliminary and is public, so it is a
second point at which a sourcing team can update. Final stage per episode as in
itc_compare.py: order (linked to an order notice, or verified order) or negative (verified
negative ITC final for that country). Episode-weighted, 90 percent bootstrap intervals over
investigation groups. Fall threshold 20 percent.

Usage:  python3 recovery_by_final_stage.py      # after itc_compare.py has written its log
"""
import re

import numpy as np
import pandas as pd

import recovery_benchmark as R

CASE = re.compile(r"\b([AC])-(\d{3})-(\d{3})\b")
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
docs = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str}).drop_duplicates("document_number")
allc = {d: {"-".join(m) for m in CASE.findall(open(f"events/raw/{d}.txt", errors="ignore").read())}
        for d in docs.document_number}
order_cases = set().union(*[allc[d] for d in docs[docs.stage == "order"].document_number])
linked = ep.docs.str.split(";").map(lambda ds: any(allc.get(d, set()) & order_cases for d in ds))
pc = pd.read_csv("events/itc_check_by_country.csv", dtype={"cty": str})
key = {(r.ini, r.cty): r.verdict for r in pc.itertuples()}
stage = pd.Series([("order" if l else {"verified negative": "negative", "verified order": "order"}
                    .get(key.get((i, c)), "unresolved")) for l, i, c in zip(linked, ep.ini, ep.cty)])

p = pd.read_csv("recovery_pairs_real_fall20.csv", dtype={"hs8": str})
p = p[p.category != "censored"]
p["stage"] = p.sid.map(stage)
p = p[p.sid.map(ep.b) < 2025 * 12 + 5]
rows = []
for s in ["order", "negative"]:
    g = p[p.stage == s]
    sh = R.shares(g)
    ci = R.boot(g, R.shares)
    print(f"[{s}] pairs {len(g):,}, episodes {g.sid.nunique()}, groups {g.cluster.nunique()}")
    for c in R.CATS:
        print(f"  {c:<14} {sh[c]:.3f}  [{ci.loc[c, 0.05]:.3f}, {ci.loc[c, 0.95]:.3f}]")
        rows.append(dict(stage=s, category=c, value=sh[c], lo=ci.loc[c, 0.05], hi=ci.loc[c, 0.95],
                         episodes=g.sid.nunique(), groups=g.cluster.nunique()))
    k = R.km(g)
    print("  KM recovered by 6 / 12 / 18 months after the fall: "
          f"{k[6]:.2f} / {k[12]:.2f} / {k[18]:.2f}")
    for t in [6, 12, 18]:
        rows.append(dict(stage=s, category=f"KM recovered by {t}", value=k[t],
                         episodes=g.sid.nunique(), groups=g.cluster.nunique()))
pd.DataFrame(rows).to_csv("recovery_by_final_stage.csv", index=False)
print("wrote recovery_by_final_stage.csv")
