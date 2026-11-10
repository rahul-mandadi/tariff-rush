"""Does the AD/CVD aftermath survive on a fixed set of cases?

The monthly event study (adcvd_event_study.py) is not a balanced cohort: different cells sit
behind different months (975 treated cell-months at k = 0, 1,437 at k = 18). If the cases seen at
month 18 are not the cases seen at month 0, the "no bounce back" path could be a change in who is
measured rather than a change in what happened to them.

Same estimator, same fixed effects, same overlap rule, same placebo. Only the set of treated
cell-months changes. Treated rows outside the chosen set are dropped (not turned into controls),
so no treated observation leaks into the comparison group.

  all       the published estimate, reproduced
  calendar  events whose full window (k -18 to 18, real and placebo) lies inside the panel, so no
            case is cut off by the start or end of the data. Selects on dates only.
  present   event-cells with trade in at least one baseline month and in every month k -12 to 18.
            Selects on the outcome: a cell that stopped trading is excluded, which leans toward
            finding a recovery, so a fall that survives here is conservative.
  both      calendar and present together

Also reports the exit side the regressions cannot see, since the panel holds positive trade only:
of the event-cells trading in the baseline, the share still trading at each horizon, real against
placebo.

Usage:  python3 adcvd_cohort_check.py
"""
import numpy as np
import pandas as pd

MIN_W = 60
K_LO, K_HI, BASE = -18, 18, (-18, -13)
SHIFT = 24

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "ym", "lv"])
df["ym"] = pd.to_datetime(df.ym)
FIRST, LAST = df.ym.min(), df.ym.max()

e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
p = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in p.groupby("document_number")}
e = e[(e.stage == "preliminary") & e.window_days.notna() & (e.window_days >= MIN_W)]
e = e[e.document_number.isin(prods)].copy()
e["b"] = pd.to_datetime(e.publication_date).dt.to_period("M").dt.to_timestamp()

masks = []
for _, r in e.iterrows():
    m = (df.cty.values == r.cty) & df.hs8.isin(prods[r.document_number]).values
    if m.any():
        masks.append((m, r.b))
print(f"events hitting the panel: {len(masks)}")

# a window [b-18-shift, b+18-shift] must sit inside the panel for both real and placebo
lo_ok = FIRST + pd.DateOffset(months=-K_LO + SHIFT)
hi_ok = LAST - pd.DateOffset(months=K_HI)
in_cal = np.array([lo_ok <= b <= hi_ok for _, b in masks])
print(f"events with a complete real and placebo window: {in_cal.sum()} "
      f"(preliminary {lo_ok:%Y-%m} to {hi_ok:%Y-%m})")

yr, mo = df.ym.dt.year.to_numpy(), df.ym.dt.month.to_numpy()
hs8_code = pd.factorize(df.hs8)[0]


def assign(shift):
    """Event time, number of claiming events, and the claiming event, per row."""
    K = np.full(len(df), 99, dtype=int)
    E = np.full(len(df), -1, dtype=int)
    hits = np.zeros(len(df), dtype=int)
    for j, (m, b) in enumerate(masks):
        bb = b - pd.DateOffset(months=shift)
        k = (yr - bb.year) * 12 + (mo - bb.month)
        inwin = m & (k >= K_LO) & (k <= K_HI)
        hits += inwin
        sel = inwin & (K == 99)
        K[sel], E[sel] = k[sel], j
    return K, E, hits


def present_cells(K, E, treated):
    """Event-cells (event, product) trading in some baseline month and every month -12..18."""
    t = pd.DataFrame({"E": E[treated], "h": hs8_code[treated], "k": K[treated]})
    base = t[t.k.between(*BASE)].groupby(["E", "h"]).size()
    post = t[t.k.between(-12, K_HI)].groupby(["E", "h"]).k.nunique()
    full = post[post == K_HI - (-12) + 1].index
    return set(full.intersection(base.index))


def dm(v, g):
    return v - (np.bincount(g, weights=v) / np.bincount(g))[g]


