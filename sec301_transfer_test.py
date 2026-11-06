"""Does the at-the-fall recovery model learned on AD/CVD cases transfer to Section 301?

Population in both domains: targeted products that fell (sec301_benchmark.py, horizon H = 16,
complete follow-up). Target: back at or above the pre-case share for three months running by
k = 16. Decision: the month the fall first shows in published data (k_fall + 2).

Features, as prediction_stage2.py at the fall, minus three that cannot transfer: China (always 1
under Section 301), both AD and CVD, and critical circumstances (always 0). Kept: pre-case share,
trend, size, rival count and concentration (every country trading in k -18..-7), the duty rate
known at the decision (AD/CVD: notices published by then; Section 301: 25 percent for Lists 1 and
2, 10 percent for List 3 until the May 2019 increase is public, 25 after) with a missing flag, and
the trade so far: month of the fall, deepest and latest smoothed share, months with no trade,
share in k -6..-1, unit-value change against rivals.

Tests:
  A  regime transfer     train on every AD/CVD case, score Section 301. Not a forecast anyone
                         could have made in 2018, since most AD/CVD training cases come later; it
                         asks whether the relationship carries across laws.
  B  strict, in time     train only on AD/CVD cases whose month 16 was published before the first
                         Section 301 decision (September 2018), score the strict Section 301
                         population, whose rival exclusions use only cases started by the tariff.
  C  strict, reverse     train on Section 301 (published by March 2020), score AD/CVD cases whose
                         fall decision comes after that.
  ref in-domain         Section 301 scored by a model trained on other Section 301 chapters
                         (5-fold, grouped by chapter): how predictable it is from its own data.
Baselines: the training domain's historical recovery rate (what you would use with no model) and,
for reference only, the target domain's own rate, which no one knows in advance.
Weights: AD/CVD products weighted 1 / products in the case, Section 301 products 1 each.
Intervals: 90 percent, 2,000 resamples of chapters (Section 301) or investigation groups (AD/CVD)
of the scored products, with the fitted models held fixed: they cover which products are scored,
not how the model would change with other training cases or other tariff dates.

Usage:  python3 sec301_transfer_test.py      # after sec301_benchmark.py
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import recovery_lib as RL

H, LAG, CHINA = 16, 2, "5700"
rng = np.random.default_rng(0)
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
ev = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str}).drop_duplicates("document_number")
pubd = pd.to_datetime(ev.set_index("document_number").publication_date)
mg = pd.read_csv("events/adcvd_margins.csv").set_index("document_number").rate
FEAT = ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals", "log_rate", "rate_missing",
        "k_fall", "depth", "latest", "zero_months", "rush", "uv_change", "uv_missing"]


def mdate(m):
    return pd.Timestamp(year=m // 12, month=m % 12 + 1, day=1)


def build(pairs, stacks, b_of, tc_of, rate_of, group_of):
    f = pairs[pairs.category != "censored"].copy()
    f = f[f.fell_at.notna()].reset_index(drop=True)
    paths = RL.share_paths(stacks[stacks.set_index(["sid", "hs8"]).index.isin(
        pd.MultiIndex.from_frame(f[["sid", "hs8"]]))])
    hs = set(f.hs8)
    lo = min(b_of.values()) - 18
    hi = max(b_of.values()) + 8
    q = RL.load_raw(hs, lo, hi, qty=True)
    raw = {h: g[["cty", "m", "value"]] for h, g in q.groupby("hs8")}
    uvq = RL.one_unit_qty(q)
    rows = []
    for r in f.itertuples():
        b0, tc = int(b_of[r.sid]), tc_of[r.sid]
        pf = RL.pre_features(raw, r.hs8, b0, tc)
        if pf is None or (r.sid, r.hs8) not in paths:
            continue
        dm = b0 + int(r.fell_at) + LAG
        rate = rate_of(r.sid, dm)
        rows.append(dict(sid=r.sid, hs8=r.hs8, group=group_of(r), b=b0, decision=dm,
                         y=int(pd.notna(r.rec_at)), **pf,
                         log_rate=float(np.log1p(rate)) if pd.notna(rate) else 0.0,
                         rate_missing=float(pd.isna(rate)),
                         **RL.fall_features(paths[(r.sid, r.hs8)], r.bench, r.fell_at,
                                            RL.uv_change(uvq, r.hs8, b0, tc, int(r.fell_at)))))
    d = pd.DataFrame(rows)
    na = d[FEAT].isna().any(axis=1)
    if na.any():
        print(f"  dropped {na.sum()} rows with a missing feature")
    return d[~na].reset_index(drop=True)


# ---------------------------------------------------------------- AD/CVD side
ad_pairs = pd.read_csv("s301_adcvd_pairs_h16.csv", dtype={"hs8": str})
ad_pairs["hs8"] = ad_pairs.hs8.str.zfill(8)
ad_st = pd.read_parquet("panel/adcvd_stacks_real.parquet")


def ad_rate(sid, dm):
    cut = mdate(dm) - pd.Timedelta(days=1)
    ds = [d for d in ep.docs[sid].split(";") if pubd[d] <= cut]
    rs = [mg.get(d, np.nan) for d in ds]
    return np.nansum(rs) if any(pd.notna(x) for x in rs) else np.nan


AD = build(ad_pairs, ad_st, ep.b.to_dict(), ep.cty.to_dict(), ad_rate, lambda r: int(ep.cluster[r.sid]))
AD["w"] = 1.0 / AD.groupby("sid").sid.transform("size")
print(f"AD/CVD fallen products {len(AD):,}, cases {AD.sid.nunique()}, groups {AD.group.nunique()}, "
      f"came back {np.average(AD.y, weights=AD.w):.3f}")

# ---------------------------------------------------------------- Section 301 side
info = pd.read_csv("s301_stacks_info.csv")
s3_pairs = pd.read_csv("s301_pairs_real.csv", dtype={"hs8": str})
s3_st = pd.read_parquet("panel/s301_stacks.parquet")
s3_st = s3_st[s3_st["sample"] == "real"]
b301 = info.set_index("sid").b.to_dict()
list_of = info.set_index("sid").list.to_dict()
RAISE = 2019 * 12 + 5  # June 2019: first decision month after the May 10 increase to 25 percent


def s301_rate(sid, dm):
    return 10.0 if list_of[sid] == "List 3" and dm < RAISE else 25.0


S3 = build(s3_pairs, s3_st, {k: v for k, v in b301.items() if k < 100}, {k: CHINA for k in b301},
           s301_rate, lambda r: r.hs8[:2])
S3["w"] = 1.0
# strict population for test B: stacks whose exclusions use only cases started by the tariff date
s3s_pairs = pd.read_csv("s301_pairs_real_strict.csv", dtype={"hs8": str})
s3s_st = pd.read_parquet("panel/s301_stacks.parquet")
s3s_st = s3s_st[s3s_st["sample"] == "real, strict"]
S3s = build(s3s_pairs, s3s_st, {k: v for k, v in b301.items() if k > 200}, {k: CHINA for k in b301},
            s301_rate, lambda r: r.hs8[:2])
S3s["w"] = 1.0
print(f"Section 301 strict population: fallen products {len(S3s):,}, came back {S3s.y.mean():.3f}")
print(f"Section 301 fallen products {len(S3):,}, chapters {S3.group.nunique()}, "
      f"came back {S3.y.mean():.3f}")
print("\nfeature means (AD/CVD, Section 301):")
print(pd.DataFrame({"AD/CVD": np.average(AD[FEAT], axis=0, weights=AD.w), "Section 301": S3[FEAT].mean()},
                   index=FEAT).round(3).to_string())


# ---------------------------------------------------------------- models
def cv_pick(tr, grid, make):
    gkf = GroupKFold(n_splits=min(5, tr.group.nunique()))
    best, bp = None, None
    for p in grid:
        sc = []
        for a, b in gkf.split(tr, groups=tr.group):
            pr = make(p, tr.iloc[a])(tr.iloc[b])
            sc.append(brier_score_loss(tr.y.iloc[b], pr, sample_weight=tr.w.iloc[b]))
        if best is None or np.mean(sc) < best:
            best, bp = np.mean(sc), p
    return bp


def logit_make(C, tr):
    m = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=3000))
    m.fit(tr[FEAT], tr.y, logisticregression__sample_weight=tr.w)
    return lambda te: m.predict_proba(te[FEAT])[:, 1]


def gbm_make(n, tr):
    m = HistGradientBoostingClassifier(max_depth=2, learning_rate=0.05, max_iter=n, l2_regularization=1.0,
                                       min_samples_leaf=40, random_state=0)
    m.fit(tr[FEAT], tr.y, sample_weight=tr.w)
    return lambda te: m.predict_proba(te[FEAT])[:, 1]


MODELS = {"logistic": (logit_make, [0.01, 0.03, 0.1, 0.3, 1.0]), "boosting": (gbm_make, [25, 50, 100, 200])}


def score(te, preds, base_src, base_tgt):
    cl = te.group.unique()
    idx = {c: np.flatnonzero(te.group.values == c) for c in cl}
    out = []
    for name, p in [("training-domain rate", np.full(len(te), base_src)),
                    ("target's own rate (reference)", np.full(len(te), base_tgt))] + list(preds.items()):
        bs = brier_score_loss(te.y, p, sample_weight=te.w)
        auc = roc_auc_score(te.y, p, sample_weight=te.w) if np.unique(p).size > 1 else np.nan
        g, g2 = [], []
        p0, p1 = np.full(len(te), base_src), np.full(len(te), base_tgt)
        for _ in range(2000):
            ii = np.concatenate([idx[c] for c in rng.choice(cl, len(cl), replace=True)])
            bm = brier_score_loss(te.y.values[ii], p[ii], sample_weight=te.w.values[ii])
            g.append(brier_score_loss(te.y.values[ii], p0[ii], sample_weight=te.w.values[ii]) - bm)
            g2.append(brier_score_loss(te.y.values[ii], p1[ii], sample_weight=te.w.values[ii]) - bm)
        t = pd.qcut(pd.Series(p).rank(method="first"), 3, labels=False)
        cal = [(np.average(p[t == i], weights=te.w[t == i]), np.average(te.y[t == i], weights=te.w[t == i]))
               for i in range(3)]
        out.append(dict(model=name, brier=bs, auc=auc,
                        gain_vs_training_rate=brier_score_loss(te.y, p0, sample_weight=te.w) - bs,
                        lo=np.quantile(g, 0.05), hi=np.quantile(g, 0.95),
                        gain_vs_target_rate=brier_score_loss(te.y, p1, sample_weight=te.w) - bs,
                        lo_t=np.quantile(g2, 0.05), hi_t=np.quantile(g2, 0.95),
                        mean_pred=np.average(p, weights=te.w), realized=np.average(te.y, weights=te.w),
                        terciles="; ".join(f"{a:.2f}/{b:.2f}" for a, b in cal)))
    return pd.DataFrame(out)


def transfer(label, tr, te):
    tr, te = tr.reset_index(drop=True), te.reset_index(drop=True)
    preds = {}
    for name, (make, grid) in MODELS.items():
        par = cv_pick(tr, grid, make)
        preds[name] = make(par, tr)(te)
    s = score(te, preds, np.average(tr.y, weights=tr.w), np.average(te.y, weights=te.w))
    te.assign(**{f"pred_{k}": v for k, v in preds.items()}).to_csv(
        f"sec301_transfer_heldout_{label[0]}.csv", index=False)
    s.insert(0, "test", label)
    s.insert(1, "train_n", len(tr))
    s.insert(2, "test_n", len(te))
    print(f"\n[{label}] train {len(tr):,} products ({tr.sid.nunique()} cases), test {len(te):,}")
    print(s.drop(columns=["test", "train_n", "test_n"]).round(3).to_string(index=False))
    return s


R = []
R.append(transfer("A: all AD/CVD -> Section 301", AD, S3))
early = AD[AD.b + H + LAG < 2018 * 12 + 8]
R.append(transfer("B: AD/CVD published by Sep 2018 -> Section 301", early, S3s))
late_ad = AD[AD.decision >= 2020 * 12 + 2]
R.append(transfer("C: Section 301 -> AD/CVD decided from Mar 2020", S3.assign(w=1.0), late_ad))
# in-domain reference: Section 301 out-of-fold by chapter
oof = {k: np.zeros(len(S3)) for k in MODELS}
for a, b in GroupKFold(n_splits=5).split(S3, groups=S3.group):
    tr, te = S3.iloc[a].reset_index(drop=True), S3.iloc[b]
    for name, (make, grid) in MODELS.items():
        oof[name][b] = make(cv_pick(tr, grid, make), tr)(te)
s = score(S3, oof, S3.y.mean(), S3.y.mean())
s.insert(0, "test", "ref: Section 301 in-domain, by chapter")
s.insert(1, "train_n", len(S3))
s.insert(2, "test_n", len(S3))
print("\n[ref: Section 301 in-domain, 5 folds by chapter]")
print(s.drop(columns=["test", "train_n", "test_n"]).round(3).to_string(index=False))
R.append(s)
pd.concat(R).to_csv("sec301_transfer_test.csv", index=False)
# coefficients in each domain, for the comparison of what predicts recovery
co = {}
for lab, d in [("AD/CVD", AD), ("Section 301", S3)]:
    m = make_pipeline(StandardScaler(), LogisticRegression(C=cv_pick(d, MODELS["logistic"][1], logit_make),
                                                           max_iter=3000))
    m.fit(d[FEAT], d.y, logisticregression__sample_weight=d.w)
    co[lab] = m[-1].coef_[0]
co = pd.DataFrame(co, index=FEAT)
print("\nstandardized logistic coefficients by domain (positive = more likely back):")
print(co.round(3).to_string())
co.to_csv("sec301_transfer_coef.csv")
print("wrote sec301_transfer_test.csv, sec301_transfer_coef.csv")
