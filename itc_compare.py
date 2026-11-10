"""Aftermath for AD/CVD cases that became orders against cases the ITC voted negative.

Uses the stacks and estimator from adcvd_stacked.py, split by what happened at the final stage:
  order      the episode's case numbers appear in a harvested order notice, or events/itc_check.py
             found an order notice or an affirmative ITC final for that country
  negative   events/itc_check.py found a negative ITC final determination for that country
Unresolved episodes are left out. Preliminary dated before mid-2025 and full 18-month follow-up.

Descriptive only. Whether a case ends in an order is decided by the ITC on the record, which
includes the import trend itself, so the two groups are selected, not randomly assigned.

Usage:  python3 itc_compare.py      # from the repo root
"""
import re
import sys

sys.argv = ["adcvd_stacked.py"]
sys.path.insert(0, ".")
import adcvd_stacked as S  # noqa: E402  (loads events, episodes and the panel)
import pandas as pd  # noqa: E402

CASE = re.compile(r"\b([AC])-(\d{3})-(\d{3})\b")
docs = S.pd.read_csv("events/adcvd_events.csv", dtype={"cty": str}).drop_duplicates("document_number")
allc = {d: {"-".join(m) for m in CASE.findall(open(f"events/raw/{d}.txt", errors="ignore").read())}
        for d in docs.document_number}
order_cases = set().union(*[allc[d] for d in docs[docs.stage == "order"].document_number])

ep = S.ep.copy()
ep["linked"] = ep.docs.str.split(";").map(lambda ds: any(allc.get(d, set()) & order_cases for d in ds))
pc = pd.read_csv("events/itc_check_by_country.csv", dtype={"cty": str})
key = {(r.ini, r.cty): r.verdict for r in pc.itertuples()}
ep["verdict"] = [("order" if l else {"verified negative": "negative", "verified order": "order"}
                  .get(key.get((i, c)), "unresolved")) for l, i, c in zip(ep.linked, ep.ini, ep.cty)]
cut = 2025 * 12 + 5
ep = ep[(ep.b < cut) & (ep.b + S.K_HI <= S.M_LAST)]
print(ep.verdict.value_counts())

real = pd.read_parquet("panel/adcvd_stacks_real.parquet")
rows, paths = [], []
for v in ["order", "negative"]:
    ids = set(ep[ep.verdict == v].index)
    d = real[real.sid.isin(ids)].reset_index(drop=True)
    S.report(d, f"final stage: {v}", rows, paths)
out = pd.DataFrame(rows)
out.to_csv("itc_compare.csv", index=False)
pd.concat(paths).to_csv("itc_compare_paths.csv", index=False)
print("wrote itc_compare.csv, itc_compare_paths.csv")
