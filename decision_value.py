"""Decision value: is acting on the forecasts better than the simple policies a sourcing team has?

The decision: start qualifying an alternative supplier (act) or wait. Acting is right if the
targeted supplier's position falls and does not come back ("bad"); waiting is right otherwise.
With qualification cost C and the loss L it avoids when the outcome is bad, acting pays when
P(bad) >= C / L. Call that threshold t.

Net benefit (decision-curve analysis, Vickers and Elkin 2006) of a policy at threshold t, per
product:   NB(t) = share acted on that turned out bad  -  share acted on that did not  x  t / (1 - t),
in units of "bad outcomes prepared for, net of the cost of unneeded qualifications". Policies:
  model         act when the forecast P(bad) >= t
  history       the historical rate known at the time: act on everything if it is >= t, else nothing
  always act    qualify a second supplier for every targeted product
  never act     NB = 0
Held-out predictions from prediction_test.py (day one) and prediction_stage2.py, episode-weighted.
The model is fixed in advance as the logistic regression at every point (the one model class used
throughout); boosting and Cox are reported alongside as sensitivity ("alt" columns) and play no part
in choosing anything. At the ITC vote the simple policies include the rate split by vote. The model's
gain over the best simple policy at each t carries a pointwise 90 percent interval from 1,000
resamples of investigation groups, holding the fitted models fixed; because 17 thresholds are
checked, the joint check reports, for the run of thresholds where the pointwise interval is above
zero, the share of resamples in which the model is ahead at every one of them at once.

Usage:  python3 decision_value.py      # after prediction_test.py and prediction_stage2.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(0)
T = np.round(np.arange(0.10, 0.901, 0.05), 2)

d0 = pd.read_csv("prediction_test_heldout.csv")
s2 = pd.read_csv("prediction_stage2_heldout.csv")
points = {
    "duty starts": pd.DataFrame({"cluster": d0.cluster, "w": d0.w, "bad": d0.bad,
                                 "model": d0.p_model, "history": d0.p_benchmark}),
    "fall first visible": (lambda g: pd.DataFrame({"cluster": g.cluster, "w": g.w, "bad": 1 - g.y,
                                                   "model": 1 - g["logit"], "history": 1 - g.history,
                                                   "alt boosting": 1 - g["boosting"], "alt Cox": 1 - g["Cox"]}))(
        s2[s2.point == "fall"]),
    "ITC final vote": (lambda g: pd.DataFrame({"cluster": g.cluster, "w": g.w, "bad": 1 - g.y,
                                               "model": 1 - g["logit, + vote"], "history": 1 - g.history,
                                               "history by vote": 1 - g["history by vote"],
                                               "alt boosting": 1 - g["boosting, + vote"],
                                               "alt Cox": 1 - g["Cox, + vote"]}))(
        s2[s2.point == "ITC"]),
}


def nb(act, bad, w, t):
    W = w.sum()
    return (w * act * bad).sum() / W - (w * act * (1 - bad)).sum() / W * t / (1 - t)


def curves(d, t):
    bad, w = d.bad.to_numpy(float), d.w.to_numpy(float)
    out = {"model": nb((d.model >= t).to_numpy(), bad, w, t),
           "history": nb((d.history >= t).to_numpy(), bad, w, t),
           "always act": nb(np.ones(len(d), bool), bad, w, t), "never act": 0.0}
    if "history by vote" in d:
        out["history by vote"] = nb((d["history by vote"] >= t).to_numpy(), bad, w, t)
    simple = [k for k in out if k != "model"]
    for alt in [c for c in d.columns if c.startswith("alt ")]:
        out[alt] = nb((d[alt] >= t).to_numpy(), bad, w, t)
    out["best simple"] = max(out[k] for k in simple)
    return out


rows, band, joint = [], {}, {}
for name, d in points.items():
    d = d.reset_index(drop=True)
    cl = d.cluster.unique()
    idx = {c: np.flatnonzero(d.cluster.values == c) for c in cl}
    draws = []
    for _ in range(1000):
        q = d.iloc[np.concatenate([idx[c] for c in rng.choice(cl, len(cl), replace=True)])]
        draws.append([curves(q, t)["model"] - curves(q, t)["best simple"] for t in T])
    draws = np.array(draws)
    joint[name] = draws
    for i, t in enumerate(T):
        c = curves(d, t)
        rows.append(dict(point=name, threshold=t, **c, gain=c["model"] - c["best simple"],
                         lo=np.quantile(draws[:, i], 0.05), hi=np.quantile(draws[:, i], 0.95)))
R = pd.DataFrame(rows)
R.to_csv("decision_value.csv", index=False)
pd.set_option("display.width", 200)
for name in points:
    x = R[R.point == name]
    print(f"\n[{name}] prevalence of bad outcomes "
          f"{np.average(points[name].bad, weights=points[name].w):.3f}")
    print(x.drop(columns="point").round(3).to_string(index=False))
    win = x[x.lo > 0].threshold
    print(f"  model beats every simple policy (pointwise 90% interval above zero) for thresholds: "
          f"{', '.join(f'{v:.2f}' for v in win) if len(win) else 'none'}")
    band[name] = list(win)
# joint check: across the longest run of consecutive winning thresholds, the share of resamples in
# which the model beats the best simple policy at every one of them at once
J = []
for name, win in band.items():
    if not win:
        continue
    runs, cur = [], [win[0]]
    for a, b in zip(win, win[1:]):
        if round(b - a, 2) == 0.05:
            cur.append(b)
        else:
            runs.append(cur); cur = [b]
    runs.append(cur)
    run = max(runs, key=len)
    cols = [list(T).index(t) for t in run]
    share = float((joint[name][:, cols] > 0).all(axis=1).mean())
    J.append(dict(point=name, lo=run[0], hi=run[-1], thresholds=len(run), share_all_positive=share))
    print(f"[{name}] thresholds {run[0]:.2f} to {run[-1]:.2f}: model ahead at all {len(run)} at once in "
          f"{100 * share:.0f}% of resamples")
pd.DataFrame(J).to_csv("decision_value_joint.csv", index=False)
print("\nwrote decision_value.csv, decision_value_joint.csv")
