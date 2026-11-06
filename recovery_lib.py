"""Shared pieces for the recovery outcomes and the at-the-fall features, so AD/CVD cases and the
Section 301 lists go through exactly the same rules.

categorize()   per targeted product: pre-case share, month of the fall, month of recovery, and the
               four outcome categories, for any horizon H (recovery_benchmark.py uses H = 18).
               Run on panel/adcvd_stacks_real.parquet with H = 18 it reproduces
               recovery_pairs_real_fall20.csv (checked in sec301_benchmark.py).
build_stack()  a stack in the format of adcvd_stacked.py for one targeted country and a product list
fall_features() what the published data show when the fall first becomes visible (k_fall + 2),
               the same definitions as prediction_stage2.py
"""
import glob

import numpy as np
import pandas as pd

FALL, LAG = 0.2, 2


def month(t):
    return t.year * 12 + t.month - 1


def load_raw(hs8s, m_lo, m_hi, qty=False):
    cols = ["hs8", "cty", "ym", "value"] + (["qty", "unit", "qty_ok"] if qty else [])
    out = []
    for f in sorted(glob.glob("panel/hs8/*.parquet")):
        y, mo = map(int, f.split("/")[-1][:7].split("-"))
        if not (m_lo <= y * 12 + mo - 1 <= m_hi):
            continue
        x = pd.read_parquet(f, columns=cols)
        out.append(x[x.hs8.isin(hs8s) & (x.value > 0)])
    r = pd.concat(out)
    r["m"] = r.ym.dt.year * 12 + r.ym.dt.month - 1
    return r.drop(columns="ym")


def build_stack(raw, products, target, b, m_cap, excl=None, k_lo=-18, k_hi=18):
    """Targeted country plus every rival trading the product in k -18..-7, months k_lo..k_hi up to
    m_cap, zeros kept, product-months with no trade among them dropped. excl maps hs8 to rival
    countries left out (named on that product by another case nearby)."""
    excl = excl or {}
    g = raw[raw.hs8.isin(products) & raw.m.between(b + k_lo, min(b + k_hi, m_cap))]
    pre = g[g.m.between(b - 18, b - 7)]
    cohort = pre[["hs8", "cty"]].drop_duplicates()
    cohort = cohort[[c == target or c not in excl.get(h, set()) for h, c in zip(cohort.hs8, cohort.cty)]]
    # the targeted country must be in the cohort for the product to count
    keep = set(cohort[cohort.cty == target].hs8)
    cohort = cohort[cohort.hs8.isin(keep)]
    months = np.arange(b + k_lo, min(b + k_hi, m_cap) + 1)
    full = cohort.merge(pd.DataFrame({"m": months}), how="cross")
    v = g.groupby(["hs8", "cty", "m"]).value.sum()
    full["value"] = v.reindex(pd.MultiIndex.from_frame(full[["hs8", "cty", "m"]])).fillna(0).to_numpy()
    tot = full.groupby(["hs8", "m"]).value.transform("sum")
    full = full[tot > 0].copy()
    full["k"] = full.m - b
    full["treated"] = full.cty == target
    return full


def categorize(d, H, b_of, last_m, fall=FALL):
    """Per (sid, hs8): pre-case share, fall month, recovery month and outcome category by k = H.
    d needs sid, hs8, k, m, value, treated. Late window for "exited" is the last six months."""
    tot = d.groupby(["sid", "hs8", "k"]).value.sum()
    tg = d[d.treated].groupby(["sid", "hs8", "k"]).value.sum()
    sh = (tg / tot).fillna(0.0).rename("share").reset_index()
    out = []
    for (s, h), g in sh.groupby(["sid", "hs8"]):
        g = g.set_index("k").share.sort_index()
        bench = g.loc[-18:-13].mean()
        if not np.isfinite(bench) or bench <= 0:
            continue
        sm = g.rolling(3, min_periods=3).mean()
        post = sm.loc[0:H]
        follow = min(H, int(last_m - b_of[s]))
        fell_at = next((k for k in range(0, 7) if k in post.index and post[k] < (1 - fall) * bench), None)
        rec_at = None
        if fell_at is not None:
            above = (post >= bench).reindex(range(fell_at, follow + 1), fill_value=False)
            run = 0
            for k, a in above.items():
                run = run + 1 if a else 0
                if run == 3:
                    rec_at = k - 2
                    break
        out.append(dict(sid=s, hs8=h, bench=bench, fell_at=fell_at, rec_at=rec_at, follow=follow))
    p = pd.DataFrame(out)
    late = (d[d.treated & d.k.between(H - 5, H)].groupby(["sid", "hs8"]).value.sum() > 0)
    p["traded_late"] = [late.get((s, h), False) for s, h in zip(p.sid, p.hs8)]
    p["category"] = np.select([p.fell_at.isna(), p.rec_at.notna(), p.traded_late],
                              ["no fall", "recovered", "not recovered"], "exited")
    p.loc[p.follow < H, "category"] = "censored"
    return p


