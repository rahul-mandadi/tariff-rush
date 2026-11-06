"""Recovery benchmark: after an AD/CVD preliminary, what usually happens to the targeted supplier?

For a sourcing team buying one product from a country just named in a preliminary AD/CVD
determination, the useful historical facts are: how often the supplier's position falls, how often
it comes back within 18 months, how long that takes, and how often trade stops altogether.

Unit: one targeted product-country pair in one episode (stacks from adcvd_stacked.py).
Position: the targeted country's share of the product's imports among the stack's countries
(targeted plus eligible rivals), smoothed as a 3-month trailing mean, so a month with no trade
counts as a share of zero rather than dropping out.
Benchmark: mean share over k = -18..-13, which precedes the case's initiation for 506 of 507
episodes (see RUN_LOG S2).

Categories, mutually exclusive, each pair in exactly one:
  no fall        smoothed share never below (1 - FALL) x benchmark in k = 0..6
  recovered      fell, then smoothed share at or above the benchmark for 3 consecutive months by
                 k = 18; recovery time is the first month of that run, counted from the fall
  not recovered  fell, not recovered by 18, traded at least once in k = 13..18
  exited         fell, not recovered, no trade in any month of k = 13..18
Recovered pairs that then stop trading in k = 13..18 are counted separately; they stay
"recovered" (ever recovered within 18 months).

Follow-up: pairs whose 18 months run past the data end are left out of the four-category shares
whatever their outcome so far, and censored at their last observed month for the Kaplan-Meier
estimate. The Kaplan-Meier clock starts at the month of the fall, and events are observed only up
to k = 18 after the duty.
Weighting: each episode counts once (each of its pairs weighted 1 / pairs in the episode). By pair,
the ten largest episodes, all 2024 aluminum extrusions cases, hold 30 percent of the pairs.
Uncertainty: 1,000 bootstrap draws of investigation groups.
Placebo: the same on stacks dated 24 months earlier.
Benchmark evaluation: for each year Y, category rates from episodes whose 18 months had finished
before Y began, scored against the realised categories of episodes with k = 0 in Y (multiclass
Brier score), against the rates from all years (in-sample, optimistic) and a uniform guess.

Usage:  python3 recovery_benchmark.py [--fall 0.2]
"""
import sys

import numpy as np
import pandas as pd

FALL = float(sys.argv[sys.argv.index("--fall") + 1]) if "--fall" in sys.argv else 0.2
K_HI = 18
B = 1000
rng = np.random.default_rng(0)
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
CATS = ["no fall", "recovered", "not recovered", "exited"]


