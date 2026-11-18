"""The methodology study (docs/SCOPE.md section 5): its results agree with the existing pipeline and
with each other. Reads only committed result files.

Run from the repository root:  python3 -m pytest tests -q
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
import sys  # noqa: E402

sys.path.insert(0, ROOT)
import modeling as M  # noqa: E402


def _fn(path, name, ns=None):
    """Load one function from a script without running the script."""
    src = open(path).read()
    start = src.index(f"def {name}(")
    end = src.index("\ndef ", start + 1) if "\ndef " in src[start + 1:] else len(src)
    nxt = src.find("\n\n\n", start)
    ns = {"np": np} if ns is None else ns
    exec(src[start:nxt if nxt > 0 else end], ns)
    return ns[name]


def test_review_rule_is_the_same_in_every_script():
    # the shared rule (modeling.py) against the one copy kept on purpose: frozen_forecast_check.py,
    # whose code is part of the frozen forecast's record and is not edited
    shared = M.review_shares
    frozen = _fn("frozen_forecast_check.py", "reviewed")
    r = np.random.default_rng(1)
    for _ in range(200):
        n = int(r.integers(1, 30))
        s = np.round(r.random(n), 1)  # rounding makes ties
        cap = float(r.choice([0.05, 0.1, 0.2, 0.3, 0.5]))
        want = shared(s, cap)
        assert np.allclose(frozen(s, cap), want)
        assert np.allclose(shared(s, cap, np.ones(n)), want)  # unweighted equals weights of one
        assert np.isclose(want.sum(), cap * n)  # exactly the capacity is reviewed


def test_ladder_step_c_is_the_current_model():
    lad = pd.read_csv("feature_ladder_heldout.csv")
    ref = pd.read_csv("prediction_landmark_heldout.csv")
    assert len(lad) == len(ref)
    for m in ["boosting", "logistic"]:
        assert np.abs(lad[f"c + how the fall has gone | {m}"] - ref[m]).max() < 1e-9
    T = pd.read_csv("feature_ladder.csv").set_index(["model", "step"])
    q = pd.read_csv("review_queue_eval.csv")
    q = q[(q.weighting == "relationship") & (q.capacity == 0.2) & (q.measure == "precision")].set_index("ranking").value
    assert abs(T.precision20[("boosting", "c + how the fall has gone")] - q["forecast (boosting)"]) < 1e-12
    assert abs(T.precision20[("logistic", "c + how the fall has gone")] - q["logistic"]) < 1e-12
    assert len(T) == 10 and T.inputs.groupby("model").apply(lambda x: x.is_monotonic_increasing).all()


def test_capacity_curve_agrees_with_review_queue_and_its_ceiling():
    C = pd.read_csv("review_queue_capacity.csv")
    q = pd.read_csv("review_queue_eval.csv")
    q = q[(q.weighting == "relationship") & (q.measure == "precision")]
    for cap in [0.1, 0.2, 0.3]:
        for name in ["forecast (boosting)", "latest share", "historical rate"]:
            got = C[(C.capacity == cap) & (C.ranking == name)].precision.iloc[0]
            want = q[(q.capacity == cap) & (q.ranking == name)].value.iloc[0]
            assert abs(got - want) < 1e-12, (cap, name)
    assert (C.capture <= C.ceiling + 1e-12).all()
    hist = C[C.ranking == "historical rate"]
    assert np.allclose(hist.precision, hist.not_back)  # a random order finds the base rate


def test_checkpoints_month_4_matches_the_capacity_curve():
    K = pd.read_csv("review_queue_checkpoints.csv")
    C = pd.read_csv("review_queue_capacity.csv")
    a = K[K.L == 4].set_index("ranking").precision
    b = C[C.capacity == 0.2].set_index("ranking").precision
    assert np.allclose(a.sort_index(), b.sort_index())
    assert sorted(K.L.unique()) == [4, 6, 8]


def test_importance_ranges_and_leading_input():
    I = pd.read_csv("model_importance.csv")
    assert I.iloc[0].feature == "latest"
    assert (I.lo <= I.brier_increase + 1e-12).all() and (I.brier_increase <= I.hi + 1e-12).all()


def test_calibration_matches_the_held_out_predictions():
    H = pd.read_csv("prediction_landmark_heldout.csv")
    g = H[H.L == 4]
    C = pd.read_csv("model_calibration.csv").set_index("sample")
    assert abs(C.mean_pred["all"] - np.average(g.boosting, weights=g.w)) < 1e-12
    assert abs(C.realized["all"] - np.average(g.y, weights=g.w)) < 1e-12
    bins = C[C.index.str.startswith("all: bin")]
    assert len(bins) == 5 and bins.relationships.sum() == len(g)


def test_recalibration_changes_probabilities_not_the_ranking():
    R = pd.read_csv("model_recalibration_heldout.csv")
    H = pd.read_csv("prediction_landmark_heldout.csv")
    h = H[H.L == 4].reset_index(drop=True)
    assert len(R) == len(h) and np.abs(R.raw.to_numpy() - h.boosting.to_numpy()).max() < 1e-12
    for _, g in R.groupby("year"):  # order preserved within each test year
        a, b = g.raw.rank(method="min").to_numpy(), g.calibrated.rank(method="min").to_numpy()
        assert (a == b).all()
    rev = M.review_shares
    R["queue"] = R.b + 4
    for col in ["raw", "calibrated"]:
        r = np.zeros(len(R))
        for _, ix in R.groupby("queue").indices.items():
            r[ix] = rev(1 - R[col].to_numpy()[ix], 0.2)
        R["r_" + col] = r
    assert np.allclose(R.r_raw, R.r_calibrated)


def test_frozen_forecast_is_intact_and_untouched_by_training():
    import hashlib
    import json
    meta = json.load(open("frozen_forecast_meta.json"))
    assert hashlib.sha256(open("frozen_forecast.csv", "rb").read()).hexdigest() == meta["sha256"]
    F = pd.read_csv("frozen_forecast.csv", dtype={"hs8": str})
    assert len(F) == meta["relationships"] and F.p_not_back.between(0, 1).all()
    # every queue is ranked 1..n, and none of its relationships has a known outcome in the training pairs
    for _, g in F.groupby("decision_month"):
        assert g.rank_forecast.min() == 1 and g.rank_forecast.max() <= len(g)
    H = pd.read_csv("prediction_landmark_heldout.csv", dtype={"hs8": str})
    assert not set(zip(F.sid, F.hs8.str.zfill(8))) & set(zip(H.sid, H.hs8.str.zfill(8)))


def test_model_family_check_matches_the_review_queue():
    """The four-family check (forecast/model_family_check.py) scores boosting and the latest share exactly
    as review_queue.py does, and by the rule fixed before it ran boosting stays the reported ranking:
    no new family beats it at 20 percent with a 90 percent interval above zero."""
    T = pd.read_csv("model_family_check.csv").set_index(["model", "capacity"])
    E = pd.read_csv("review_queue_eval.csv")
    E = E[(E.weighting == "relationship") & (E.measure == "precision")].set_index(["ranking", "capacity"]).value
    for cap in [0.1, 0.2, 0.3]:
        assert abs(T.loc[("boosting", cap), "precision"] - E[("forecast (boosting)", cap)]) < 1e-9
        assert abs(T.loc[("latest share", cap), "precision"] - E[("latest share", cap)]) < 1e-9
    for name in ["elastic net", "random forest"]:
        assert not T.loc[(name, 0.2), "minus_boosting_lo"] > 0, name
