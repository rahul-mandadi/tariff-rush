"""AD/CVD aftermath on a fixed cohort that keeps zero-trade months: a stacked event study.

adcvd_event_study.py pools every cell-month into one regression. Its treated cohort changes with
event time (975 cells at k = 0, 1,437 at k = 18), product-country pairs that stop trading leave
the panel, months outside any window act as reference alongside the baseline, and companion
notices for one case claim the same months and get dropped. adcvd_cohort_check.py showed the
headline fall is sensitive to all of that. This script rebuilds the estimate so none of it
applies.

Design
  episode     notices for one targeted country, initiated in the same month, with overlapping
              products (companion AD and CVD notices) collapse to one episode, dated at the
              first preliminary determination, k = 0.
  notices     only affirmative preliminary determinations. EXCLUDE lists 21 notices that are
              negative, critical-circumstances-only, or administrative-review / no-shipment
              notices, each read from its own summary (review of 2026-11-06).
  stack       one per episode: the episode's products, the targeted country, and every rival
              country trading those products before the case, over k = -18 to +18.
  cohort      fixed from pre-case information only. A product-country pair is in the stack if
              it traded at least once in k = -18 to -7 and before the case's initiation month.
              It stays in for every later month whether or not it trades.
  zeros       a month with no reported trade is zero. A product-month with no imports from any
              country is dropped (the code was not in use). Months past the data end are not
              observed and are not filled.
  controls    rivals that are themselves named on that product by an episode with k = 0 within
              36 months before to 18 months after are dropped from the stack.
  estimators  PPML on value (zeros included; the coefficient is a proportional change in the
              targeted country's expected imports against rivals of the same product and month),
              a linear probability model on whether the pair trades at all, and OLS on log value
              among positive months (the original outcome, for comparison only).
              Fixed effects: stack x product x month and stack x product x country.
              Event-time indicators for the targeted country, k = -12 to 18; k = -18 to -13 is
              the reference. Standard errors clustered on investigation groups (episodes sharing
              an initiation month and products, i.e. one petition across countries).
  placebo     the same stacks with k = 0 moved 24 months earlier.

Usage:  python3 adcvd_stacked.py
"""
import glob

import sys

import numpy as np
import pandas as pd
import scipy.sparse as sp

K_LO, K_HI, BASE = -18, 18, (-18, -13)
SHIFT = 24
EXCLUDE = {
    # negative preliminary determinations: no duty
    "2016-19867", "2018-23719", "2019-10283", "2021-10918",
    # critical-circumstances-only notices, separate from the case's own preliminary
    "2015-28252", "2015-31083", "2016-15132", "2016-21501", "2017-08469", "2020-02696",
    "2020-24135", "2023-15392", "2025-14337",
    # administrative reviews / no-shipment findings on orders that already existed
    "2017-24186", "2019-12726", "2019-27030", "2019-27937", "2021-24227", "2022-08347",
    "2023-03300", "2024-20773",
}


def mi(ts):
    """Month index."""
    ts = pd.to_datetime(ts)
    return ts.dt.year * 12 + ts.dt.month - 1 if hasattr(ts, "dt") else ts.year * 12 + ts.month - 1


# ---------------------------------------------------------------- events -> episodes
e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
p = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in p.groupby("document_number")}
e = e[(e.stage == "preliminary") & e.window_days.notna() & (e.window_days >= 60)]
e = e[e.document_number.isin(prods) & ~e.document_number.isin(EXCLUDE)].copy()
e["b"] = mi(e.publication_date)
e["date"] = pd.to_datetime(e.publication_date)
e["ini"] = mi(e.initiation_date)
e["prog"] = e.case.fillna("").str[:1]

