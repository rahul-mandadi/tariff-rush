"""What happened to China's share in each product of the 2018 Section 301 tariffs.

Reads:  events/s301_products.csv, panel/hs8/, panel/adcvd_stacks_real.parquet,
        results/adcvd_episodes_collapsed.csv, results/recovery_pairs_real_fall20.csv
Writes: results/s301_benchmark.csv, results/s301_pairs_*.csv, results/s301_adcvd_pairs_h16.csv, results/s301_stacks_info.csv,
        panel/s301_stacks.parquet
Run:    python3 section301/sec301_benchmark.py
        (after events/build_301_lists.py and measure/recovery_benchmark.py)
"""
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, ".")  # the shared modules are at the repo root
import recovery_lib as RL  # noqa: E402

H, SHIFT, CHINA, CAP = 16, 24, "5700", 2020 * 12 + 0
B = 1000
rng = np.random.default_rng(0)
CATS = ["no fall", "recovered", "not recovered", "exited"]
ep = pd.read_csv("results/adcvd_episodes_collapsed.csv", dtype={"cty": str})

# ---------------------------------------------------------------- check against recovery_benchmark
st = pd.read_parquet("panel/adcvd_stacks_real.parquet")
chk = RL.categorize(st, 18, ep.b.to_dict(), int(st.m.max()))
ref = pd.read_csv("results/recovery_pairs_real_fall20.csv", dtype={"hs8": str})
m = chk.merge(ref[["sid", "hs8", "category"]].assign(hs8=lambda x: x.hs8.str.zfill(8)),
              on=["sid", "hs8"], suffixes=("", "_ref"))
same = lambda a, b: ((a == b) | (pd.isna(a) & pd.isna(b))).all()  # noqa: E731
cols = ["category", "bench", "fell_at", "rec_at", "follow"]
m = chk.merge(ref.assign(hs8=lambda x: x.hs8.str.zfill(8))[["sid", "hs8"] + cols], on=["sid", "hs8"],
              suffixes=("", "_ref"))
ok = {c: bool(same(m[c], m[c + "_ref"])) if c != "bench" else bool(np.allclose(m[c], m[c + "_ref"]))
      for c in cols}
print(f"check: {len(m):,} of {len(ref):,} pairs matched; identical on {ok}")
assert len(m) == len(ref) and all(ok.values())


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
# each episode's first preliminary date, for the strict sample's exact-date rule
ev = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str}).drop_duplicates("document_number")
pubd = pd.to_datetime(ev.set_index("document_number").publication_date)
first = [min(pubd[d] for d in ds.split(";")) for ds in ep.docs]
epP = [(set(P.split(";")), c, b, f) for P, c, b, f in zip(ep.P, ep.cty, ep.b, first)]
stacks, info = [], []
for i, (name, g) in enumerate(L.groupby("list"), start=1):
    b = int(g.b.iloc[0])
    start = pd.Timestamp(g.start.iloc[0])
    for shift, tag in [(0, "real"), (SHIFT, "placebo"), (0, "real, strict")]:
        b0 = b - shift
        cap = CAP if shift == 0 else b0 + H
        # clean controls use AD/CVD cases from 36 months before to 18 after; the strict version,
        # for the transfer tests, uses only cases whose first preliminary was published on or
        # before the list's start date (exact dates)
        excl, china_case = {}, set()
        for P, c, bb, fd in epP:
            known = fd <= start if tag == "real, strict" else bb <= b0 + 18
            if b0 - 36 <= bb and known:
                for h in P & set(g.hs8):
                    if c == CHINA:
                        china_case.add(h)
                    else:
                        excl.setdefault(h, set()).add(c)
        use = set(g.hs8) - china_case
        d = RL.build_stack(raw, use, CHINA, b0, cap, excl)
        sid = i + (100 if shift else 0) + (200 if tag == "real, strict" else 0)
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
for tag in ["real", "placebo", "real, strict"]:
    d = S[S["sample"] == tag]
    last = CAP if tag == "real" else None
    # each placebo list ends at its own b + H; categorize uses one last month, so run per list
    parts = []
    for sid, g in d.groupby("sid"):
        parts.append(RL.categorize(g, H, b_of, b_of[sid] + H if tag == "placebo" else CAP))
    p = pd.concat(parts, ignore_index=True)
    p["list"] = p.sid.map(info.set_index("sid").list)
    p["chapter"] = p.hs8.str[:2]
    p.to_csv(f"results/s301_pairs_{tag.replace(', ', '_')}.csv", index=False)
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
ad.to_csv("results/s301_adcvd_pairs_h16.csv", index=False)
pd.DataFrame(res).to_csv("results/s301_benchmark.csv", index=False)
info.to_csv("results/s301_stacks_info.csv", index=False)
print("wrote results/s301_benchmark.csv, results/s301_pairs_{real,placebo,real_strict}.csv, results/s301_adcvd_pairs_h16.csv, "
      "results/s301_stacks_info.csv, panel/s301_stacks.parquet")
