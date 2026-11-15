"""The four outcomes after a duty (no fall, fell and came back, stayed down, stopped) and recovery times.

Reads:  panel/adcvd_stacks_real.parquet, panel/adcvd_stacks_placebo.parquet, adcvd_episodes_collapsed.csv
Writes: recovery_benchmark_fall20.csv, recovery_benchmark_eval_fall20.csv, recovery_pairs_*_fall20.csv
        (the suffix follows --fall)
Run:    python3 measure/recovery_benchmark.py --fall 0.2
        (also 0.1 and 0.3; after measure/adcvd_stacked.py)
"""
import sys

import numpy as np
import pandas as pd

FALL = float(sys.argv[sys.argv.index("--fall") + 1]) if "--fall" in sys.argv else 0.2
K_HI = 18
LAG = 2  # months between the end of a data month and its release, rounded up
B = 1000
rng = np.random.default_rng(0)
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
CATS = ["no fall", "recovered", "not recovered", "exited"]


def pairs(stacks, shift):
    d = stacks
    tot = d.groupby(["sid", "hs8", "k"]).value.sum()
    tg = d[d.treated].groupby(["sid", "hs8", "k"]).value.sum()
    sh = (tg.reindex(tot.index).fillna(0.0) / tot).where(tot > 0).rename("share").reset_index()
    out = []
    last_m = d.m.max()
    for (s, h), g in sh.groupby(["sid", "hs8"]):
        g = g.set_index("k").share.sort_index()
        # put the path on calendar months: a month with no trade from any country in the panel
        # has no defined share, so it is missing, and the 3-month average needs 3 real months
        g = g.reindex(range(int(g.index.min()), int(g.index.max()) + 1))
        bench = g.loc[-18:-13].mean()
        if not np.isfinite(bench) or bench <= 0:
            continue
        sm = g.rolling(3, min_periods=3).mean()
        post = sm.loc[0:K_HI]
        if not post.loc[0:6].notna().any():  # no comparison trade in months 0..6: fall not measurable
            continue
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

    # the fake date covers fewer episodes (it needs 42 months of data before the case), so repeat
    # the real shares on just the episodes that also have a complete fake-date window. Run last so
    # the bootstrap draws for the two main samples are unchanged.
    both = set(plac[plac.category != "censored"].sid)
    pm = real[real.sid.isin(both)]
    s, ci = shares(pm), boot(pm[pm.category != "censored"], shares)
    print(f"\n[real, fake-date-matched episodes] complete pairs {(pm.category != 'censored').sum():,}, "
          f"episodes {pm[pm.category != 'censored'].sid.nunique()}")
    for c_ in CATS:
        print(f"  {c_:<14} {s[c_]:.3f}  [{ci.loc[c_, 0.05]:.3f}, {ci.loc[c_, 0.95]:.3f}]")
        res.append(dict(sample="real, fake-date-matched", measure=c_, value=s[c_],
                        lo=ci.loc[c_, 0.05], hi=ci.loc[c_, 0.95], fall=FALL))
    k, kci = km(pm), boot(pm, km)
    print(f"  Kaplan-Meier recovered by 18: {k[18]:.3f}  [{kci.loc[18, 0.05]:.3f}, {kci.loc[18, 0.95]:.3f}]")
    res.append(dict(sample="real, fake-date-matched", measure="KM recovered by 18", value=k[18],
                    lo=kci.loc[18, 0.05], hi=kci.loc[18, 0.95], fall=FALL))

    # evaluate the benchmark on later cases
    c = real[real.category != "censored"].copy()
    ev = []
    allrates = shares(c).to_numpy()
    for Y in range(2018, 2025):
        test = c[c.year == Y]
        if len(test) < 30:
            continue
        # episodes whose month k = 18 had been released before January of Y (Census publishes a
        # month's trade about five weeks after it ends)
        bmonth = c.sid.map(ep.b)
        train = c[(bmonth + K_HI + LAG) < Y * 12]
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