def estimate(keep, K):
    d = df[keep]
    Kk = K[keep]
    ks = [k for k in range(-12, K_HI + 1)]
    X = np.column_stack([(Kk == k).astype(float) for k in ks])
    y = d.lv.to_numpy(float)
    g1 = d.groupby(["hs8", "ym"], sort=False).ngroup().to_numpy()
    g2 = d.groupby(["hs8", "cty"], sort=False).ngroup().to_numpy()
    for _ in range(25):
        y = dm(dm(y, g1), g2)
        for j in range(X.shape[1]):
            X[:, j] = dm(dm(X[:, j], g1), g2)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    XtX = np.linalg.inv(X.T @ X)
    meat = np.zeros((len(ks), len(ks)))
    order = np.argsort(g2, kind="stable")
    bounds = np.flatnonzero(np.diff(g2[order])) + 1
    for i in np.split(order, bounds):
        u = X[i].T @ resid[i]
        meat += np.outer(u, u)
    se = np.sqrt(np.diag(XtX @ meat @ XtX))
    n_k = [(Kk == k).sum() for k in ks]
    return pd.DataFrame({"k": ks, "coef": beta, "se": se, "pct": 100 * (np.exp(beta) - 1),
                         "n": n_k})


def summarize(r):
    pre = r[r.k.between(-12, -4)].pct.mean()
    post = r[r.k.between(0, K_HI)].pct.mean()
    late = r[r.k.between(13, K_HI)].pct.mean()
    drop = r[r.k.between(0, K_HI)].coef.mean() - r[r.k.between(-12, -4)].coef.mean()
    return pre, post, late, drop


rows, paths = [], []
exits = {}
for label, shift in [("real", 0), ("placebo", SHIFT)]:
    K, E, hits = assign(shift)
    treated = hits == 1
    clean = hits <= 1
    cal_row = treated & in_cal[np.clip(E, 0, None)]
    pres = present_cells(K, E, treated)
    key = pd.MultiIndex.from_arrays([E, hs8_code])
    pres_row = treated & key.isin(list(pres))
    print(f"\n[{label}] treated cell-months {treated.sum():,}; "
          f"present event-cells {len(pres):,}")

    for name, sel in [("all", treated), ("calendar", cal_row),
                      ("present", pres_row), ("both", cal_row & pres_row)]:
        keep = clean & (~treated | sel)
        r = estimate(keep, K)
        pre, post, late, drop = summarize(r)
        nk = r.set_index("k").n
        rows.append(dict(sample=name, run=label, cells_k0=int(nk[0]), cells_k18=int(nk[18]),
                         before=pre, after=post, months_13_18=late, fall_log=drop))
        paths.append(r.assign(sample=name, run=label))
        print(f"  {name:<9} k0 {nk[0]:>5}  k18 {nk[18]:>5}  before {pre:+5.1f}%  "
              f"after {post:+5.1f}%  months 13-18 {late:+5.1f}%  fall {drop:+.3f} log")

    # exits: of event-cells trading in the baseline, the share trading at each k
    t = pd.DataFrame({"E": E[treated], "h": hs8_code[treated], "k": K[treated]})
    base = t[t.k.between(*BASE)][["E", "h"]].drop_duplicates()
    n0 = len(base)
    t = t.merge(base, on=["E", "h"])
    exits[label] = (t.groupby("k").size() / n0).reindex(range(-12, K_HI + 1), fill_value=0)
    print(f"  baseline-trading event-cells: {n0:,}")

out = pd.DataFrame(rows)
out.to_csv("adcvd_cohort_check.csv", index=False)
pd.concat(paths).to_csv("adcvd_cohort_paths.csv", index=False)

ex = pd.DataFrame(exits)
ex.to_csv("adcvd_cohort_exits.csv")
print("\nshare of baseline-trading event-cells still trading")
print(f"  {'k':>4}{'real':>8}{'placebo':>9}")
for k in [-12, -6, -1, 0, 3, 6, 12, 18]:
    print(f"  {k:>4}{ex.real[k]:>8.2f}{ex.placebo[k]:>9.2f}")
print("\nwrote adcvd_cohort_check.csv, adcvd_cohort_paths.csv, adcvd_cohort_exits.csv")
