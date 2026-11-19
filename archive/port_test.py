"""When volume is displaced from one origin, does it arrive through different districts?

This is the stakeholder objection made testable. Everything else in the project is dollars at
HS8 by country. An operator commits capacity at a facility. So: take the products an AD/CVD
case names, and ask whether the district mix of TOTAL imports of those products changes after
duties start.

  mix shifts     the replacement arrives on different lanes, through different districts.
                 That is a lane story and it changes who gets the boxes.
  mix holds      the same districts handle the same volume from a different flag. An operator
                 sees nothing and we should say so rather than implying otherwise.

Measured as total variation distance between the district share vectors before and after,
which is half the sum of absolute share changes and reads directly as "this fraction of the
volume changed district". Every case is paired with a placebo running the same windows 24
months earlier, because district mix drifts on its own.

Two filters this endpoint needs and the country-only one does not: SUMMARY_LVL must be DET,
and CTY_CODE carries region aggregates (0003 EUROPEAN UNION, 0014 PACIFIC RIM) that are also
4 digits. Real countries are taken from the main panel, whose codes were verified to sum
exactly to the published all-country total.

Usage:  python3 port_test.py
"""
import glob, gzip, json, os
import numpy as np
import pandas as pd

W = 12          # months each side
SHIFT = 24      # placebo offset

real_ctys = set(pd.read_parquet("panel/hs8/2024-06.parquet", columns=["cty"]).cty.unique())
cases = pd.read_csv("port_test_cases.csv", dtype={"cty": str})
prods = pd.read_csv("events/adcvd_products.csv", dtype=str)
print(f"cases {len(cases)}   real country codes {len(real_ctys)}")

frames = []
for p in sorted(glob.glob("port/raw/*.json.gz")):
    with gzip.open(p, "rt") as f:
        d = json.load(f)
    df = pd.DataFrame(d[1:], columns=d[0])
    df = df.loc[:, ~df.columns.duplicated()]
    frames.append(df)
if not frames:
    raise SystemExit("no port/raw -- run port_harvest.py first")
d = pd.concat(frames, ignore_index=True)
d = d[(d.SUMMARY_LVL == "DET") & (d.DISTRICT != "-") & d.CTY_CODE.isin(real_ctys)]
d["value"] = pd.to_numeric(d.GEN_VAL_MO, errors="coerce").fillna(0)
d["hs8"] = d.I_COMMODITY.str[:8]
d["ym"] = pd.to_datetime(d.YEAR + "-" + d.MONTH + "-01")
d = d[d.value > 0]
print(f"district rows: {len(d):,}   districts {d.DISTRICT.nunique()}   "
      f"months {d.ym.nunique()}   ${d.value.sum()/1e9:,.1f}B")


def mix(sub):
    s = sub.groupby("DISTRICT").value.sum()
    return s / s.sum() if s.sum() > 0 else None


def tvd(a, b):
    idx = a.index.union(b.index)
    return float(0.5 * np.abs(a.reindex(idx, fill_value=0) - b.reindex(idx, fill_value=0)).sum())


def run(shift):
    out = []
    for _, c in cases.iterrows():
        hs = set(prods[prods.document_number == c.case_id].hs8)
        sub = d[d.hs8.isin(hs)]
        if sub.empty:
            continue
        a = pd.Timestamp(c.init) - pd.DateOffset(months=shift)
        b = pd.Timestamp(c.pub) - pd.DateOffset(months=shift)
        pre = sub[(sub.ym >= a - pd.DateOffset(months=W)) & (sub.ym < a)]
        post = sub[(sub.ym >= b) & (sub.ym < b + pd.DateOffset(months=W))]
        if pre.empty or post.empty:
            continue
        m_pre, m_post = mix(pre), mix(post)
        if m_pre is None or m_post is None:
            continue
        # where the treated origin landed, before
        t_pre = mix(pre[pre.CTY_CODE == c.cty])
        rec = dict(case_id=c.case_id, country=c.country, regime=c.regime,
                   absorbed=c.absorbed, n_districts=sub.DISTRICT.nunique(),
                   tvd_total=tvd(m_pre, m_post),
                   treated_top_district=(t_pre.idxmax() if t_pre is not None else ""),
                   treated_top_share=(round(float(t_pre.max()), 3) if t_pre is not None else np.nan),
                   pre_usd=float(pre.value.sum()), post_usd=float(post.value.sum()))
        out.append(rec)
    return pd.DataFrame(out)


real, plac = run(0), run(SHIFT)
real.to_csv("port_test_real.csv", index=False)
print("\n=== does the district mix of TOTAL imports shift after duties? ===")
print("tvd = fraction of volume that changed district (0 = identical, 1 = completely different)\n")
m = real[["case_id", "country", "regime", "absorbed", "tvd_total",
          "treated_top_district", "treated_top_share"]].merge(
    plac[["case_id", "tvd_total"]].rename(columns={"tvd_total": "tvd_placebo"}),
    on="case_id", how="left")
print(m.to_string(index=False, float_format=lambda x: f"{x:,.3f}"))

print(f"\nmedian tvd  real {real.tvd_total.median():.3f}   "
      f"placebo {plac.tvd_total.median():.3f}")
for rg, g in m.groupby("regime"):
    print(f"  {rg:<13} real {g.tvd_total.median():.3f}  placebo {g.tvd_placebo.median():.3f}")

# the clearest single case, district by district
if len(real):
    c = cases[cases.case_id == real.sort_values("absorbed", ascending=False).iloc[0].case_id].iloc[0]
    hs = set(prods[prods.document_number == c.case_id].hs8)
    sub = d[d.hs8.isin(hs)]
    a, b = pd.Timestamp(c.init), pd.Timestamp(c.pub)
    pre = sub[(sub.ym >= a - pd.DateOffset(months=W)) & (sub.ym < a)]
    post = sub[(sub.ym >= b) & (sub.ym < b + pd.DateOffset(months=W))]
    t = (pd.DataFrame({"before": mix(pre), "after": mix(post)}).fillna(0) * 100)
    t["change_pp"] = t.after - t.before
    nm = sub.drop_duplicates("DISTRICT").set_index("DISTRICT").DIST_NAME
    t["district"] = nm.reindex(t.index).str[:24]
    print(f"\n=== {c.case_id}, {c.country}, most-absorbed case: district shares (%) ===")
    print(t.reindex(t.change_pp.abs().sort_values(ascending=False).index)
           .head(10)[["district", "before", "after", "change_pp"]]
           .to_string(float_format=lambda x: f"{x:,.1f}"))