def pairs(stacks, shift):
    d = stacks
    tot = d.groupby(["sid", "hs8", "k"]).value.sum()
    tg = d[d.treated].groupby(["sid", "hs8", "k"]).value.sum()
    sh = (tg / tot).fillna(0.0).rename("share").reset_index()
    out = []
    last_m = d.m.max()
    for (s, h), g in sh.groupby(["sid", "hs8"]):
        g = g.set_index("k").share.sort_index()
        bench = g.loc[-18:-13].mean()
        if not np.isfinite(bench) or bench <= 0:
            continue
        sm = g.rolling(3, min_periods=3).mean()
        post = sm.loc[0:K_HI]
        b0 = int(ep.b[s]) - shift
        follow = min(K_HI, int(last_m - b0))            # last observed k
        fell_at = next((k for k in range(0, 7) if k in post.index and post[k] < (1 - FALL) * bench),
                       None)
        rec_at = None
        if fell_at is not None:
            above = (post >= bench).reindex(range(fell_at, follow + 1), fill_value=False)
            run = 0
            for k, a in above.items():
                run = run + 1 if a else 0
                if run == 3:
                    rec_at = k - 2
                    break
        out.append(dict(sid=s, hs8=h, bench=bench, fell_at=fell_at, rec_at=rec_at, follow=follow,
                        cluster=int(ep.cluster[s]), year=(b0 // 12)))
    p = pd.DataFrame(out)
    trade = (d[d.treated & d.k.between(13, K_HI)].groupby(["sid", "hs8"]).value.sum() > 0)
    p["traded_13_18"] = [trade.get((s, h), False) for s, h in zip(p.sid, p.hs8)]
    complete = p.follow >= K_HI
    p["category"] = np.select(
        [p.fell_at.isna(), p.rec_at.notna(), p.traded_13_18],
        ["no fall", "recovered", "not recovered"], "exited")
    # every pair without a full 18 months is left out of the category shares, whatever its
    # outcome so far: keeping the incomplete pairs that had already done well (no fall, or an
    # early recovery) while dropping the rest would select on the outcome (fixed 2026-11-06)
    p.loc[~complete, "category"] = "censored"
    p["recovered_then_inactive"] = (p.category == "recovered") & ~p.traded_13_18
    return p


def weights(p):
    return 1.0 / p.groupby("sid").sid.transform("size")


def shares(p):
    c = p[p.category != "censored"]
    w = weights(c)
    return (w.groupby(c.category).sum() / w.sum()).reindex(CATS, fill_value=0.0)


def km(p):
    """Kaplan-Meier probability of having recovered by months since the fall, among pairs that fell."""
    f = p[p.fell_at.notna()].copy()
    f["t"] = np.where(f.rec_at.notna(), f.rec_at - f.fell_at, f.follow - f.fell_at)
    f["ev"] = f.rec_at.notna()
    f["w"] = weights(f)
    s, out = 1.0, {}
    for t in range(0, K_HI + 1):
        at_risk = f.w[f.t >= t].sum()
        ev = f.w[(f.t == t) & f.ev].sum()
        if at_risk:
            s *= 1 - ev / at_risk
        out[t] = 1 - s
    return pd.Series(out)


def boot(p, fn):
    cl = p.cluster.unique()
    idx = {c: p.index[p.cluster == c] for c in cl}
    draws = []
    for _ in range(B):
        pick = rng.choice(cl, len(cl), replace=True)
        # each drawn copy of a cluster gets fresh episode ids, so a cluster drawn twice counts
        # twice under the episode weights (otherwise weights() would merge the copies)
        parts = [p.loc[idx[c]].assign(sid=p.loc[idx[c], "sid"] + (n + 1) * 10_000_000)
                 for n, c in enumerate(pick)]
        draws.append(fn(pd.concat(parts)))
    return pd.concat(draws, axis=1).quantile([0.05, 0.95], axis=1).T


def brier(probs, test):
    """Episode-weighted multiclass Brier score."""
    y = pd.get_dummies(test.category).reindex(columns=CATS, fill_value=0).to_numpy(float)
    w = weights(test).to_numpy()
    return float(np.sum(w * np.sum((y - probs) ** 2, axis=1)) / w.sum())


if __name__ == "__main__":
    real = pairs(pd.read_parquet("panel/adcvd_stacks_real.parquet"), 0)
    plac = pairs(pd.read_parquet("panel/adcvd_stacks_placebo.parquet"), 24)
    res = []
    for label, p in [("real", real), ("placebo", plac)]:
        s = shares(p)
        ci = boot(p[p.category != "censored"], shares)
        k = km(p)
        kci = boot(p, km)
        n = (p.category != "censored").sum()
        print(f"\n[{label}] pairs {len(p):,} (complete {n:,}, censored "
              f"{(p.category == 'censored').sum():,}), episodes {p.sid.nunique()}, "
              f"groups {p.cluster.nunique()}; fall threshold {FALL:.0%}")
        for c in CATS:
            print(f"  {c:<14} {s[c]:.3f}  [{ci.loc[c, 0.05]:.3f}, {ci.loc[c, 0.95]:.3f}]")
            res.append(dict(sample=label, measure=c, value=s[c], lo=ci.loc[c, 0.05],
                            hi=ci.loc[c, 0.95], fall=FALL))
        rti = p.recovered_then_inactive.sum()
        print(f"  recovered, then inactive in 13..18: {rti}")
        print("  Kaplan-Meier, share of fallen pairs recovered by months since the fall:")
        for t in [3, 6, 12, 18]:
            print(f"    {t:>2}: {k[t]:.3f}  [{kci.loc[t, 0.05]:.3f}, {kci.loc[t, 0.95]:.3f}]")
            res.append(dict(sample=label, measure=f"KM recovered by {t}", value=k[t],
                            lo=kci.loc[t, 0.05], hi=kci.loc[t, 0.95], fall=FALL))

    # evaluate the benchmark on later cases
    c = real[real.category != "censored"].copy()
    ev = []
    allrates = shares(c).to_numpy()
    for Y in range(2018, 2025):
        test = c[c.year == Y]
        if len(test) < 30:
            continue
        # episodes whose 18 months (k = 0 at b) finished before January of Y
        bmonth = c.sid.map(ep.b)
        train = c[(bmonth + K_HI) < Y * 12]
        if len(train) < 100:
            continue
        r = shares(train).to_numpy()
        ev.append(dict(year=Y, n_test=len(test), n_train=len(train),
                       brier_benchmark=brier(np.tile(r, (len(test), 1)), test),
                       brier_all_years=brier(np.tile(allrates, (len(test), 1)), test),
                       brier_uniform=brier(np.full((len(test), 4), 0.25), test),
                       **{f"pred_{k}": v for k, v in zip(CATS, r)},
                       **{f"real_{k}": v for k, v in shares(test).items()}))
    E = pd.DataFrame(ev)
    print("\nbenchmark scored on later cases (lower Brier is better)")
    print(E[["year", "n_train", "n_test", "brier_benchmark", "brier_all_years",
             "brier_uniform"]].round(3).to_string(index=False))
    print(E[["year"] + [f"pred_{k}" for k in CATS] + [f"real_{k}" for k in CATS]].round(2)
          .to_string(index=False))

    tag = f"_fall{int(FALL * 100)}"
    pd.DataFrame(res).to_csv(f"recovery_benchmark{tag}.csv", index=False)
    E.to_csv(f"recovery_benchmark_eval{tag}.csv", index=False)
    real.to_csv(f"recovery_pairs_real{tag}.csv", index=False)
    plac.to_csv(f"recovery_pairs_placebo{tag}.csv", index=False)
    print(f"\nwrote recovery_benchmark{tag}.csv, recovery_benchmark_eval{tag}.csv, "
          f"recovery_pairs_*{tag}.csv")
