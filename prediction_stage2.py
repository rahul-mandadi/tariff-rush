"""Second decision point: once a targeted product has visibly fallen, can we tell whether it recovers?

prediction_test.py asks the hardest version of the question, on the day the duty starts, and
finds no reliable gain over the historical rates. A sourcing team gets two later looks: when the
fall shows up in the published trade data, and when the ITC votes on the final injury
determination a few months later. This script tests both.

Population: targeted product-country pairs from recovery_benchmark.py (20 percent fall rule,
complete 18-month follow-up) whose position fell within k = 0..6.
Target: recovered = back at or above the pre-case share for three months running by k = 18.

Decision points, each with the trade data a team could have seen (Census publishes a month's
trade about five weeks after it ends, so at decision month M the last visible month is M - 2):
  fall   decision month k_fall + 2, the first month the fall is visible. Visible data through
         k_fall. Case facts from notices published by then (the ITC vote is not yet known).
  ITC    decision month = month of the final-stage notice: the ITC's negative final
         determination, or the Commerce order that follows an affirmative vote. Visible data
         through that month - 2. Only pairs whose fall is visible by then and that are not yet
         visibly back. Episodes whose final stage is unresolved, or whose first order notice in
         the harvest comes after k = 12 (a later continuation notice, not the order itself), are
         left out.

Information sets compared on the ITC population:
  day 0      the 10 facts prediction_test.py uses (pre-case structure, preliminary rate, case type)
  + trade    adds what the published data show by the decision: month of the fall, deepest
             smoothed share so far and the latest one (both as a ratio to the pre-case level),
             share of months with no trade since the duty, the share in k -6..-1 against the
             pre-case level (any rush before the duty), and the targeted exporter's change in
             import unit value against rivals (same product, one reporting unit), with a
             missing flag
  + vote     adds whether the ITC found no injury

Baselines: the historical recovery rate in the training cases (same population), and the same
rate split by the ITC vote.
Models (on the fullest information set): L2 logistic regression; shallow gradient boosting
(depth 2, learning rate 0.05, strong L2); penalized Cox proportional hazards on months to
recovery with delayed entry at the decision, converted to a probability of recovery by k = 18.
Hyperparameters by 5-fold cross-validation grouped by investigation group inside the training
cases.
Validation as prediction_test.py: forward-chaining by year of k = 0; training cases only once
their month 18 had been published before the test year began. Every score episode-weighted.
Brier gains carry 90 percent intervals from 2,000 resamples of investigation groups.

Descriptive and predictive only: the ITC's vote rests on the import record itself.

Usage:  python3 prediction_stage2.py
"""
import glob
import json
import re

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

K_HI, LAG, MAX_K_FINAL = 18, 2, 12
rng = np.random.default_rng(0)
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
ev = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str}).drop_duplicates("document_number")
pubd = pd.to_datetime(ev.set_index("document_number").publication_date)
mon = lambda t: t.year * 12 + t.month - 1  # noqa: E731

# ---------------------------------------------------------------- final stage and its date
CASE = re.compile(r"\b([AC])-(\d{3})-(\d{3})\b")
allc = {d: {"-".join(m) for m in CASE.findall(open(f"events/raw/{d}.txt", errors="ignore").read())}
        for d in ev.document_number}
orders = ev[ev.stage == "order"].document_number.tolist()
order_cases = set().union(*[allc[d] for d in orders])
pub_itc = {}
for f in glob.glob("events/raw/itc_cache/*"):
    try:
        js = json.loads(open(f).read())
    except Exception:
        continue
    for r in (js.get("results", []) if isinstance(js, dict) else []):
        if r.get("document_number") and r.get("publication_date"):
            pub_itc[r["document_number"]] = pd.Timestamp(r["publication_date"])
pc = pd.read_csv("events/itc_check_by_country.csv", dtype={"cty": str})
key = {(r.ini, r.cty): r.verdict for r in pc.itertuples()}
fam_of = {(r.ini, r.cty): r.family for r in pc.itertuples()}
grp = pd.read_csv("events/itc_check.csv")
grp_ev = {(r.family, r.ini): str(r.evidence).split(";")[0] for r in grp.itertuples()}
neg_doc = pd.read_csv("events/itc_negative_audit.csv").set_index("sid").itc_doc

