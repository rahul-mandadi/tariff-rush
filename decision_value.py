"""Decision value: potential net benefit of acting on the forecasts, under assumed costs.

The decision: start qualifying an alternative supplier (act) or wait. Acting is right if the
targeted country's position in the product falls and does not come back by month 18 ("bad").
With an assumed qualification cost C and an assumed avoidable loss L when the outcome is bad,
acting pays when P(bad) >= t = C / L. This is a potential benefit under those assumptions, not a
measured saving. It assumes (i) the country-level outcome stands in for the loss to an importer
buying from that country, and (ii) qualifying at the decision date can still avoid that loss
(qualification takes days to about 18 months, see evidence/USE_EVIDENCE.md).

Net benefit (decision-curve analysis, Vickers and Elkin 2006) of a policy at threshold t, per
product:  NB(t) = share acted on that turned out bad - share acted on that did not x t / (1 - t).

Policies, all as probabilities of the bad outcome (non-recovery):
  model           logistic regression, the common model at every decision point (chosen for
                  consistency across points, not preregistered); P(bad) = 1 - P(recover) for the
                  stage-2 files, P(bad) directly for day one
  history         the training-years base rate; act on everything if >= t, else nothing
  history by vote at the ITC vote only, the base rate split by the vote
  share only      at the ITC vote only, the logistic model of the latest published share
  always / never  qualify for every product / for none (NB = 0)
Boosting and Cox are reported as sensitivity columns and do not enter any comparison.

Inference. The threshold grid is fixed in advance: 0.10 to 0.90 in steps of 0.05 (17 points).
Every policy is scored on the same 2,000 paired resamples of investigation groups. For each
baseline b and threshold t, D(b, t) = NB(model) - NB(b). Pointwise 90 percent intervals are the
5th and 95th percentiles of D. Simultaneous one-sided 90 percent lower bounds over all (b, t) use
the max-t method: with s(b, t) the bootstrap standard deviation of D, c is the 90th percentile of
max over (b, t) of (D* - D) / s, and the bound is D - c x s. The model is supported at t only if
its simultaneous bound is above zero against every baseline at t. All intervals hold the fitted
models fixed; they do not reflect refitting on other training data.

Usage:  python3 decision_value.py      # after prediction_test.py and prediction_stage2.py
"""
import numpy as np
import pandas as pd

B = 2000
rng = np.random.default_rng(0)
T = np.round(np.arange(0.10, 0.901, 0.05), 2)

d0 = pd.read_csv("prediction_test_heldout.csv")
s2 = pd.read_csv("prediction_stage2_heldout.csv")
fall, itc = s2[s2.point == "fall"], s2[s2.point == "ITC"]
points = {
    "duty starts": pd.DataFrame({"cluster": d0.cluster, "w": d0.w, "bad": d0.bad,
                                 "model": d0.p_model, "history": d0.p_benchmark}),
    "fall first visible": pd.DataFrame({"cluster": fall.cluster, "w": fall.w, "bad": 1 - fall.y,
                                        "model": 1 - fall["logit"], "history": 1 - fall.history,
                                        "alt boosting": 1 - fall["boosting"], "alt Cox": 1 - fall["Cox"]}),
    "ITC final vote": pd.DataFrame({"cluster": itc.cluster, "w": itc.w, "bad": 1 - itc.y,
                                    "model": 1 - itc["logit, + vote"], "history": 1 - itc.history,
                                    "history by vote": 1 - itc["history by vote"],
                                    "share only": 1 - itc["logit, latest share only"],
                                    "alt boosting": 1 - itc["boosting, + vote"],
                                    "alt Cox": 1 - itc["Cox, + vote"]}),
}
PROB_BASELINES = ["history", "history by vote", "share only"]


