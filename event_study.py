"""Month-by-month version of the within-product test.

The three-bin test said the enumerated events had a +64.6% "pre" period, which is larger
than its own rush. A pre-period that big means the design is tracking something already in
motion, so the rush number cannot be read. Three bins cannot show what. This traces the
coefficient month by month around the announcement instead.

What a genuine rush looks like: flat before the announcement, a spike between announcement
and effective date, a dip after. What contamination looks like: already climbing well
before the announcement.

Contamination control: a cell-month is dropped if it sits inside the window of any OTHER
event, so one tariff's rush cannot be read as another's pre-period. China alone has
roughly twenty actions, so without this the windows overlap constantly.

Baseline is k in [-12,-7], i.e. a year to half a year before announcement.

Usage:  python3 event_study.py [--mech ENUMERATED] [--outcome lv|lq]
"""
import sys
import numpy as np
import pandas as pd

args = sys.argv
MECH = args[args.index("--mech")+1] if "--mech" in args else None
OUT = args[args.index("--outcome")+1] if "--outcome" in args else "lv"
DIFF = "--diff" in args
K_LO, K_HI, BASE = -12, 12, (-12, -7)
REDUCING = {"REVOKE", "DECREASE", "SUSPEND"}

df = pd.read_parquet("panel/analysis.parquet", columns=["hs8", "cty", "chapter", "ym", "lv", "lq"])
df = df[df[OUT].notna()].reset_index(drop=True)
df["ym"] = pd.to_datetime(df.ym)

if DIFF:
    # a level that is already climbing breaks parallel trends. Differencing removes the
    # slow trend and leaves the month-to-month jump, which is what a rush actually is.
    # Only consecutive months are differenced; a gap in the cell produces a null.
    df = df.sort_values(["hs8", "cty", "ym"]).reset_index(drop=True)
    g = df.groupby(["hs8", "cty"], sort=False)
    prev_v = g[OUT].shift(1)
    prev_m = g["ym"].shift(1)
    consec = (df.ym - prev_m).dt.days.between(28, 31)
    df[OUT] = np.where(consec, df[OUT] - prev_v, np.nan)
    df = df[df[OUT].notna()].reset_index(drop=True)
    print(f"differenced: {len(df):,} consecutive-month observations")

ymv = df.ym.values

ev = pd.read_csv("events_resolved.csv", dtype={"cty": str})
ep = pd.read_csv("event_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in ep.groupby("document_number")}
ev = ev[(ev.window_days >= 7) & (~ev.action_kind.isin(REDUCING))].copy()
ev["a"] = pd.to_datetime(ev.announcement_date).dt.to_period("M").dt.to_timestamp()
ev["e"] = pd.to_datetime(ev.effective_date).dt.to_period("M").dt.to_timestamp()
allev = ev.copy()
if MECH:
    ev = ev[ev.mechanism == MECH]
print(f"outcome={OUT}  mechanism={MECH or 'ALL'}  events={ev.document_number.nunique()}")


def mask_for(e):
    m = (df.cty.values == e.cty)
    if e.mechanism == "ENUMERATED":
        m &= df.hs8.isin(prods.get(e.document_number, set())).values
    elif e.mechanism == "MATERIAL_CLASS":
        m &= df.chapter.isin(set(str(e.chapters).split(";"))).values
    return m


# any cell-month inside some other event's announce..effective window
contaminated = np.zeros(len(df), bool)
for _, e in allev.iterrows():
    contaminated |= mask_for(e) & (ymv >= e.a.to_datetime64()) & (ymv <= e.e.to_datetime64())

K = np.full(len(df), 99, dtype=int)
own = np.zeros(len(df), bool)
for _, e in ev.iterrows():
    m = mask_for(e)
    if not m.any():
        continue
    k = ((df.ym.dt.year - e.a.year) * 12 + (df.ym.dt.month - e.a.month)).to_numpy()
    sel = m & (k >= K_LO) & (k <= K_HI) & (K == 99)
    K[sel] = k[sel]
    own |= m & (k >= K_LO) & (k <= K_HI)

treated_now = (K != 99)
# drop other events' windows from this event's timeline
drop = contaminated & ~((K >= 0) & (K <= 12) & treated_now)
keep = ~drop
d = df[keep].copy()
Kk = K[keep]
print(f"rows kept {len(d):,} of {len(df):,}  (dropped {drop.sum():,} contaminated)")
print(f"treated cell-months in window: {(Kk != 99).sum():,}")

ks = [k for k in range(K_LO, K_HI + 1) if not (BASE[0] <= k <= BASE[1])]
X = np.column_stack([(Kk == k).astype(float) for k in ks])
y = d[OUT].to_numpy(float)
g1 = d.groupby(["hs8", "ym"], sort=False).ngroup().to_numpy()
g2 = d.groupby(["hs8", "cty"], sort=False).ngroup().to_numpy()


def demean(v, g):
    return v - (np.bincount(g, weights=v) / np.bincount(g))[g]


for _ in range(25):
    y = demean(demean(y, g1), g2)
    for j in range(X.shape[1]):
        X[:, j] = demean(demean(X[:, j], g1), g2)

beta, *_ = np.linalg.lstsq(X, y, rcond=None)
resid = y - X @ beta
XtX_inv = np.linalg.inv(X.T @ X)
meat = np.zeros((len(ks), len(ks)))
for _, idx in pd.Series(np.arange(len(y))).groupby(g2):
    i = idx.to_numpy()
    u = X[i].T @ resid[i]
    meat += np.outer(u, u)
se = np.sqrt(np.diag(XtX_inv @ meat @ XtX_inv))

print(f"\nmonths relative to announcement (0 = announcement month)")
print(f"baseline = k in [{BASE[0]},{BASE[1]}]\n")
print(f"  {'k':>4}{'coef':>9}{'se':>8}{'effect':>10}   ")
for k, b, s in zip(ks, beta, se):
    star = "*" if abs(b / s) > 1.96 else " "
    bar = "#" * min(40, int(abs(b) * 40))
    side = " " * 20 if b >= 0 else " " * max(0, 20 - len(bar))
    print(f"  {k:>4}{b:>9.4f}{s:>8.4f}{100*(np.exp(b)-1):>9.1f}%{star} "
          f"{(side + bar) if b >= 0 else (side + bar)}")
print(f"\nn={len(y):,}  cells={len(np.unique(g2)):,}")

out = pd.DataFrame({"k": ks, "coef": beta, "se": se,
                    "pct": 100*(np.exp(beta)-1),
                    "sig": np.abs(beta/se) > 1.96})
out["mechanism"] = MECH or "ALL"
out["outcome"] = OUT
fn = f"event_study_{(MECH or 'ALL').lower()}_{OUT}{'_diff' if DIFF else ''}.csv"
out.to_csv(fn, index=False)
print(f"wrote {fn}")