first = [min(pubd[d] for d in ds.split(";")) for ds in ep.docs]
stage, k_final, d_final = [], [], []
for s, (ds, b, f0) in enumerate(zip(ep.docs, ep.b, first)):
    own = set().union(*[allc.get(d, set()) for d in ds.split(";")])
    od = [pubd[o] for o in orders if allc[o] & own and pubd[o] > f0]
    if own & order_cases:
        st, dt = "order", (min(od) if od else None)
    else:
        v = key.get((ep.ini[s], ep.cty[s]))
        st = {"verified negative": "negative", "verified order": "order"}.get(v, "unresolved")
        dt = None
        if st == "negative" and s in neg_doc.index:
            dt = pub_itc.get(neg_doc[s])
        if st == "order":
            dt = pub_itc.get(grp_ev.get((fam_of.get((ep.ini[s], ep.cty[s])), ep.ini[s])))
    stage.append(st)
    k_final.append(mon(dt) - b if dt is not None else np.nan)
    d_final.append(dt)
ep["stage"], ep["k_final"], ep["d_final"] = stage, k_final, d_final

# ---------------------------------------------------------------- pairs and their share paths
pairs = pd.read_csv("recovery_pairs_real_fall20.csv", dtype={"hs8": str})
pairs["hs8"] = pairs.hs8.str.zfill(8)
pairs = pairs[(pairs.category != "censored") & pairs.fell_at.notna()].copy()
pairs["recovered"] = pairs.rec_at.notna().astype(int)
st = pd.read_parquet("panel/adcvd_stacks_real.parquet")
st = st[st.sid.isin(set(pairs.sid))]
tot = st.groupby(["sid", "hs8", "k"]).value.sum()
tg = st[st.treated].groupby(["sid", "hs8", "k"]).value.sum()
share = (tg / tot).fillna(0.0)
tv = st[st.treated].set_index(["sid", "hs8", "k"]).value
paths = {}
for (s, h), g in share.groupby(level=[0, 1]):
    g = g.droplevel([0, 1]).sort_index()
    paths[(s, h)] = (g, g.rolling(3, min_periods=3).mean(), tv.loc[(s, h)].sort_index())

# unit values: the targeted exporter and its rivals, products with one reporting unit throughout
files = sorted(glob.glob("panel/hs8/*.parquet"))
need = set(pairs.hs8)
cols = ["hs8", "cty", "ym", "value", "qty", "unit", "qty_ok"]
q = pd.concat([x[x.hs8.isin(need) & (x.value > 0)] for x in
               (pd.read_parquet(f, columns=cols) for f in files)])
q["m"] = q.ym.dt.year * 12 + q.ym.dt.month - 1
one_unit = q.groupby("hs8").unit.nunique()
okq = q[q.hs8.isin(one_unit[one_unit == 1].index) & q.qty_ok.fillna(False).astype(bool) & (q.qty > 0)]
uvq = {h: g[["cty", "m", "value", "qty"]] for h, g in okq.groupby("hs8")}

# pre-case structure, every country trading in k -18..-7 (as prediction_test.py)
raw = q[["hs8", "cty", "m", "value"]]
by_h = {h: g for h, g in raw.groupby("hs8")}


def pre_features(s, h):
    b0, tc = int(ep.b[s]), ep.cty[s]
    g = by_h.get(h)
    g = g[(g.m >= b0 - 18) & (g.m <= b0 - 7)] if g is not None else None
    if g is None or g.empty:
        return None
    cs = g.groupby("cty").value.sum()
    csh = cs / cs.sum()
    mm = g.groupby("m").value.sum()
    shm = g[g.cty == tc].groupby("m").value.sum().reindex(mm.index, fill_value=0) / mm
    x = (shm.index - b0).to_numpy(float)
    return dict(pre_share=float(csh.get(tc, 0.0)),
                pre_trend=float(np.polyfit(x, shm.to_numpy(float), 1)[0]) if len(x) > 2 else 0.0,
                log_pre_value=float(np.log1p(cs.get(tc, 0.0))),
                hhi=float((csh ** 2).sum()), n_rivals=float(np.log(max(len(cs) - 1, 1))))


def uv_change(s, h, kv):
    """Targeted exporter's log unit value change (k 0..kv vs -18..-7) minus the rivals'."""
    g = uvq.get(h)
    if g is None:
        return np.nan
    b0, tc = int(ep.b[s]), ep.cty[s]
    g = g[(g.m >= b0 - 18) & (g.m <= b0 + kv)]
    pre, post = g[g.m <= b0 - 7], g[g.m >= b0]
    def luv(x):
        return np.log(x.value.sum() / x.qty.sum()) if len(x) and x.qty.sum() > 0 else np.nan
    t = luv(post[post.cty == tc]) - luv(pre[pre.cty == tc])
    r = luv(post[post.cty != tc]) - luv(pre[pre.cty != tc])
    return t - r


