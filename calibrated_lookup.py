"""Calibrated lookup: the second-decision-point models (prediction_stage2.py) as a table a sourcing
team can read, "of 100 products like yours, about N came back".

Calibration: the held-out predictions run high in places. For each test year Y, a Platt scaling
(logistic regression on the logit of the model's probability) is fitted only on held-out predictions
of earlier years whose month 18 had been published before January of Y (at least 50 products), and
applied to year Y. Earlier test years have too little published history and stay uncalibrated. Compared on the years
that can be calibrated: Brier score and calibration by predicted tercile, raw against calibrated.

Lookup cells, using facts visible at each decision:
  at the fall      the targeted supplier's pre-case imports (12 months, k -18..-7) under $1M, $1M to
                   $10M, over $10M; and the preliminary duty rate missing, up to 25 percent, over 25
  at the ITC vote  the latest published share against the pre-case level (under half, half to
                   four-fifths, four-fifths or more); and the vote (duty confirmed or lifted)
Each cell: held-out products and cases, the model's average prediction, and the share that actually
came back. The cells use the uncalibrated prediction, because the calibration test above made later
years worse once it was restricted to labels already published. Cells with fewer than 20 products or 5 cases are marked too few.
Episode-weighted, as everywhere else.

Usage:  python3 calibrated_lookup.py      # after prediction_stage2.py
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

P = pd.read_csv("prediction_stage2_heldout.csv")
D = pd.read_csv("prediction_stage2_features.csv", dtype={"hs8": str})
yrs = pd.read_csv("prediction_stage2_years.csv")
MODEL = {"fall": "boosting", "ITC": "logit, + vote"}
K_HI, LAG = 18, 2
logit = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4)))  # noqa: E731


def aligned(pt):
    """Held-out rows with their features: run() wrote each test year's rows in feature-file order."""
    d = D[D.point == pt].reset_index(drop=True)
    f = pd.concat([d[d.year == Y] for Y in yrs[yrs.point == pt].year]).reset_index(drop=True)
    p = P[P.point == pt].reset_index(drop=True)
    assert (f.sid.values == p.sid.values).all() and (f.recovered.values == p.y.values).all()
    return pd.concat([p, f.drop(columns=["sid", "cluster", "w", "year"])], axis=1)


def calibrate(p, col):
    out = pd.Series(np.nan, index=p.index)
    for Y in sorted(p.year.unique()):
        # only earlier held-out cases whose month 18 had been published before January of Y
        past, now = p[(p.year < Y) & (p.b + K_HI + LAG < Y * 12)], p.year == Y
        if len(past) < 50 or past.y.nunique() < 2:
            continue
        m = LogisticRegression(C=1e6).fit(logit(past[col]).to_frame(), past.y, sample_weight=past.w)
        out[now] = m.predict_proba(logit(p.loc[now, col]).to_frame())[:, 1]
    return out


def terciles(p, col):
    t = pd.qcut(p[col].rank(method="first"), 3, labels=["low", "mid", "high"])
    return p.groupby(t, observed=True).apply(
        lambda g: pd.Series(dict(pred=np.average(g[col], weights=g.w), real=np.average(g.y, weights=g.w))),
        include_groups=False)


ev, cells = [], []
for pt in ["fall", "ITC"]:
    p = aligned(pt)
    col = MODEL[pt]
    p["calibrated"] = calibrate(p, col)
    c = p[p.calibrated.notna()]
    print(f"\n[{pt}] model: {col}; calibrated test years {sorted(c.year.unique())}, products {len(c):,}")
    for name in [col, "calibrated"]:
        bs = brier_score_loss(c.y, c[name], sample_weight=c.w)
        t = terciles(c, name)
        gap = float((t.pred - t.real).abs().max())
        print(f"  {name:<16} Brier {bs:.4f}; mean predicted {np.average(c[name], weights=c.w):.3f} vs "
              f"realized {np.average(c.y, weights=c.w):.3f}; largest tercile gap {gap:.3f}")
        print("   ", t.round(3).to_dict("index"))
        ev.append(dict(point=pt, model=name, years=f"{c.year.min()}-{c.year.max()}", brier=bs,
                       mean_pred=np.average(c[name], weights=c.w), realized=np.average(c.y, weights=c.w),
                       max_tercile_gap=gap))
    # lookup cells, on every held-out product, with the model's own (uncalibrated) prediction:
    # calibrating on earlier published years made the later years worse (calibrated_lookup_eval.csv)
    p["pred"] = p[col]
    if pt == "fall":
        val = np.expm1(p.log_pre_value)
        p["row"] = pd.cut(val, [-1, 1e6, 1e7, np.inf], labels=["under $1M", "$1M to $10M", "over $10M"])
        rate = np.expm1(p.log_rate)
        p["col"] = np.where(p.rate_missing == 1, "rate not published",
                            np.where(rate <= 25, "rate up to 25%", "rate over 25%"))
        rlab, clab = "pre-case imports, 12 months", "preliminary duty rate"
    else:
        p["row"] = pd.cut(p.latest, [-np.inf, 0.5, 0.8, np.inf], right=False,
                          labels=["under half", "half to 4/5", "4/5 or more"])
        p["col"] = np.where(p.itc_negative == 1, "duty lifted", "duty confirmed")
        rlab, clab = "latest share vs pre-case", "ITC vote"
    for (r, cc), g in p.groupby(["row", "col"], observed=True):
        few = len(g) < 20 or g.sid.nunique() < 5
        cells.append(dict(point=pt, row_by=rlab, row=r, col_by=clab, col=cc, products=len(g),
                          cases=g.sid.nunique(),
                          expected=np.nan if few else np.average(g.pred, weights=g.w),
                          came_back=np.nan if few else np.average(g.y, weights=g.w), too_few=few))
L = pd.DataFrame(cells)
pd.set_option("display.width", 200)
for pt in ["fall", "ITC"]:
    x = L[L.point == pt]
    print(f"\nlookup at the {pt}: expected (model) / came back (held-out), per 100 products")
    tab = x.assign(cell=[("too few" if f else f"{100 * e:.0f} / {100 * b:.0f}  ({n} products, {c} cases)")
                         for e, b, n, c, f in zip(x.expected, x.came_back, x.products, x.cases, x.too_few)])
    order = {"fall": ["under $1M", "$1M to $10M", "over $10M"],
             "ITC": ["under half", "half to 4/5", "4/5 or more"]}[pt]
    print(tab.pivot(index="row", columns="col", values="cell").reindex(order).to_string())
pd.DataFrame(ev).to_csv("calibrated_lookup_eval.csv", index=False)
L.to_csv("calibrated_lookup.csv", index=False)
print("\nwrote calibrated_lookup.csv, calibrated_lookup_eval.csv")
