"""Section 301 Lists 1 to 3: what happened to China's position in each taxed product.

Same design as the AD/CVD work: for each list, a stack of its products with China and every rival
country that traded them in k -18..-7, months with no trade kept as zeros, reference k -18..-13.
Rivals named on the same product by an AD/CVD case with k = 0 within 36 months before to 18 after
are left out, and so are products where China itself had such a case, so the comparison isolates
Section 301. Fake date: the same lists 24 months earlier, cohort rebuilt from its own window.

Horizon: every window stops at January 2020, before China's COVID shutdown, which would otherwise
read as a tariff effect. List 3 (September 2018) then has 16 months, so the outcomes use H = 16
throughout, with "stopped trading" meaning no imports in months 11 to 16, and the AD/CVD rates are
recomputed at the same horizon for the comparison.

Unit: one product. Each list is one tariff date, so there is no honest standard error for the
list-level effect; the shares carry 90 percent intervals from resampling 2-digit chapters, which
covers product heterogeneity but not the common shock of each list date.

First, a check that recovery_lib.categorize reproduces recovery_pairs_real_fall20.csv on the AD/CVD
stacks at H = 18.

Usage:  python3 sec301_benchmark.py
"""
import numpy as np
import pandas as pd

import recovery_lib as RL

H, SHIFT, CHINA, CAP = 16, 24, "5700", 2020 * 12 + 0
B = 1000
rng = np.random.default_rng(0)
CATS = ["no fall", "recovered", "not recovered", "exited"]
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})

# ---------------------------------------------------------------- check against recovery_benchmark
st = pd.read_parquet("panel/adcvd_stacks_real.parquet")
chk = RL.categorize(st, 18, ep.b.to_dict(), int(st.m.max()))
ref = pd.read_csv("recovery_pairs_real_fall20.csv", dtype={"hs8": str})
m = chk.merge(ref[["sid", "hs8", "category"]].assign(hs8=lambda x: x.hs8.str.zfill(8)),
              on=["sid", "hs8"], suffixes=("", "_ref"))
print(f"check: {len(m):,} of {len(ref):,} pairs matched; categories identical: "
      f"{(m.category == m.category_ref).mean():.4f}")
assert len(m) == len(ref) and (m.category == m.category_ref).all()


def shares(p, w):
    c = p[p.category != "censored"]
    ww = w.loc[c.index]
    return (ww.groupby(c.category).sum() / ww.sum()).reindex(CATS, fill_value=0.0)


def boot(p, w, groups):
    gs = groups.loc[p.index]
    cl = gs.unique()
    idx = {c: p.index[gs == c] for c in cl}
    draws = []
    for _ in range(B):
        ii = np.concatenate([idx[c] for c in rng.choice(cl, len(cl), replace=True)])
        q = p.loc[ii].reset_index(drop=True)
        draws.append(shares(q, w.loc[ii].reset_index(drop=True)))
    return pd.concat(draws, axis=1).quantile([0.05, 0.95], axis=1).T


# AD/CVD at the same horizon, episode-weighted
ad = RL.categorize(st, H, ep.b.to_dict(), int(st.m.max()))
ad = ad[ad.category != "censored"].reset_index(drop=True)
ad["cluster"] = ad.sid.map(ep.cluster)
w_ad = 1.0 / ad.groupby("sid").sid.transform("size")
ad_sh = shares(ad, w_ad)
ad_ci = boot(ad, w_ad, ad.cluster)

# ---------------------------------------------------------------- Section 301 stacks
L = pd.read_csv("events/s301_products.csv", dtype={"hs8": str})
L["b"] = pd.to_datetime(L.start).map(RL.month)
prods = set(L.hs8)
raw = RL.load_raw(prods, L.b.min() - SHIFT - 18, CAP)
epP = [(set(P.split(";")), c, b) for P, c, b in zip(ep.P, ep.cty, ep.b)]
stacks, info = [], []
for i, (name, g) in enumerate(L.groupby("list"), start=1):
    b = int(g.b.iloc[0])
    for shift, tag in [(0, "real"), (SHIFT, "placebo")]:
        b0 = b - shift
        cap = CAP if shift == 0 else b0 + H
        excl, china_case = {}, set()
        for P, c, bb in epP:
            if b0 - 36 <= bb <= b0 + 18:
                for h in P & set(g.hs8):
                    if c == CHINA:
                        china_case.add(h)
                    else:
                        excl.setdefault(h, set()).add(c)
        use = set(g.hs8) - china_case
        d = RL.build_stack(raw, use, CHINA, b0, cap, excl)
        sid = i + (100 if shift else 0)
        d["sid"], d["list"], d["sample"] = sid, name, tag
        stacks.append(d)
        info.append(dict(list=name, sample=tag, sid=sid, b=b0, products_listed=len(g),
                         dropped_china_adcvd=len(china_case), products_in_stack=d.hs8.nunique(),
                         rivals_mean=d[~d.treated].groupby("hs8").cty.nunique().mean()))