mg = pd.read_csv("events/adcvd_margins.csv").set_index("document_number").rate
crit_doc = ev.set_index("document_number").critical_affirm.fillna(False).astype(bool)


def case_facts(s, upto):
    ds = [d for d in ep.docs[s].split(";") if pubd[d] <= upto]
    rates = [mg.get(d, np.nan) for d in ds]
    rate = np.nansum(rates) if any(pd.notna(r) for r in rates) else np.nan
    return dict(log_rate=float(np.log1p(rate)) if pd.notna(rate) else 0.0,
                rate_missing=float(pd.isna(rate)), crit=float(any(crit_doc.get(d, False) for d in ds)),
                both=float(ep.ad[s] and ep.cvd[s]), china=float(ep.cty[s] == "5700"))


def trade_features(s, h, bench, fell_at, kv):
    sh, sm, v = paths[(s, h)]
    post = sm.loc[0:kv]
    vv = v.reindex(range(0, kv + 1), fill_value=0)
    uvc = uv_change(s, h, kv)
    return dict(k_fall=float(fell_at), depth=float(post.min() / bench), latest=float(post.iloc[-1] / bench),
                zero_months=float((vv == 0).mean()), rush=float(sh.loc[-6:-1].mean() / bench),
                uv_change=0.0 if pd.isna(uvc) else float(np.clip(uvc, -3, 3)),
                uv_missing=float(pd.isna(uvc)))


rows = []
for r in pairs.itertuples():
    s, h, b0 = r.sid, r.hs8, int(ep.b[r.sid])
    pf = pre_features(s, h)
    if pf is None:
        continue
    base = dict(sid=s, hs8=h, cluster=r.cluster, year=b0 // 12, b=b0, recovered=r.recovered,
                rec_at=r.rec_at, stage=ep.stage[s], **pf)
    # day-0 case facts: notices on or before the first preliminary
    day0 = case_facts(s, first[s])
    # decision point "fall": month k_fall + 2, data through k_fall
    kv = int(r.fell_at)
    dt = pd.Timestamp(year=(b0 + kv + LAG) // 12, month=(b0 + kv + LAG) % 12 + 1, day=1)
    rows.append(dict(point="fall", entry=kv, **base, **{f"d0_{k}": x for k, x in day0.items()},
                     **case_facts(s, dt - pd.Timedelta(days=1)),
                     **trade_features(s, h, r.bench, r.fell_at, kv), itc_negative=np.nan))
    # decision point "ITC"
    kf = ep.k_final[s]
    if ep.stage[s] in ("order", "negative") and pd.notna(kf) and kf <= MAX_K_FINAL:
        kv = int(kf) - LAG
        visible_back = pd.notna(r.rec_at) and r.rec_at + 2 <= kv
        if r.fell_at <= kv and not visible_back:
            dt = ep.d_final[s]
            rows.append(dict(point="ITC", entry=kv - 2, **base, **{f"d0_{k}": x for k, x in day0.items()},
                             **case_facts(s, dt), **trade_features(s, h, r.bench, r.fell_at, kv),
                             itc_negative=float(ep.stage[s] == "negative")))
D = pd.DataFrame(rows)
D["w"] = 1.0 / D.groupby(["point", "sid"]).sid.transform("size")
_na = D.drop(columns=["rec_at", "itc_negative"]).isna().sum()
print("missing feature values:", _na[_na > 0].to_dict())
D = D.dropna(subset=list(_na[_na > 0].index)).reset_index(drop=True)  # one pair lacks k -6..-1
D["w"] = 1.0 / D.groupby(["point", "sid"]).sid.transform("size")

PRE = ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals"]
DAY0 = PRE + ["d0_log_rate", "d0_rate_missing", "d0_crit", "d0_both", "d0_china"]
TRADE = ["k_fall", "depth", "latest", "zero_months", "rush", "uv_change", "uv_missing"]
CASE_NOW = ["log_rate", "rate_missing", "crit", "both", "china"]
SETS = {"day 0": DAY0, "+ trade": PRE + CASE_NOW + TRADE, "+ vote": PRE + CASE_NOW + TRADE + ["itc_negative"]}


# ---------------------------------------------------------------- models
def cv_pick(tr, grid, make):
    gkf = GroupKFold(n_splits=min(5, tr.cluster.nunique()))
    best, bp = None, None
    for p in grid:
        sc = []
        for a, b in gkf.split(tr, groups=tr.cluster):
            pr = make(p, tr.iloc[a])(tr.iloc[b])
            sc.append(brier_score_loss(tr.recovered.iloc[b], pr, sample_weight=tr.w.iloc[b]))
        if best is None or np.mean(sc) < best:
            best, bp = np.mean(sc), p
    return bp


def logit(feat):
    def make(C, tr):
        m = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=3000))
        m.fit(tr[feat], tr.recovered, logisticregression__sample_weight=tr.w)
        return lambda te: m.predict_proba(te[feat])[:, 1]
    return make, [0.01, 0.03, 0.1, 0.3, 1.0]


