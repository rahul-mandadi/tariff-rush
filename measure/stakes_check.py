"""What is at stake: U.S. imports from the named country in the named products, in the 12 months
before each duty, by the year the duty began, against all U.S. imports that year.

An upper bound. Duty notices list catch-all product codes that also hold goods outside the duty,
so a code's full trade is counted. The 2024 aluminum extrusions cases (14 countries, 96 codes each,
including "other" auto and air-conditioner parts) are the extreme: about 70 billion dollars on their
own. They are kept in the case file and flagged, and the yearly totals are given with and without them.

Reads:  results/adcvd_episodes_collapsed.csv, panel/hs8/*.parquet
Writes: results/stakes_cases.csv (one row per case), results/stakes_by_year.csv (2016 to 2025)
Run:    python3 measure/stakes_check.py      (after measure/adcvd_stacked.py)
"""
import glob

import pandas as pd

ep = pd.read_csv("results/adcvd_episodes_collapsed.csv", dtype={"cty": str})
ep["codes"] = ep.P.str.split(";")
ep["year"] = ep.b // 12                     # b is year * 12 + (month - 1) of the first preliminary
pairs = {(c, h) for c, P in zip(ep.cty, ep.codes) for h in P}

val, tot = {}, {}                           # (country, code, month) -> value; month -> all U.S. imports
for f in sorted(glob.glob("panel/hs8/*.parquet")):
    d = pd.read_parquet(f, columns=["hs8", "cty", "value", "year", "month"])
    m = int(d.year.iloc[0]) * 12 + int(d.month.iloc[0]) - 1
    tot[m] = float(d.value.sum())
    d["cty"], d["hs8"] = d.cty.astype(str), d.hs8.astype(str)
    k = d[[(c, h) in pairs for c, h in zip(d.cty, d.hs8)]]
    for c, h, v in zip(k.cty, k.hs8, k.value):
        val[(c, h, m)] = val.get((c, h, m), 0.0) + float(v)
assert len(tot) == 140, len(tot)

ep["pre12"] = [sum(val.get((c, h, m), 0.0) for h in P for m in range(b - 12, b))
               for c, P, b in zip(ep.cty, ep.codes, ep.b)]
ALU = ["2024-05068", "2024-05070", "2024-09931", "2024-09969"]   # aluminum extrusions, 2024
alu_clusters = ep.loc[ep.docs.str.contains("|".join(ALU)), "cluster"].unique()
ep["aluminum_2024"] = ep.cluster.isin(alu_clusters)
assert ep.aluminum_2024.sum() == 14, ep.aluminum_2024.sum()
ep["n_codes"] = ep.codes.map(len)
ep[["cty", "docs", "year", "n_codes", "pre12", "aluminum_2024"]].to_csv("results/stakes_cases.csv", index=False)

yr_tot = pd.Series(tot).groupby(lambda m: m // 12).sum()
rows = []
for y in range(2016, 2026):
    e = ep[ep.year == y]
    rows.append(dict(year=y, cases=len(e), pre12_bn=e.pre12.sum() / 1e9,
                     aluminum_2024_bn=e[e.aluminum_2024].pre12.sum() / 1e9, us_imports_bn=yr_tot[y] / 1e9))
r = pd.DataFrame(rows)
r.to_csv("results/stakes_by_year.csv", index=False)

e_ = ep[(ep.year >= 2016) & (ep.year <= 2025)]
no_alu = r.pre12_bn - r.aluminum_2024_bn
print(r.round(2).to_string(index=False))
print(f"\n2016 to 2025, {len(e_)} cases. A year: {r.pre12_bn.mean():.1f} bn with every case "
      f"({100 * r.pre12_bn.sum() / r.us_imports_bn.sum():.2f}% of U.S. imports), {no_alu.mean():.1f} bn "
      f"without the 2024 aluminum cases ({100 * no_alu.sum() / r.us_imports_bn.sum():.2f}%).")
print(f"One case: median {e_.pre12.median() / 1e6:.0f} m, middle half {e_.pre12.quantile(.25) / 1e6:.0f} "
      f"to {e_.pre12.quantile(.75) / 1e6:.0f} m.")
print("wrote results/stakes_cases.csv, results/stakes_by_year.csv")