files = sorted(glob.glob("panel/hs8/*.parquet"))
raw = pd.concat([pd.read_parquet(f, columns=["hs8", "cty", "ym", "value"]) for f in files])
raw = raw[raw.value > 0]
raw["m"] = mi(raw.ym)
M_FIRST, M_LAST = int(raw.m.min()), int(raw.m.max())
in_panel = set(raw.hs8.unique())
e["P"] = e.document_number.map(lambda d: frozenset(prods[d] & in_panel))
e = e[e.P.map(len) > 0]


def union_find(keys, overlap):
    parent = list(range(len(keys)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            if overlap(i, j):
                parent[find(i)] = find(j)
    return [find(i) for i in range(len(keys))]


# companion notices: same country, same initiation month, overlapping products
eps = []
for (cty, ini), g in e.groupby(["cty", "ini"]):
    g = g.reset_index(drop=True)
    root = union_find(range(len(g)), lambda i, j: bool(g.P[i] & g.P[j]))
    for r in set(root):
        h = g[[x == r for x in root]]
        first = h.date.min()
        eps.append(dict(cty=cty, ini=int(ini), b=int(h.b.min()),
                        P=frozenset().union(*h.P), docs=";".join(h.document_number),
                        first_date=first, P0=frozenset().union(*h[h.date <= first].P),
                        ad="A" in set(h.prog), cvd="C" in set(h.prog)))
ep = pd.DataFrame(eps)
# one petition across countries: same initiation month, overlapping products
root = union_find(range(len(ep)), lambda i, j: ep.ini[i] == ep.ini[j] and bool(ep.P[i] & ep.P[j]))
ep["cluster"] = pd.factorize(pd.Series(root))[0]
ep["k_ini"] = ep.ini - ep.b
print(f"notices kept {len(e)}, excluded {len(EXCLUDE)}; episodes {len(ep)}; "
      f"investigation groups {ep.cluster.nunique()}")
print(f"episodes with both AD and CVD: {(ep.ad & ep.cvd).sum()}")
print(f"initiation month relative to k = 0: median {ep.k_ini.median():.0f}, "
      f"min {ep.k_ini.min()}, max {ep.k_ini.max()}")
print(f"episodes initiated at or before k = -13 (reference window not wholly pre-case): "
      f"{(ep.k_ini <= -13).sum()}")
print(f"episodes whose initiation falls at or before k = -7, so the -12..-7 benchmark is not "
      f"wholly pre-case: {(ep.k_ini <= -7).sum()}")

# (product, country) -> months at which an episode starts, for clean controls
named, named_date = {}, {}
for _, r in ep.iterrows():
    for h in r.P:
        named.setdefault((h, r.cty), []).append(r.b)
        named_date.setdefault((h, r.cty), []).append((r.b, r.first_date))

# ---------------------------------------------------------------- stacks
allP = set().union(*ep.P)
sub = raw[raw.hs8.isin(allP)]
by_h = {h: g[["cty", "m", "value"]] for h, g in sub.groupby("hs8")}
pm_tot = sub.groupby(["hs8", "m"]).value.sum()
pm_live = set(pm_tot[pm_tot > 0].index)


def build(shift, excl_hi=18, decision=False):
    """excl_hi: rivals named on the product by another episode with k = 0 up to this many months
    after this one are left out; 18 for the measurement, where hindsight is allowed.
    decision=True (build_decision_stacks.py, real dates only): what a forecaster knew on the day of
    the episode's first preliminary. Rivals are left out only if their own first preliminary was
    published on or before that date (exact dates, not months), and the products are only those
    named in notices published by that date, not ones a later companion notice adds."""
    assert not (decision and shift), "decision-time panels are for real dates only"
    out = []
    for s, r in ep.iterrows():
        b = r.b - shift
        lo, hi = b + K_LO, min(b + K_HI, M_LAST)
        if lo < M_FIRST:
            continue
        elig_hi = min(b - 7, r.ini - shift - 1)     # strictly before the case's initiation
        for h in (r.P0 if decision else r.P):
            g = by_h[h]
            g = g[(g.m >= lo) & (g.m <= hi)]
            pre = g[(g.m >= lo) & (g.m <= elig_hi)]
            ctys = set(pre.cty)
            if r.cty not in ctys:
                continue
            if decision:
                bad = {c for c in ctys if c != r.cty and any(
                    b - 36 <= bb and fd <= r.first_date for bb, fd in named_date.get((h, c), []))}
            else:
                bad = {c for c in ctys if c != r.cty and any(
                    b - 36 <= bb - shift <= b + excl_hi for bb in named.get((h, c), []))}
            ctys -= bad
            if len(ctys) < 2:
                continue
            months = [m for m in range(lo, hi + 1) if (h, m) in pm_live]
            grid = pd.MultiIndex.from_product([sorted(ctys), months], names=["cty", "m"])
            v = g.groupby(["cty", "m"]).value.sum().reindex(grid, fill_value=0)
            d = v.reset_index()
            d["hs8"], d["sid"], d["cluster"] = h, s, r.cluster
            d["treated"] = (d.cty == r.cty)
            d["k"] = d.m - b
            out.append(d)
    return pd.concat(out, ignore_index=True)


# ---------------------------------------------------------------- estimators
def demean(cols, w, groups, tol=1e-8, it=2000):
    """Weighted alternating projections onto two sets of fixed effects."""
    out = cols.copy()
    A = [sp.csr_matrix((np.ones(len(g)), (np.arange(len(g)), g))) for g in groups]
    sw = [np.bincount(g, weights=w) for g in groups]
    for _ in range(it):
        prev = out.copy()
        for a, s in zip(A, sw):
            out -= a @ ((a.T @ (w[:, None] * out)) / s[:, None])
        if np.max(np.abs(out - prev)) < tol:
            break
    return out


def drop_singleton_zero(d, y):
    """Drop fixed-effect groups whose outcome is all zero (PPML separation), to a fixed point."""
    keep = np.ones(len(d), bool)
    while True:
        n = keep.sum()
        for cols in (["sid", "hs8", "m"], ["sid", "hs8", "cty"]):
            s = pd.Series(y[keep]).groupby([d[c].to_numpy()[keep] for c in cols]).transform("sum")
            idx = np.flatnonzero(keep)
            keep[idx[(s.to_numpy() == 0)]] = False
        if keep.sum() == n:
            return keep


def design(d, ks):
    X = np.column_stack([(d.treated.to_numpy() & (d.k.to_numpy() == k)).astype(float) for k in ks])
    g1 = d.groupby(["sid", "hs8", "m"], sort=False).ngroup().to_numpy()
    g2 = d.groupby(["sid", "hs8", "cty"], sort=False).ngroup().to_numpy()
    return X, [g1, g2]


def cluster_vcov(Xt, u, w, cl):
    B = np.linalg.inv((Xt * w[:, None]).T @ Xt)
    S = np.zeros((Xt.shape[1],) * 2)
    order = np.argsort(cl, kind="stable")
    for i in np.split(order, np.flatnonzero(np.diff(cl[order])) + 1):
        sg = Xt[i].T @ u[i]
        S += np.outer(sg, sg)
    G = len(np.unique(cl))
    return G / (G - 1) * B @ S @ B


def ols(d, y, ks):
    X, gs = design(d, ks)
    w = np.ones(len(y))
    Xt = demean(X, w, gs)
    yt = demean(y[:, None], w, gs)[:, 0]
    beta = np.linalg.lstsq(Xt, yt, rcond=None)[0]
    return beta, cluster_vcov(Xt, yt - Xt @ beta, w, d.cluster.to_numpy())


def ppml(d, y, ks, tol=1e-8, it=100):
    keep = drop_singleton_zero(d, y)
    d, y = d[keep].reset_index(drop=True), y[keep]
    X, gs = design(d, ks)
    mu = (y + y.mean()) / 2
    eta = np.log(mu)
    dev_old = np.inf
    zt_prev = None
    for _ in range(it):
        z = eta + (y - mu) / mu
        Xt = demean(X, mu, gs)
        zt = demean(z[:, None], mu, gs)[:, 0]
        beta = np.linalg.lstsq(Xt * np.sqrt(mu)[:, None], zt * np.sqrt(mu), rcond=None)[0]
        eta = z - (zt - Xt @ beta)
        mu = np.exp(eta)
        dev = 2 * np.sum(np.where(y > 0, y * np.log(np.where(y > 0, y, 1) / mu), 0) - (y - mu))
        if abs(dev - dev_old) / max(1.0, abs(dev)) < tol:
            break
        dev_old = dev
    Xt = demean(X, mu, gs)
    # score of the Poisson likelihood: x~ (y - mu); bread uses weights mu
    V = cluster_vcov(Xt, y - mu, mu, d.cluster.to_numpy())
    return beta, V, len(d)


KS = [k for k in range(K_LO, K_HI + 1) if not (BASE[0] <= k <= BASE[1])]


def contrast(beta, V, a, b):
    """Mean of coefficients over window b minus mean over window a, with its standard error."""
    c = np.array([(0 if a is None else (1 / (a[1] - a[0] + 1)) * -(a[0] <= k <= a[1])) +
                  (1 / (b[1] - b[0] + 1)) * (b[0] <= k <= b[1]) for k in KS], float)
    return c @ beta, float(np.sqrt(c @ V @ c))


WINDOWS = {"after (0..18) vs reference (-18..-13)": (None, (0, 18)),
           "months 13..18 vs reference (-18..-13)": (None, (13, 18)),
           "pre-case (-12..-7) vs reference (-18..-13)": (None, (-12, -7)),
           "petition (-6..-1) vs pre-case (-12..-7)": ((-12, -7), (-6, -1)),
           "after (0..18) vs pre-case (-12..-7)": ((-12, -7), (0, 18)),
           "months 13..18 vs pre-case (-12..-7)": ((-12, -7), (13, 18)),
           "after (0..18) vs old 'before' (-12..-4)": ((-12, -4), (0, 18))}


def report(d, label, rows, paths):
    print(f"\n[{label}] rows {len(d):,}  stacks {d.sid.nunique()}  "
          f"targeted pairs {d[d.treated][['sid','hs8']].drop_duplicates().shape[0]:,}  "
          f"clusters {d.cluster.nunique()}  share of rows zero {(d.value == 0).mean():.2f}")
    yv = d.value.to_numpy(float)
    res = {}
    b, V, n = ppml(d, yv, KS)
    res["PPML value, zeros in"] = (b, V, n)
    b, V = ols(d, (yv > 0).astype(float), KS)
    res["trades at all (LPM)"] = (b, V, len(d))
    pos = d[d.value > 0].reset_index(drop=True)
    b, V = ols(pos, np.log(pos.value.to_numpy(float)), KS)
    res["log value, positive only"] = (b, V, len(pos))
    for name, (b, V, n) in res.items():
        se = np.sqrt(np.diag(V))
        paths.append(pd.DataFrame({"k": KS, "coef": b, "se": se, "outcome": name, "sample": label}))
        for wname, (a, bb) in WINDOWS.items():
            est, s = contrast(b, V, a, bb)
            rows.append(dict(sample=label, outcome=name, contrast=wname, est=est, se=s, n=n))
            print(f"  {name:<26} {wname:<42} {est:+.3f} ({s:.3f})")


def transitions(d, label):
    """Trading status of each targeted or rival pair, by period, among pairs trading pre-case."""
    t = d.assign(on=d.value > 0)
    per = lambda lo, hi: t[t.k.between(lo, hi)].groupby(["sid", "hs8", "cty"]).on.any()
    base = per(-12, -7)
    a, b, c = per(0, 6), per(7, 12), per(13, 18)
    f = pd.DataFrame({"base": base, "a": a, "b": b, "c": c}).dropna().reset_index()
    f = f[f.base.astype(bool)]
    f["treated"] = f.cty == f.sid.map(ep.cty)
    out = []
    for tr, g in f.groupby("treated"):
        g = g[["a", "b", "c"]].astype(bool)
        out.append(dict(sample=label, group="targeted" if tr else "rivals", pairs=len(g),
                        inactive_13_18=(~g.c).mean(),
                        active_0_6_then_inactive_13_18=(g.a & ~g.c).mean(),
                        inactive_0_6_then_active_13_18=(~g.a & g.c).mean(),
                        inactive_all_0_18=(~g.a & ~g.b & ~g.c).mean()))
    return out


def validate():
    """PPML here against statsmodels' Poisson GLM with explicit dummies, on three stacks."""
    import statsmodels.api as sm
    real = build(0)
    st = sorted(real.sid.unique())[:3]
    d = real[real.sid.isin(st)].reset_index(drop=True)
    y = d.value.to_numpy(float)
    keep = drop_singleton_zero(d, y)
    d, y = d[keep].reset_index(drop=True), y[keep]
    b, V, n = ppml(d, y, KS)
    X, gs = design(d, KS)
    live = X.any(0)
    D = pd.get_dummies(pd.DataFrame({"a": gs[0].astype(str), "b": gs[1].astype(str)}),
                       drop_first=True).astype(float).to_numpy()
    Z = np.column_stack([np.ones(len(y)), X[:, live], D])
    g = sm.GLM(y / y.mean(), Z, family=sm.families.Poisson()).fit()
    ref = g.params[1:1 + live.sum()]
    print(f"rows {len(y)}, max |difference| in event coefficients: "
          f"{np.max(np.abs(b[live] - ref)):.2e}")


if __name__ == "__main__" and "--validate" in sys.argv:
    validate()
elif __name__ == "__main__":
    rows, paths, trans = [], [], []
    real = build(0)
    plac = build(SHIFT)
    full = lambda d: d[d.sid.map(lambda s: ep.b[s] + K_HI <= M_LAST)]
    # episodes that have a complete real window and a placebo window inside the data
    both = set(full(real).sid) & set(plac.sid)
    real_full = full(real)
    real_full = real_full.reset_index(drop=True)
    print(f"\nepisodes with complete 18-month follow-up: {real_full.sid.nunique()}; "
          f"of those with a placebo window too: {len(both)}")
    report(real_full, "real, complete follow-up", rows, paths)
    report(real_full[real_full.sid.isin(both)].reset_index(drop=True),
           "real, placebo-matched", rows, paths)
    pl = plac[plac.sid.isin(both)].reset_index(drop=True)
    report(pl, "placebo, 24 months earlier", rows, paths)
    pre_ok = real_full[real_full.sid.map(lambda s: ep.k_ini[s] > -7)].reset_index(drop=True)
    report(pre_ok, "real, benchmark wholly before initiation", rows, paths)

    trans += transitions(real_full, "real, complete follow-up")
    trans += transitions(pl, "placebo, 24 months earlier")
    T = pd.DataFrame(trans)
    print("\ntrading status among pairs that traded in the pre-case window (k -12..-7)")
    print(T.round(3).to_string(index=False))

    pd.DataFrame(rows).to_csv("adcvd_stacked.csv", index=False)
    pd.concat(paths).to_csv("adcvd_stacked_paths.csv", index=False)
    T.to_csv("adcvd_stacked_transitions.csv", index=False)
    ep.assign(P=ep.P.map(lambda s: ";".join(sorted(s)))).to_csv("adcvd_episodes_collapsed.csv",
                                                                index=False)
    real.to_parquet("panel/adcvd_stacks_real.parquet")
    plac.to_parquet("panel/adcvd_stacks_placebo.parquet")
    print("\nwrote adcvd_stacked.csv, adcvd_stacked_paths.csv, adcvd_stacked_transitions.csv, "
          "adcvd_episodes_collapsed.csv, panel/adcvd_stacks_*.parquet")
