"""The main measurement, split by how the case ended: permanent order or rejected by the ITC.

Reads:  panel/adcvd_stacks_real.parquet, events/adcvd_events.csv, events/itc_check_by_country.csv
Writes: itc_compare.csv, itc_compare_paths.csv
Run:    python3 measure/itc_compare.py      (after events/itc_check.py)
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