def share_paths(d):
    tot = d.groupby(["sid", "hs8", "k"]).value.sum()
    tg = d[d.treated].groupby(["sid", "hs8", "k"]).value.sum()
    share = (tg / tot).fillna(0.0)
    tv = d[d.treated].set_index(["sid", "hs8", "k"]).value
    paths = {}
    for (s, h), g in share.groupby(level=[0, 1]):
        g = g.droplevel([0, 1]).sort_index()
        paths[(s, h)] = (g, g.rolling(3, min_periods=3).mean(), tv.loc[(s, h)].sort_index())
    return paths


def pre_features(raw, h, b0, tc):
    g = raw[(raw.hs8 == h) & raw.m.between(b0 - 18, b0 - 7)] if not isinstance(raw, dict) else raw.get(h)
    if isinstance(raw, dict) and g is not None:
        g = g[g.m.between(b0 - 18, b0 - 7)]
    if g is None or g.empty:
        return None
    cs = g.groupby("cty").value.sum()
    csh = cs / cs.sum()
    mm = g.groupby("m").value.sum()
    shm = g[g.cty == tc].groupby("m").value.sum().reindex(mm.index, fill_value=0) / mm
    x = (shm.index - b0).to_numpy(float)
    return dict(pre_share=float(csh.get(tc, 0.0)),
                pre_trend=float(np.polyfit(x, shm.to_numpy(float), 1)[0]) if len(x) > 2 else 0.0,
                log_pre_value=float(np.log1p(cs.get(tc, 0.0))),
                hhi=float((csh ** 2).sum()), n_rivals=float(np.log(max(len(cs) - 1, 1))))


def uv_change(uvq, h, b0, tc, kv):
    g = uvq.get(h)
    if g is None:
        return np.nan
    g = g[(g.m >= b0 - 18) & (g.m <= b0 + kv)]
    pre, post = g[g.m <= b0 - 7], g[g.m >= b0]

    def luv(x):
        return np.log(x.value.sum() / x.qty.sum()) if len(x) and x.qty.sum() > 0 else np.nan
    return (luv(post[post.cty == tc]) - luv(pre[pre.cty == tc])) - (luv(post[post.cty != tc]) - luv(pre[pre.cty != tc]))


def one_unit_qty(q):
    one = q.groupby("hs8").unit.nunique()
    ok = q[q.hs8.isin(one[one == 1].index) & q.qty_ok.fillna(False).astype(bool) & (q.qty > 0)]
    return {h: g[["cty", "m", "value", "qty"]] for h, g in ok.groupby("hs8")}


def fall_features(path, bench, fell_at, uvc):
    sh, sm, v = path
    kv = int(fell_at)
    post = sm.loc[0:kv]
    vv = v.reindex(range(0, kv + 1), fill_value=0)
    return dict(k_fall=float(fell_at), depth=float(post.min() / bench), latest=float(post.iloc[-1] / bench),
                zero_months=float((vv == 0).mean()), rush=float(sh.loc[-6:-1].mean() / bench),
                uv_change=0.0 if pd.isna(uvc) else float(np.clip(uvc, -3, 3)), uv_missing=float(pd.isna(uvc)))
