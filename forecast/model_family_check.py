"""Check the month-4 ranking with two more model families: elastic-net logistic regression and a random forest.

The rule was fixed before this ran (docs/SCOPE.md, change log, 2026-11-18): boosting stays the
reported ranking whatever the result; these models are a check only. Each family gets the same
inputs, training years and grouped tuning as the current models, and is scored on the same
held-out month-4 lists. The script first refits logistic and boosting and stops unless they
reproduce prediction_landmark_heldout.csv, so all four models see exactly the same data.

Reads:  panel/landmark_features.parquet, prediction_landmark_heldout.csv
Writes: model_family_check.csv, model_family_check_heldout.csv, model_family_check_settings.csv
Run:    python3 forecast/model_family_check.py      (after forecast/prediction_landmark.py)
"""
import ast
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, ".")  # the shared modules are at the repo root
import modeling as M  # noqa: E402

warnings.filterwarnings("ignore", category=ConvergenceWarning)
K_HI, LAG, L_EVAL, CAPS, B = 18, 2, 4, [0.1, 0.2, 0.3], 1000
rng = np.random.default_rng(0)


def landmark_features():
    """The month-4 model's inputs, read from forecast/prediction_landmark.py so they cannot drift."""
    for node in ast.parse(open("forecast/prediction_landmark.py").read()).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "FEAT":
            return ast.literal_eval(node.value)
    raise KeyError("FEAT")


FEAT = landmark_features()

# ---------------------------------------------------------------- the two new families
ENET_GRID = [(C, r) for C in M.LOGISTIC_GRID for r in (0.25, 0.5, 0.75)]   # strength, share of L1
FOREST_GRID = [(6, 40), (10, 40), (None, 40), (None, 80)]                  # max depth, min rows per leaf


def elastic_net(features):
    def make(setting, tr):
        C, l1_ratio = setting
        m = make_pipeline(StandardScaler(), LogisticRegression(penalty="elasticnet", solver="saga", C=C,
                                                               l1_ratio=l1_ratio, max_iter=5000, tol=1e-4,
                                                               random_state=0))  # saga shuffles rows
        m.fit(tr[features], tr.y, logisticregression__sample_weight=tr.w)
        return lambda te: m.predict_proba(te[features])[:, 1]
    return make


def random_forest(features):
    def make(setting, tr):
        depth, leaf = setting
        m = RandomForestClassifier(n_estimators=300, max_depth=depth, min_samples_leaf=leaf, n_jobs=-1,
                                   random_state=0)
        m.fit(tr[features], tr.y, sample_weight=tr.w)
        return lambda te: m.predict_proba(te[features])[:, 1]
    return make


MODELS = {"logistic": (M.logistic, M.LOGISTIC_GRID), "boosting": (M.boosting, M.BOOSTING_GRID),
          "elastic net": (elastic_net, ENET_GRID), "random forest": (random_forest, FOREST_GRID)}

# ---------------------------------------------------------------- the same forward-in-time loop
D = pd.read_parquet("panel/landmark_features.parquet")
D["hs8"] = D.hs8.astype(str).str.zfill(8)
preds, chosen = [], []
for Y in sorted(D.year.unique()):
    te = D[D.year == Y]
    tr = D[(D.b + K_HI + LAG) < Y * 12].reset_index(drop=True)
    if te.sid.nunique() < 5 or tr.sid.nunique() < 40 or te.y.nunique() < 2:
        continue
    p = te[["sid", "hs8", "cluster", "year", "b", "L", "y", "latest"]].copy()
    p["w"] = 1.0 / te.groupby(["sid", "L"]).sid.transform("size")
    for name, (maker, grid) in MODELS.items():
        make = maker(FEAT)
        setting = M.tune(tr, grid, make)
        p[name] = make(setting, tr)(te)
        chosen.append(dict(year=Y, model=name, setting=str(setting)))
    preds.append(p)
    print(f"  test {Y}: {te.sid.nunique()} cases, {len(te):,} rows; chosen "
          + ", ".join(f"{c['model']} {c['setting']}" for c in chosen if c["year"] == Y), flush=True)
