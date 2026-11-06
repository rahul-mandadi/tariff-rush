"""The stacked AD/CVD aftermath, on physical quantity instead of dollar value.

Kylie asked whether the data are inflation-adjusted. In the within-product design a price change
shared by every supplier cancels, but a price change specific to the targeted country does not:
if the duty makes the targeted exporter cut its price, value falls even when tonnage holds. This
reruns adcvd_stacked.py's estimator on quantity, and on value for exactly the same rows, so the two
can be compared on one sample.

A stack's product is kept only if every trading row in its window reports quantity in one unit,
the same unit for every country and month (qty_ok in the panel, one unit across the product's
ten-digit lines). A month with no trade is zero quantity, as for value.

Reads panel/adcvd_stacks_real.parquet and panel/adcvd_stacks_placebo.parquet, written by
adcvd_stacked.py.

Usage:  python3 adcvd_stacked_qty.py
"""
import glob
import sys

sys.argv = ["adcvd_stacked.py"]
import adcvd_stacked as S  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

files = sorted(glob.glob("panel/hs8/*.parquet"))
allP = set().union(*S.ep.P)
q = pd.concat([pd.read_parquet(f, columns=["hs8", "cty", "ym", "value", "qty", "unit", "qty_ok"])
               for f in files])
q = q[q.hs8.isin(allP) & (q.value > 0)]
q["m"] = S.mi(q.ym)
q = q[["hs8", "cty", "m", "qty", "unit", "qty_ok"]]


def attach(st):
    d = st.merge(q, on=["hs8", "cty", "m"], how="left")
    pos = d.value > 0
    bad_row = pos & (~d.qty_ok.fillna(False).astype(bool) | d.qty.isna() | (d.qty <= 0))
    units = d[pos].groupby(["sid", "hs8"]).unit.nunique()
    bad = set(d[bad_row].groupby(["sid", "hs8"]).size().index) | set(units[units > 1].index)
    key = pd.MultiIndex.from_arrays([d.sid, d.hs8])
    d = d[~key.isin(list(bad))].copy()
    d["qty"] = np.where(d.value > 0, d.qty, 0.0)
    u = d[d.value > 0].groupby(["sid", "hs8"]).unit.first()
    return d.drop(columns=["unit", "qty_ok"]), u


if __name__ == "__main__":
    real = pd.read_parquet("panel/adcvd_stacks_real.parquet")
    plac = pd.read_parquet("panel/adcvd_stacks_placebo.parquet")
    full = real[real.sid.map(lambda s: S.ep.b[s] + S.K_HI <= S.M_LAST)]
    both = set(full.sid) & set(plac.sid)
    rq, ru = attach(full.reset_index(drop=True))
    pq, _ = attach(plac[plac.sid.isin(both)].reset_index(drop=True))
    tr = rq[rq.treated]
    print(f"real: kept {rq[['sid','hs8']].drop_duplicates().shape[0]:,} stack-products of "
          f"{full[['sid','hs8']].drop_duplicates().shape[0]:,}; targeted value share kept "
          f"{tr.value.sum() / full[full.treated].value.sum():.2f}")
    print("units:", ru.value_counts().head(6).to_dict())

    rows, paths = [], []
    for d, label in [(rq, "real, complete follow-up"), (pq, "placebo, 24 months earlier")]:
        d = d.reset_index(drop=True)
        for col in ["qty", "value"]:
            dd = d.assign(value=d[col])          # report() reads the outcome from `value`
            S.report(dd, f"{label} [{col}]", rows, paths)
    out = pd.DataFrame(rows)
    paths = pd.concat(paths)
    # report() names its outcomes after value; relabel the rows estimated on quantity
    for t in (out, paths):
        q_rows = t["sample"].str.contains(r"\[qty\]")
        t.loc[q_rows, "outcome"] = t.loc[q_rows, "outcome"].str.replace("value", "quantity")
    out.to_csv("adcvd_stacked_qty.csv", index=False)
    paths.to_csv("adcvd_stacked_qty_paths.csv", index=False)
    print("wrote adcvd_stacked_qty.csv, adcvd_stacked_qty_paths.csv")
