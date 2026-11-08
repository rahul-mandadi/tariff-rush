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
    sh = (tg.reindex(tot.index).fillna(0.0) / tot).where(tot > 0).rename("share").reset_index()
    out = []
    for (s, h), g in sh.groupby(["sid", "hs8"]):
        g = g.set_index("k").share.sort_index()
        # put the path on calendar months: a month with no trade from any country in the panel
        # has no defined share, so it is missing, and the 3-month average needs 3 real months
        g = g.reindex(range(int(g.index.min()), int(g.index.max()) + 1))
        bench = g.loc[-18:-13].mean()
        if not np.isfinite(bench) or bench <= 0:
            continue
        sm = g.rolling(3, min_periods=3).mean()
        post = sm.loc[0:H]
        if not post.loc[0:6].notna().any():  # no comparison trade in months 0..6: fall not measurable
            continue
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
    p = pd.DataFrame(out, columns=["sid", "hs8", "bench", "fell_at", "rec_at", "follow"])
    if p.empty:
        return p.assign(traded_late=pd.Series(dtype=bool), category=pd.Series(dtype=str))
    late = (d[d.treated & d.k.between(H - 5, H)].groupby(["sid", "hs8"]).value.sum() > 0)
    p["traded_late"] = [late.get((s, h), False) for s, h in zip(p.sid, p.hs8)]
    p["category"] = np.select([p.fell_at.isna(), p.rec_at.notna(), p.traded_late],
                              ["no fall", "recovered", "not recovered"], "exited")
    p.loc[p.follow < H, "category"] = "censored"
    return p


def share_paths(d):
    tot = d.groupby(["sid", "hs8", "k"]).value.sum()
    tg = d[d.treated].groupby(["sid", "hs8", "k"]).value.sum()
    share = (tg.reindex(tot.index).fillna(0.0) / tot).where(tot > 0)
    tv = d[d.treated].set_index(["sid", "hs8", "k"]).value
    paths = {}
    for (s, h), g in share.groupby(level=[0, 1]):
        g = g.droplevel([0, 1]).sort_index()
        g = g.reindex(range(int(g.index.min()), int(g.index.max()) + 1))  # calendar months, gaps missing
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
    if g.unit.nunique() > 1:
        return np.nan
    g = g[g.qty_ok.fillna(False).astype(bool) & (g.qty > 0)]
    pre, post = g[g.m <= b0 - 7], g[g.m >= b0]

    def luv(x):
        return np.log(x.value.sum() / x.qty.sum()) if len(x) and x.qty.sum() > 0 else np.nan
    return (luv(post[post.cty == tc]) - luv(pre[pre.cty == tc])) - (luv(post[post.cty != tc]) - luv(pre[pre.cty != tc]))


def one_unit_qty(q):
    """Rows by product; uv_change decides one-unit eligibility inside each visible window."""
    return {h: g[["cty", "m", "value", "qty", "unit", "qty_ok"]] for h, g in q.groupby("hs8")}


def fall_features(path, bench, fell_at, uvc):
    sh, sm, v = path
    kv = int(fell_at)
    post = sm.loc[0:kv]
    vv = v.reindex(range(0, kv + 1), fill_value=0)
    return dict(k_fall=float(fell_at), depth=float(post.min() / bench),
                latest=float(post.dropna().iloc[-1] / bench),
                zero_months=float((vv == 0).mean()), rush=float(sh.loc[-6:-1].mean() / bench),
                uv_change=0.0 if pd.isna(uvc) else float(np.clip(uvc, -3, 3)), uv_missing=float(pd.isna(uvc)))


