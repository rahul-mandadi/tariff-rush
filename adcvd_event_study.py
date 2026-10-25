"""Month-by-month path of imports around an AD/CVD preliminary determination.

The episode test says imports from a targeted origin fall about 27 percent against other
origins of the same product, and that there is no rush beforehand. Two summary numbers cannot
show whether that drop is a step at the determination or a trend that was already running, and
the difference decides whether it can be read as caused by the duty.

k = 0 is the month duties start being collected. Fixed effects are product-month and
product-origin, so what is left is one origin moving against the others supplying the same
product that month. Baseline is k in [-18,-13].

A cell-month that falls inside more than one case's event window is dropped, since China and
Korea cells in particular are named by many cases and a contaminated observation cannot be
attributed to one of them. An earlier version assigned such a month to whichever case it met
first and dropped nothing, which left overlapping treatments pooled.

The same estimation is run on events shifted back 24 months, where no determination occurred, so
the path can be read against a placebo rather than against zero.

Usage:  python3 adcvd_event_study.py [--min-window 60]
"""
import sys
import numpy as np
import pandas as pd

args = sys.argv
MIN_W = int(args[args.index("--min-window")+1]) if "--min-window" in args else 60
K_LO, K_HI, BASE = -18, 18, (-18, -13)
SHIFT = 24          # placebo: the same events, two years before anything happened

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "ym", "lv"])
df["ym"] = pd.to_datetime(df.ym)
ymv = df.ym.values

e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
p = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in p.groupby("document_number")}
e = e[(e.stage == "preliminary") & e.window_days.notna() & (e.window_days >= MIN_W)]
e = e[e.document_number.isin(prods)].copy()
e["b"] = pd.to_datetime(e.publication_date).dt.to_period("M").dt.to_timestamp()
e["a"] = pd.to_datetime(e.initiation_date).dt.to_period("M").dt.to_timestamp()
print(f"events: {len(e)} doc-country rows, {e.document_number.nunique()} documents")

masks = []
for _, r in e.iterrows():
    m = (df.cty.values == r.cty) & df.hs8.isin(prods[r.document_number]).values
    if m.any():
        masks.append((m, r.a, r.b))
print(f"events hitting the panel: {len(masks)}")

contaminated = np.zeros(len(df), bool)
for m, a, b in masks:
    contaminated |= m & (ymv >= a.to_datetime64()) & (ymv <= b.to_datetime64())

def assign(shift):
    """Event time per row, and a count of how many events claim each row."""
    K = np.full(len(df), 99, dtype=int)
    hits = np.zeros(len(df), dtype=int)
    for m, a, b in masks:
        bb = b - pd.DateOffset(months=shift)
        k = ((df.ym.dt.year - bb.year) * 12 + (df.ym.dt.month - bb.month)).to_numpy()
        inwin = m & (k >= K_LO) & (k <= K_HI)
        hits += inwin
        sel = inwin & (K == 99)
        K[sel] = k[sel]
    return K, hits


def fit(shift, label):
    K, hits = assign(shift)
    # a month claimed by more than one case cannot be attributed to either
    drop = hits > 1
    print(f"\n[{label}] overlapping cell-months dropped: {drop.sum():,} "
          f"of {(hits > 0).sum():,} in any window")
    d = df[~drop].copy()
    Kk = K[~drop]
    ks = [k for k in range(K_LO, K_HI + 1) if not (BASE[0] <= k <= BASE[1])]
    X = np.column_stack([(Kk == k).astype(float) for k in ks])
    y = d.lv.to_numpy(float)
    g1 = d.groupby(["hs8", "ym"], sort=False).ngroup().to_numpy()
    g2 = d.groupby(["hs8", "cty"], sort=False).ngroup().to_numpy()
    return estimate(ks, X, y, g1, g2, label)


def dm(v, g):
    return v - (np.bincount(g, weights=v) / np.bincount(g))[g]


def estimate(ks, X, y, g1, g2, label):
    for _ in range(25):
        y = dm(dm(y, g1), g2)
        for j in range(X.shape[1]):
            X[:, j] = dm(dm(X[:, j], g1), g2)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    XtX = np.linalg.inv(X.T @ X)
    meat = np.zeros((len(ks), len(ks)))
    for _, idx in pd.Series(np.arange(len(y))).groupby(g2):
        i = idx.to_numpy()
        u = X[i].T @ resid[i]
        meat += np.outer(u, u)
    se = np.sqrt(np.diag(XtX @ meat @ XtX))
    print(f"  [{label}] n={len(y):,}  cells={len(np.unique(g2)):,}")
    return pd.DataFrame({"k": ks, "coef": beta, "se": se,
                         "pct": 100 * (np.exp(beta) - 1),
                         "sig": np.abs(beta / se) > 1.96})


real = fit(0, "real")
plac = fit(SHIFT, "placebo")

print(f"\nk = months from the preliminary determination (0 = duties start)")
print(f"baseline k in [{BASE[0]},{BASE[1]}], placebo shifted back {SHIFT} months\n")
print(f"  {'k':>4}{'real':>10}{'placebo':>11}{'difference':>13}")
for k in real.k:
    r = real[real.k == k].iloc[0]
    q = plac[plac.k == k].iloc[0]
    star = "*" if abs(r.coef / r.se) > 1.96 else " "
    print(f"  {k:>4}{r.pct:>9.1f}%{star}{q.pct:>10.1f}%{r.pct - q.pct:>12.1f}")

real.to_csv("adcvd_event_study.csv", index=False)
plac.to_csv("adcvd_event_study_placebo.csv", index=False)
print("\nwrote adcvd_event_study.csv and adcvd_event_study_placebo.csv")