def nb_matrix(d, cols, idx=None):
    """Net benefit of each probability column at every threshold, plus always act; rows of d
    taken by idx (a resample) if given."""
    bad = d.bad.to_numpy(float)
    w = d.w.to_numpy(float)
    if idx is not None:
        bad, w = bad[idx], w[idx]
    W = w.sum()
    out = {}
    for c in cols:
        p = d[c].to_numpy(float)
        if idx is not None:
            p = p[idx]
        act = p[:, None] >= T[None, :]
        tp = (w[:, None] * act * bad[:, None]).sum(0) / W
        fp = (w[:, None] * act * (1 - bad[:, None])).sum(0) / W
        out[c] = tp - fp * T / (1 - T)
    prev = (w * bad).sum() / W
    out["always act"] = prev - (1 - prev) * T / (1 - T)
    out["never act"] = np.zeros(len(T))
    return out


def main():
    rows, sim = [], []
    for name, d in points.items():
        d = d.reset_index(drop=True)
        prob_cols = ["model"] + [c for c in PROB_BASELINES if c in d] + [c for c in d if c.startswith("alt ")]
        baselines = [c for c in PROB_BASELINES if c in d] + ["always act", "never act"]
        est = nb_matrix(d, prob_cols)
        cl = d.cluster.unique()
        ix = {c: np.flatnonzero(d.cluster.values == c) for c in cl}
        diffs = {b: np.empty((B, len(T))) for b in baselines}
        for r in range(B):
            idx = np.concatenate([ix[c] for c in rng.choice(cl, len(cl), replace=True)])
            nb = nb_matrix(d, prob_cols, idx)
            for b in baselines:
                diffs[b][r] = nb["model"] - nb[b]
        # max-t simultaneous lower bounds over every (baseline, threshold)
        D = np.stack([est["model"] - est[b] for b in baselines])          # baselines x thresholds
        Dstar = np.stack([diffs[b] for b in baselines], axis=1)            # draws x baselines x T
        sd = Dstar.std(axis=0, ddof=1)
        live = sd > 1e-9  # below this the spread is floating-point noise
        z = np.where(live, (Dstar - D) / np.where(live, sd, 1), 0.0)
        c90 = np.quantile(z.reshape(B, -1).max(axis=1), 0.90)
            # policies that act on the same products differ only by floating-point noise: a tie
        sim_lo = np.where(np.abs(D) < 1e-12, 0.0, np.where(live, D - c90 * sd, D))
        for j, t in enumerate(T):
            row = dict(point=name, threshold=t, **{f"nb_{k}": v[j] for k, v in est.items()})
            for i, b in enumerate(baselines):
                row[f"diff_{b}"] = D[i, j]
                row[f"lo_{b}"], row[f"hi_{b}"] = np.quantile(Dstar[:, i, j], [0.05, 0.95])
                row[f"simlo_{b}"] = sim_lo[i, j]
            row["supported"] = bool(all(sim_lo[i, j] > 0 for i in range(len(baselines))))
            rows.append(row)
        supported = [t for j, t in enumerate(T) if all(sim_lo[i, j] > 0 for i in range(len(baselines)))]
        sim.append(dict(point=name, baselines=", ".join(baselines), critical_value=c90,
                        supported_thresholds=", ".join(f"{t:.2f}" for t in supported) or "none",
                        n_supported=len(supported)))

    R = pd.DataFrame(rows)
    R.to_csv("decision_value.csv", index=False)
    S = pd.DataFrame(sim)
    S.to_csv("decision_value_joint.csv", index=False)
    pd.set_option("display.width", 220)
    for name in points:
        x = R[R.point == name]
        cols = ["threshold", "nb_model"] + [c for c in x.columns if c.startswith("simlo_")]
        print(f"\n[{name}] prevalence of bad outcomes "
              f"{np.average(points[name].bad, weights=points[name].w):.3f}")
        print(x[cols].dropna(axis=1, how="all").round(3).to_string(index=False))
    print("\nsimultaneous support (model ahead of every baseline, one-sided 90 percent, max-t over all "
          "baselines and thresholds):")
    print(S.round(3).to_string(index=False))
    print("\nwrote decision_value.csv, decision_value_joint.csv")


if __name__ == "__main__":
    main()