def gbm(feat):
    def make(n, tr):
        m = HistGradientBoostingClassifier(max_depth=2, learning_rate=0.05, max_iter=n,
                                           l2_regularization=1.0, min_samples_leaf=40, random_state=0)
        m.fit(tr[feat], tr.recovered, sample_weight=tr.w)
        return lambda te: m.predict_proba(te[feat])[:, 1]
    return make, [25, 50, 100, 200]


def cox_fit(X, entry, t, ev_, w, lam):
    """Penalized Cox partial likelihood, Breslow ties, delayed entry, case weights."""
    times = np.unique(t[ev_ == 1])
    def nll(beta):
        eta = X @ beta
        r = np.exp(eta)
        ll, g = 0.0, -lam * beta
        for u in times:
            at = (entry < u) & (t >= u)
            d = (t == u) & (ev_ == 1)
            if not d.any():
                continue
            sw = (w[at] * r[at]).sum()
            dw = w[d].sum()
            ll += (w[d] * eta[d]).sum() - dw * np.log(sw)
            g += (w[d][:, None] * X[d]).sum(0) - dw * (w[at] * r[at]) @ X[at] / sw
        ll -= 0.5 * lam * beta @ beta
        return -ll, -g
    res = minimize(nll, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B")
    beta = res.x
    r = np.exp(X @ beta)
    h0 = {u: w[(t == u) & (ev_ == 1)].sum() / (w[(entry < u) & (t >= u)] * r[(entry < u) & (t >= u)]).sum()
          for u in times}
    return beta, pd.Series(h0).sort_index()


def cox(feat):
    def make(lam, tr):
        sc = StandardScaler().fit(tr[feat])
        X = sc.transform(tr[feat])
        t = np.where(tr.recovered == 1, tr.rec_at, K_HI).astype(float)
        beta, h0 = cox_fit(X, tr.entry.to_numpy(float), t, tr.recovered.to_numpy(), tr.w.to_numpy(), lam)
        def pred(te):
            r = np.exp(sc.transform(te[feat]) @ beta)
            H = np.array([h0[(h0.index > e) & (h0.index <= K_HI)].sum() for e in te.entry])
            return 1 - np.exp(-H * r)
        return pred
    return make, [1.0, 10.0, 100.0]


def run(pt, specs):
    d = D[D.point == pt].reset_index(drop=True)
    out, preds = [], []
    for Y in sorted(d.year.unique()):
        te = d[d.year == Y]
        tr = d[(d.b + K_HI + LAG) < Y * 12].reset_index(drop=True)
        if len(te) < 30 or tr.sid.nunique() < 40 or te.recovered.nunique() < 2:
            continue
        p = pd.DataFrame({"sid": te.sid.values, "cluster": te.cluster.values, "w": te.w.values,
                          "y": te.recovered.values, "year": Y})
        p["history"] = np.average(tr.recovered, weights=tr.w)
        if pt == "ITC":
            rate = {v: np.average(g.recovered, weights=g.w) for v, g in tr.groupby("itc_negative")}
            p["history by vote"] = te.itc_negative.map(rate).fillna(p["history"].iloc[0]).values
        for name, (make, grid) in specs.items():
            par = cv_pick(tr, grid, make)
            p[name] = make(par, tr)(te)
        preds.append(p)
        out.append(dict(point=pt, year=Y, train_episodes=tr.sid.nunique(), test_episodes=te.sid.nunique(),
                        test_pairs=len(te), recovered=np.average(te.recovered, weights=te.w)))
    return pd.DataFrame(out), pd.concat(preds)


def score(P, cols, ref):
    rows = []
    cl = P.cluster.unique()
    idx = {c: np.flatnonzero(P.cluster.values == c) for c in cl}
    for c in cols:
        bs = brier_score_loss(P.y, P[c], sample_weight=P.w)
        auc = roc_auc_score(P.y, P[c], sample_weight=P.w) if P[c].nunique() > 1 else np.nan
        row = dict(model=c, brier=bs, auc=auc)
        for rname in ref:
            gains = []
            for _ in range(2000):
                ii = np.concatenate([idx[k] for k in rng.choice(cl, len(cl), replace=True)])
                q_ = P.iloc[ii]
                gains.append(brier_score_loss(q_.y, q_[rname], sample_weight=q_.w)
                             - brier_score_loss(q_.y, q_[c], sample_weight=q_.w))
            g0 = brier_score_loss(P.y, P[rname], sample_weight=P.w) - bs
            row[f"gain_vs_{rname}"] = g0
            row[f"lo_vs_{rname}"], row[f"hi_vs_{rname}"] = np.quantile(gains, [0.05, 0.95])
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    for pt in ["fall", "ITC"]:
        d = D[D.point == pt]
        print(f"[{pt}] pairs {len(d):,}, episodes {d.sid.nunique()}, groups {d.cluster.nunique()}, "
              f"recovered (episode-weighted) {np.average(d.recovered, weights=d.w):.3f}")
    print("ITC population by vote:", D[D.point == "ITC"].groupby("stage").sid.nunique().to_dict())

    full = SETS["+ vote"]
    yrs_i, P_i = run("ITC", {"logit, day 0": logit(SETS["day 0"]), "logit, latest share only": logit(["latest"]),
                             "logit, + trade": logit(SETS["+ trade"]),
                             "logit, + vote": logit(full), "boosting, + vote": gbm(full),
                             "Cox, + vote": cox(full)})
    yrs_f, P_f = run("fall", {"logit, depth only": logit(["depth"]), "logit, day 0": logit(SETS["day 0"]),
                              "logit": logit(SETS["+ trade"]),
                              "boosting": gbm(SETS["+ trade"]),
                              "Cox": cox(SETS["+ trade"])})
    S_i = score(P_i, ["history", "history by vote", "logit, day 0", "logit, latest share only",
                      "logit, + trade", "logit, + vote",
                      "boosting, + vote", "Cox, + vote"], ["history", "history by vote",
                                                           "logit, latest share only"])
    S_f = score(P_f, ["history", "logit, depth only", "logit, day 0", "logit", "boosting", "Cox"],
                ["history", "logit, day 0"])
    S_i.insert(0, "point", "ITC")
    S_f.insert(0, "point", "fall")
    pd.set_option("display.width", 200)
    print("\ntest years:\n", pd.concat([yrs_f, yrs_i]).round(3).to_string(index=False))
    print("\nat the fall (pooled held-out):\n", S_f.round(4).to_string(index=False))
    print("\nat the ITC decision (pooled held-out):\n", S_i.round(4).to_string(index=False))
    by_year = (P_i.groupby("year").apply(lambda g: pd.Series(
        {c: brier_score_loss(g.y, g[c], sample_weight=g.w) for c in ["history", "history by vote",
                                                                        "logit, + vote", "boosting, + vote",
                                                                        "Cox, + vote"]}),
        include_groups=False))
    print("\nITC decision, Brier by test year:\n", by_year.round(3).to_string())
    # what the visible data already say at the ITC decision: share of pairs whose latest smoothed
    # share is back at the pre-case level, and their recovery rate
    di = D[D.point == "ITC"]
    for lab, g in [("latest >= pre-case", di[di.latest >= 1]), ("latest < pre-case", di[di.latest < 1])]:
        print(f"  {lab}: {g.w.sum() / di.w.sum():.3f} of pairs (episode-weighted), recovered "
              f"{np.average(g.recovered, weights=g.w):.3f}")
    for pt, feat in [("fall", SETS["+ trade"]), ("ITC", SETS["+ vote"])]:
        d = D[D.point == pt]
        mk, grid = logit(feat)
        C = cv_pick(d.reset_index(drop=True), grid, mk)
        m = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=3000))
        m.fit(d[feat], d.recovered, logisticregression__sample_weight=d.w)
        co = pd.Series(m[-1].coef_[0], index=feat).sort_values()
        print(f"\n[{pt}] full-sample logistic coefficients (standardized, C = {C}); positive = more likely back:")
        print(co.round(3).to_string())
        co.rename("coef").to_frame().assign(point=pt).to_csv(f"prediction_stage2_coef_{pt}.csv")
    pd.concat([S_f, S_i]).to_csv("prediction_stage2.csv", index=False)
    D.to_csv("prediction_stage2_features.csv", index=False)
    pd.concat([yrs_f, yrs_i]).to_csv("prediction_stage2_years.csv", index=False)
    pd.concat([P_f.assign(point="fall"), P_i.assign(point="ITC")]).to_csv("prediction_stage2_heldout.csv",
                                                                          index=False)
    print("wrote prediction_stage2.csv, prediction_stage2_years.csv, prediction_stage2_heldout.csv, "
          "prediction_stage2_features.csv")