def final_stage(ep):
    """Each episode's final stage (order / negative / unresolved) and the date it became public:
    the first harvested order notice after the first preliminary for cases linked to an order, the
    ITC's negative determination notice for verified negatives. The same rule as
    prediction_stage2.py, which keeps its own copy so its committed results stay byte-identical."""
    import json
    import re
    ev = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str}).drop_duplicates("document_number")
    pubd = pd.to_datetime(ev.set_index("document_number").publication_date)
    case = re.compile(r"\b([AC])-(\d{3})-(\d{3})\b")
    allc = {d: {"-".join(m) for m in case.findall(open(f"events/raw/{d}.txt", errors="ignore").read())}
            for d in ev.document_number}
    orders = ev[ev.stage == "order"].document_number.tolist()
    order_cases = set().union(*[allc[d] for d in orders])
    pub_itc = {}
    for f in glob.glob("events/raw/itc_cache/*"):
        try:
            js = json.loads(open(f).read())
        except Exception:
            continue
        for r in (js.get("results", []) if isinstance(js, dict) else []):
            if r.get("document_number") and r.get("publication_date"):
                pub_itc[r["document_number"]] = pd.Timestamp(r["publication_date"])
    pc = pd.read_csv("events/itc_check_by_country.csv", dtype={"cty": str})
    key = {(r.ini, r.cty): r.verdict for r in pc.itertuples()}
    fam_of = {(r.ini, r.cty): r.family for r in pc.itertuples()}
    grp = pd.read_csv("events/itc_check.csv")
    grp_ev = {(r.family, r.ini): str(r.evidence).split(";")[0] for r in grp.itertuples()}
    neg_doc = pd.read_csv("events/itc_negative_audit.csv").set_index("sid").itc_doc
    first = [min(pubd[d] for d in ds.split(";")) for ds in ep.docs]
    out = []
    for s, (ds, b, f0) in enumerate(zip(ep.docs, ep.b, first)):
        own = set().union(*[allc.get(d, set()) for d in ds.split(";")])
        od = [pubd[o] for o in orders if allc[o] & own and pubd[o] > f0]
        if own & order_cases:
            st, dt = "order", (min(od) if od else None)
        else:
            v = key.get((ep.ini[s], ep.cty[s]))
            st = {"verified negative": "negative", "verified order": "order"}.get(v, "unresolved")
            dt = None
            if st == "negative" and s in neg_doc.index:
                dt = pub_itc.get(neg_doc[s])
            if st == "order":
                dt = pub_itc.get(grp_ev.get((fam_of.get((ep.ini[s], ep.cty[s])), ep.ini[s])))
        out.append(dict(stage=st, d_final=dt, k_final=month(dt) - b if dt is not None else np.nan,
                        first=f0))
    return pd.DataFrame(out, index=ep.index)


def both_programs_known(ep):
    """True if both an antidumping and a countervailing investigation of the episode's country were
    public by the episode's first preliminary: an initiation notice (same country, initiation month
    within one month of the episode's, naming at least one of the episode's products) or one of the
    episode's own preliminaries whose investigation was initiated on or before first_date. The old
    flag ("ad and cvd" over every notice in the episode) read companion preliminaries published after
    the decision; every one of those companions had been initiated by then, so all old positives
    stay, and 51 episodes are added whose companion investigation existed but whose preliminary was
    negative or did not join the episode. For 8 episodes the companion's initiation is known only
    from its later preliminary (the harvest lacks the initiation notice); the fact was public at
    first_date, but its detection relies on the later document."""
    e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
    e["date"] = pd.to_datetime(e.publication_date)
    e["prog"] = e.case.fillna("").str[:1]
    e["m"] = e.date.dt.year * 12 + e.date.dt.month - 1
    ini = e[e.stage == "initiation"]
    prods = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
    prods = {d: set(g.hs8) for d, g in prods.groupby("document_number")}
    pre = e[e.stage == "preliminary"].set_index("document_number")
    out = {}
    for s, r in ep.iterrows():
        fd = pd.Timestamp(r.first_date)
        P = set(str(r.P).split(";"))
        i = ini[(ini.cty == str(r.cty)) & ((ini.m - int(r.ini)).abs() <= 1) & (ini.date <= fd)]
        i = i.loc[np.array([bool(prods.get(d, set()) & P) for d in i.document_number], dtype=bool)]
        progs = set(i.prog)
        own = pre.loc[pre.index.isin(str(r.docs).split(";"))]
        # a companion investigation was public once it was initiated, even if its preliminary came later
        opened = pd.to_datetime(own.initiation_date, errors="coerce")
        progs |= set(own[(own.date <= fd) | (opened <= fd)].prog)
        out[s] = {"A", "C"} <= progs
    return pd.Series(out)
