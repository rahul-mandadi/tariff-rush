"""Did treated imports rise between announcement and effective date, relative to the
same product from origins that were not tariffed?

This is the comparison the chapter-level work could not make. A commodity price shock
moves every origin of a product together. A tariff moves one origin relative to the
others. So the control for "aluminum from Canada in March 2018" is aluminum from every
origin not tariffed, in March 2018.

Two-way fixed effects by iterative demeaning:
  product x month   absorbs anything that moved a product globally that month
  product x origin  absorbs the fact that some origins are simply bigger suppliers

Terms, all relative to the same product from untreated origins in the same month:
  pre    three months before announcement. Should be flat. This is the placebo: if it
         is large, the design is picking up trends rather than the tariff.
  rush   announcement month through effective month, when buying ahead can happen
  post   six months after it took effect, where payback would show up

On action_kind: the classifier labels most real impositions SCOPE_CHANGE, including the
original Section 301 action and the 2025 reciprocal tariffs. Filtering to IMPOSE left two
events. So direction is taken the other way round, by excluding the actions that plainly
reduce exposure (REVOKE, DECREASE, SUSPEND) and keeping the rest.

Usage:  python3 within_product_test.py [--outcome lv|lq]
"""
import sys
import numpy as np
import pandas as pd

OUT = "lq" if "--outcome" in sys.argv and sys.argv[sys.argv.index("--outcome")+1] == "lq" else "lv"
MIN_WINDOW, PRE_MONTHS, POST_MONTHS = 7, 3, 6
REDUCING = {"REVOKE", "DECREASE", "SUSPEND"}

df = pd.read_parquet("panel/analysis.parquet",
                     columns=["hs8", "cty", "chapter", "ym", "lv", "lq"])
df = df[df[OUT].notna()].reset_index(drop=True)
df["ym"] = pd.to_datetime(df.ym)

ev = pd.read_csv("events_resolved.csv", dtype={"cty": str})
ep = pd.read_csv("event_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in ep.groupby("document_number")}
ev = ev[(ev.window_days >= MIN_WINDOW) & (~ev.action_kind.isin(REDUCING))].copy()
ev["a"] = pd.to_datetime(ev.announcement_date).dt.to_period("M").dt.to_timestamp()
ev["e"] = pd.to_datetime(ev.effective_date).dt.to_period("M").dt.to_timestamp()

print(f"panel {len(df):,} rows, outcome = {'log value' if OUT=='lv' else 'log quantity'}")
print(f"events usable: {ev.document_number.nunique()}  "
      f"({ev.groupby('mechanism').document_number.nunique().to_dict()})")


def mask_for(e):
    m = (df.cty.values == e.cty)
    if e.mechanism == "ENUMERATED":
        m &= df.hs8.isin(prods.get(e.document_number, set())).values
    elif e.mechanism == "MATERIAL_CLASS":
        m &= df.chapter.isin(set(str(e.chapters).split(";"))).values
    return m


def flags(events):
    pre = np.zeros(len(df), bool); rush = np.zeros(len(df), bool); post = np.zeros(len(df), bool)
    ymv = df.ym.values
    for _, e in events.iterrows():
        m = mask_for(e)
        if not m.any():
            continue
        a0 = (e.a - pd.DateOffset(months=PRE_MONTHS)).to_datetime64()
        pe = (e.e + pd.DateOffset(months=POST_MONTHS)).to_datetime64()
        a, b = e.a.to_datetime64(), e.e.to_datetime64()
        pre |= m & (ymv >= a0) & (ymv < a)
        rush |= m & (ymv >= a) & (ymv <= b)
        post |= m & (ymv > b) & (ymv <= pe)
    rush_only = rush
    return pre & ~rush_only, rush_only, post & ~rush_only


def demean(v, g):
    return v - (np.bincount(g, weights=v) / np.bincount(g))[g]


def run(events, label):
    pre, rush, post = flags(events)
    if rush.sum() == 0:
        print(f"\n{label}: no treated cell-months"); return
    keep = np.ones(len(df), bool)
    # a product-month is only usable if some origin of it is untreated that month
    tm = pd.DataFrame({"g": df.groupby(["hs8", "ym"], sort=False).ngroup(), "t": rush})
    bad = tm.groupby("g").t.transform("all").to_numpy()
    keep &= ~bad
    d = df[keep]
    y = d[OUT].to_numpy(float)
    X = np.column_stack([pre[keep].astype(float), rush[keep].astype(float),
                         post[keep].astype(float)])
    g1 = d.groupby(["hs8", "ym"], sort=False).ngroup().to_numpy()
    g2 = d.groupby(["hs8", "cty"], sort=False).ngroup().to_numpy()
    for _ in range(25):
        y = demean(demean(y, g1), g2)
        for j in range(X.shape[1]):
            X[:, j] = demean(demean(X[:, j], g1), g2)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    meat = np.zeros((3, 3))
    for _, idx in pd.Series(np.arange(len(y))).groupby(g2):
        i = idx.to_numpy()
        u = X[i].T @ resid[i]
        meat += np.outer(u, u)
    se = np.sqrt(np.diag(XtX_inv @ meat @ XtX_inv))
    print(f"\n{label}   events={events.document_number.nunique()}  "
          f"treated cell-months: rush {rush.sum():,}, post {post.sum():,}")
    print(f"  {'term':<7}{'coef':>9}{'se':>8}{'t':>7}{'effect':>10}")
    for nm, b, s in zip(["pre", "rush", "post"], beta, se):
        star = "*" if abs(b / s) > 1.96 else " "
        print(f"  {nm:<7}{b:>9.4f}{s:>8.4f}{b/s:>7.2f}{100*(np.exp(b)-1):>9.1f}%{star}")
    print(f"  n={len(y):,}  cells={len(np.unique(g2)):,}")


run(ev, "ALL MECHANISMS")
for mech in ["ENUMERATED", "COUNTRY_WIDE", "MATERIAL_CLASS"]:
    sub = ev[ev.mechanism == mech]
    if len(sub):
        run(sub, mech)