S = pd.concat(stacks, ignore_index=True)
info = pd.DataFrame(info)
print("\n", info.to_string(index=False))
S.to_parquet("panel/s301_stacks.parquet", index=False)

b_of = info.set_index("sid").b.to_dict()
res = []
for tag in ["real", "placebo"]:
    d = S[S["sample"] == tag]
    last = CAP if tag == "real" else None
    # each placebo list ends at its own b + H; categorize uses one last month, so run per list
    parts = []
    for sid, g in d.groupby("sid"):
        parts.append(RL.categorize(g, H, b_of, CAP if tag == "real" else b_of[sid] + H))
    p = pd.concat(parts, ignore_index=True)
    p["list"] = p.sid.map(info.set_index("sid").list)
    p["chapter"] = p.hs8.str[:2]
    p.to_csv(f"s301_pairs_{tag}.csv", index=False)
    c = p[p.category != "censored"].reset_index(drop=True)
    w = pd.Series(1.0, index=c.index)
    sh, ci = shares(c, w), boot(c, w, c.chapter)
    print(f"\n[Section 301, {tag}] products {len(c):,} (censored {(p.category == 'censored').sum()}), "
          f"chapters {c.chapter.nunique()}")
    for k in CATS:
        print(f"  {k:<14} {sh[k]:.3f}  [{ci.loc[k, 0.05]:.3f}, {ci.loc[k, 0.95]:.3f}]")
        res.append(dict(sample=f"Section 301, {tag}", measure=k, value=sh[k], lo=ci.loc[k, 0.05],
                        hi=ci.loc[k, 0.95], n=len(c)))
    for name, g in c.groupby("list"):
        s2 = shares(g, w.loc[g.index])
        print(f"    {name}: " + ", ".join(f"{k} {s2[k]:.2f}" for k in CATS) + f"  (n={len(g)})")
        for k in CATS:
            res.append(dict(sample=f"Section 301, {tag}, {name}", measure=k, value=s2[k], n=len(g)))
    # China's value-weighted share of the listed products, before and late
    agg = d.groupby("k").apply(lambda x: x[x.treated].value.sum() / x.value.sum(), include_groups=False)
    before, late = agg.loc[-18:-13].mean(), agg.loc[H - 5:H].mean()
    print(f"  China's share of these products' imports (value-weighted): k -18..-13 {before:.3f}, "
          f"k {H - 5}..{H} {late:.3f}, change {np.log(late / before):+.3f} log points")
    res.append(dict(sample=f"Section 301, {tag}", measure="China share before", value=before))
    res.append(dict(sample=f"Section 301, {tag}", measure="China share late", value=late))

print(f"\n[AD/CVD at H = {H}] pairs {len(ad):,}, episodes {ad.sid.nunique()}, groups {ad.cluster.nunique()}")
for k in CATS:
    print(f"  {k:<14} {ad_sh[k]:.3f}  [{ad_ci.loc[k, 0.05]:.3f}, {ad_ci.loc[k, 0.95]:.3f}]")
    res.append(dict(sample="AD/CVD, same horizon", measure=k, value=ad_sh[k], lo=ad_ci.loc[k, 0.05],
                    hi=ad_ci.loc[k, 0.95], n=len(ad)))
ad.to_csv("s301_adcvd_pairs_h16.csv", index=False)
pd.DataFrame(res).to_csv("s301_benchmark.csv", index=False)
info.to_csv("s301_stacks_info.csv", index=False)
print("wrote s301_benchmark.csv, s301_pairs_{real,placebo}.csv, s301_adcvd_pairs_h16.csv, "
      "s301_stacks_info.csv, panel/s301_stacks.parquet")