P = pd.concat(preds, ignore_index=True)
P.to_csv("model_family_check_heldout.csv", index=False)

ref = pd.read_csv("prediction_landmark_heldout.csv", dtype={"hs8": str})
assert len(ref) == len(P)
for name in ["logistic", "boosting"]:
    diff = np.abs(ref[name].to_numpy() - P[name].to_numpy()).max()
    assert diff < 1e-9, f"{name} differs from prediction_landmark_heldout.csv by {diff}"
print("check passed: logistic and boosting reproduce prediction_landmark_heldout.csv")

# ---------------------------------------------------------------- month-4 scoring, as review_queue.py
G = P[P.L == L_EVAL].reset_index(drop=True)
G["queue"] = G.b + L_EVAL
SCORES = {"latest share": -G.latest.to_numpy(), **{n: 1 - G[n].to_numpy() for n in MODELS}}


def measures(g, idx):
    down = 1 - g.y.to_numpy()
    out = {}
    for name, score in SCORES.items():
        s = score[idx]
        row = {}
        for cap in CAPS:
            r = np.zeros(len(g))
            for _, ix in g.groupby("queue").indices.items():
                r[ix] = M.review_shares(s[ix], cap)
            row[cap] = ((r * down).sum() / r.sum(), (r * down).sum() / down.sum())
        if name != "latest share":
            row["brier"] = brier_score_loss(g.y, g[name], sample_weight=g.w)
            row["auc"] = roc_auc_score(g.y, g[name], sample_weight=g.w)
        out[name] = row
    return out


point = measures(G, np.arange(len(G)))
cl = G.cluster.unique()
gi = {c: np.flatnonzero(G.cluster.to_numpy() == c) for c in cl}
boot = []
for _ in range(B):
    idx = np.concatenate([gi[c] for c in rng.choice(cl, len(cl), replace=True)])
    boot.append(measures(G.iloc[idx].reset_index(drop=True), idx))


def r90(x):
    return np.quantile(x, [0.05, 0.95])


rows = []
for name in ["boosting", "logistic", "elastic net", "random forest", "latest share"]:
    for cap in CAPS:
        prec, capt = point[name][cap]
        bp = np.array([b[name][cap][0] for b in boot])
        row = dict(model=name, capacity=cap, precision=prec, lo=r90(bp)[0], hi=r90(bp)[1], capture=capt)
        for base in ["latest share", "boosting"]:
            if name != base:
                d = bp - np.array([b[base][cap][0] for b in boot])
                row[f"minus_{base.replace(' ', '_')}"] = prec - point[base][cap][0]
                row[f"minus_{base.replace(' ', '_')}_lo"], row[f"minus_{base.replace(' ', '_')}_hi"] = r90(d)
        if name != "latest share":
            row["brier"], row["auc"] = point[name]["brier"], point[name]["auc"]
            bb = np.array([b[name]["brier"] for b in boot])
            ba = np.array([b[name]["auc"] for b in boot])
            row["brier_lo"], row["brier_hi"] = r90(bb)
            row["auc_lo"], row["auc_hi"] = r90(ba)
        rows.append(row)
T = pd.DataFrame(rows)
T.to_csv("model_family_check.csv", index=False)
pd.set_option("display.width", 250)
print(f"\nmonth 4, held out: {len(G)} relationships, {G.sid.nunique()} cases, {G.cluster.nunique()} groups")
print(T.round(3).to_string(index=False))
print("\nchosen settings by test year:")
pd.DataFrame(chosen).to_csv("model_family_check_settings.csv", index=False)
print(pd.DataFrame(chosen).pivot(index="year", columns="model", values="setting").to_string())
print("wrote model_family_check.csv, model_family_check_heldout.csv, model_family_check_settings.csv")
