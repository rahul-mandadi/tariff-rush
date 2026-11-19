"""Appendix K of the report (model inputs, settings and checks), checked against saved outputs and code.

Each table is parsed from the report and compared cell by cell, with exact headers and row keys, so a
wrong row cannot hide behind a correct one elsewhere. Each figure quoted in prose is checked inside
the one paragraph that states it. The listed settings and input groups are compared with the code.

Run from the repository root:  python3 -m pytest tests -q
"""
import ast
import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
import modeling as M  # noqa: E402

RAW = open("FINAL_REPORT.md").read()
K = RAW[RAW.index("### Appendix K."):]


def flat(s):
    return " ".join(s.split())


def paragraph(text, phrase):
    """The one blank-line-separated block of text that contains phrase, flattened."""
    hits = [flat(b) for b in text.split("\n\n") if phrase in flat(b)]
    assert len(hits) == 1, (phrase, len(hits))
    return hits[0]


def table(caption):
    """Header and rows of the markdown table that follows the given caption, rows keyed by first cell."""
    rest = K[K.index(f"**{caption}.**"):]
    lines = [ln for ln in rest.split("\n\n")[1].splitlines() if ln.startswith("|")]
    cells = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    header, body = cells[0], cells[2:]
    keys = [r[0] for r in body]
    assert len(keys) == len(set(keys)), f"{caption}: duplicate row keys"
    return header, {r[0]: r[1:] for r in body}


def constant(path, name):
    """A module-level constant from a script, read without running the script. Simple expressions
    (range, a comprehension over the shared grids) are evaluated with only those names available."""
    src = open(path).read()

    def value(node):
        try:
            return ast.literal_eval(node)
        except ValueError:
            return eval(ast.get_source_segment(src, node), {"__builtins__": {}, "range": range, "list": list, "M": M})
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if getattr(t, "id", "") == name:
                    return value(node.value)
                if isinstance(t, ast.Tuple) and name in [getattr(e, "id", "") for e in t.elts]:
                    return value(node.value.elts[[e.id for e in t.elts].index(name)])
    raise KeyError(name)


def pts(x):
    return f"{100 * x:+.1f}".replace("+-", "-")


def iv(lo, hi):
    return f"[{100 * lo:.1f}, {100 * hi:.1f}]"


# ---------------------------------------------------------------- inputs and settings
def test_inputs_match_the_code():
    feat = constant("forecast/prediction_landmark.py", "FEAT")
    groups = [constant("forecast/feature_ladder.py", n) for n in ["A", "BB", "C", "CTX"]]
    assert sorted(feat) == sorted(sum(groups, [])) and len(feat) == len(set(feat)) == 23
    assert "The 23 inputs:" in flat(K)
    # the four bullets in the report follow the ladder's groups: 5 before the case, 5 case facts,
    # the latest share plus 8 fall inputs, 4 context inputs
    a, bb, c, ctx = groups
    assert a[:5] == ["pre_share", "pre_trend", "log_pre_value", "hhi", "n_rivals"]
    assert a[5:] == ["log_rate", "rate_missing", "crit", "both", "china"]
    assert bb == ["latest"] and len(c) == 8 and len(ctx) == 4
    assert constant("forecast/prediction_landmark.py", "LANDMARKS") == list(range(3, 15))
    assert constant("forecast/prediction_landmark.py", "LAG") == 2
    assert constant("forecast/prediction_landmark.py", "K_HI") == 18
    lead = paragraph(K, "one gradient boosting model per test year")
    assert "from month 3 to month 14" in lead and "two months before the checkpoint" in lead


def test_settings_match_the_code():
    b = M.boosting_model(100)
    settings = paragraph(K, "HistGradientBoostingClassifier")
    assert f"depth {b.max_depth}, learning rate {b.learning_rate}, L2 penalty {b.l2_regularization}" in settings
    assert f"at least {b.min_samples_leaf} rows per leaf" in settings
    g = M.BOOSTING_GRID
    assert f"from {g[0]}, {g[1]}, {g[2]} and {g[3]}" in settings
    c = M.LOGISTIC_GRID
    assert f"from {c[0]}, {c[1]}, {c[2]} and {c[3]}" in settings
    assert "5-fold cross-validation" in settings and "GroupKFold(n_splits=min(5" in open("modeling.py").read()

    caption = paragraph(K, "**Table K1.**")
    enet = constant("forecast/model_family_check.py", "ENET_GRID")
    assert sorted({r for _, r in enet}) == [0.25, 0.5, 0.75] and sorted({C for C, _ in enet}) == sorted(c)
    assert "L1 share 0.25, 0.5 or 0.75" in caption
    forest = constant("forecast/model_family_check.py", "FOREST_GRID")
    shown = ", ".join(f"({'unlimited' if d is None else d}, {leaf})" for d, leaf in forest[:-1])
    d, leaf = forest[-1]
    shown += f" or ({'unlimited' if d is None else d}, {leaf})"
    assert shown in caption, shown
    assert "n_estimators=300" in open("forecast/model_family_check.py").read() and "300 trees" in caption
    assert "random_state=0))  # saga shuffles rows" in open("forecast/model_family_check.py").read()


def test_the_rule_is_the_one_in_the_scope_contract():
    scope = flat(open("docs/SCOPE.md").read())
    assert "boosting stays the reported ranking whatever the result" in scope
    caption = paragraph(K, "**Table K1.**")
    assert "boosting stays the reported ranking whatever the result" in caption
    assert "reported under Limitations" in caption


# ---------------------------------------------------------------- Table K1, model families
def test_table_k1_model_families():
    T = pd.read_csv("results/model_family_check.csv")
    T = T[T.capacity == 0.2].set_index("model")
    header, rows = table("Table K1")
    assert header == ["model", "not recovered, reviewed", "minus latest share", "minus boosting", "Brier", "AUC"]
    names = {"boosting (reported)": "boosting", "random forest": "random forest", "logistic": "logistic",
             "elastic net": "elastic net", "latest share": "latest share"}
    assert list(rows) == list(names)
    for shown, name in names.items():
        r = T.loc[name]
        want = [f"{100 * r.precision:.1f}%",
                "" if name == "latest share" else f"{pts(r.minus_latest_share)} "
                f"{iv(r.minus_latest_share_lo, r.minus_latest_share_hi)}",
                "" if name == "boosting" else f"{pts(r.minus_boosting)} {iv(r.minus_boosting_lo, r.minus_boosting_hi)}",
                "" if name == "latest share" else f"{r.brier:.3f}",
                "" if name == "latest share" else f"{r.auc:.3f}"]
        assert rows[shown] == want, (shown, rows[shown], want)


def test_table_k1_paragraph():
    T = pd.read_csv("results/model_family_check.csv")
    T = T[T.capacity == 0.2].set_index("model")
    text = paragraph(K, "All four families beat the latest share")
    models = ["boosting", "random forest", "logistic", "elastic net"]
    assert (T.loc[models].minus_latest_share_lo > 0).all()
    others = T.loc[["random forest", "logistic", "elastic net"]]
    assert ((others.minus_boosting_lo < 0) & (others.minus_boosting_hi > 0)).all()
    assert "all three intervals against boosting include zero" in text

    S = pd.read_csv("results/model_family_check_settings.csv")
    S["setting"] = S.setting.map(ast.literal_eval)
    logit = S[S.model == "logistic"].setting
    enet = S[S.model == "elastic net"].setting
    assert len(logit) == len(enet) == 6
    assert (logit == max(M.LOGISTIC_GRID)).all() and "C = 1.0" in text and "in all six test years" in text
    assert sum(C == max(M.LOGISTIC_GRID) for C, _ in enet) == 5 and "C = 1.0 in five years" in text
    assert all(r == 0.75 for _, r in enet) and "0.75, in all six" in text


# ---------------------------------------------------------------- Table K2 and permutation importance
def test_table_k2_feature_ladder():
    L = pd.read_csv("results/feature_ladder.csv")
    L = L[L.model == "boosting"].reset_index(drop=True)
    header, rows = table("Table K2")
    assert header == ["inputs", "inputs, without context", "not recovered, reviewed", "Brier", "AUC",
                      "change from step before"]
    shown = ["the case and before the case", "plus the latest share", "plus the fall so far (reported)",
             "plus other countries' pickup", "plus rivals already under a duty"]
    assert list(rows) == shown and len(L) == len(shown)
    for i, r in L.iterrows():
        want = [str(r.inputs), f"{100 * r.precision20:.1f}%", f"{r.brier:.3f}", f"{r.auc:.3f}",
                "" if pd.isna(r.vs_prev) else f"{pts(r.vs_prev)} {iv(r.vs_prev_lo, r.vs_prev_hi)}"]
        assert rows[shown[i]] == want, (shown[i], rows[shown[i]], want)
    assert L.loc[2, "inputs"] + 4 == 23, "the reported step plus the four context inputs is the 23-input model"


def test_permutation_paragraph():
    I = pd.read_csv("results/model_importance.csv").set_index("feature").sort_values("brier_increase", ascending=False)
    text = paragraph(K, "Shuffling one input at a time")
    assert "20 times" in text and constant("forecast/model_explain.py", "REPEATS") == 20
    top = I.iloc[0]
    assert I.index[0] == "latest"
    assert f"{top.brier_increase:.3f} [{top.lo:.3f}, {top.hi:.3f}] without the latest share" in text
    assert I.index[1:4].tolist() == ["rush", "log_pre_value", "hhi"]
    r = I.loc["rush"]
    assert f"{r.brier_increase:.3f} for the pre-case rush ({r.lo:.3f} to {r.hi:.3f})" in text
    assert f"{I.loc['log_pre_value'].brier_increase:.3f} for the pre-case import value" in text
    assert f"{I.loc['hhi'].brier_increase:.3f} for market concentration" in text


# ---------------------------------------------------------------- calibration
def test_calibration_paragraph():
    C = pd.read_csv("results/model_recalibration.csv")
    A = C[C["sample"] == "all"].set_index("model")
    raw, cal = A.loc["raw"], A.loc["calibrated"]
    text = paragraph(K, "**Calibration.**")
    assert f"{100 * raw.mean_pred:.1f} percent chance of recovering" in text
    assert f"and {100 * raw.realized:.1f} percent recovered" in text
    assert f"understates recovery by {-100 * raw.gap:.1f} points (90 percent interval {-100 * raw.gap_hi:.1f} " \
           f"to {-100 * raw.gap_lo:.1f})" in text
    assert f"to {-100 * cal.gap:.1f} points ({-100 * cal.gap_hi:.1f} to {-100 * cal.gap_lo:.1f})" in text
    assert 0.4 < cal.gap / raw.gap < 0.6, "the text says about half"
    assert f"Brier score by {cal.brier_gain_vs_raw:.3f} ({cal.brier_gain_lo:.3f} to {cal.brier_gain_hi:.3f})" in text
    small = C[C["sample"] == "smallest third"].set_index("model")
    assert f"{-100 * small.loc['raw', 'gap']:.1f} points raw and {-100 * small.loc['calibrated', 'gap']:.1f} " \
           f"after recalibration" in text
    thirds = C[C["sample"].str.endswith(" third") & (C.model == "raw")].set_index("sample").gap
    assert (-thirds).idxmax() == "smallest third", "the text says the gap is largest for the smallest third"


def test_recalibration_keeps_every_month_4_review_list():
    """Same calendar-month queues, same reviewed shares at every capacity, raw against recalibrated."""
    H = pd.read_csv("results/model_recalibration_heldout.csv")
    H["queue"] = H.b + 4
    for cap in [0.1, 0.2, 0.3]:
        for _, g in H.groupby("queue"):
            a = M.review_shares(1 - g.raw.to_numpy(), cap)
            b = M.review_shares(1 - g.calibrated.to_numpy(), cap)
            assert np.allclose(a, b), (cap, g.queue.iloc[0])


# ---------------------------------------------------------------- Table K3, the fall threshold
def test_table_k3_fall_threshold():
    header, rows = table("Table K3")
    assert header == ["fall threshold", "fell and not back", "fake date", "back within 18 months of falling",
                      "fake date"]
    shown = {"below 90 percent": 10, "below 80 percent (reported)": 20, "below 70 percent": 30}
    assert list(rows) == list(shown)
    for label, fall in shown.items():
        r = pd.read_csv(f"results/recovery_benchmark_fall{fall}.csv").set_index(["sample", "measure"]).value
        want = [f"{100 * (r[(s, 'not recovered')] + r[(s, 'exited')]):.0f}%" for s in ["real", "placebo"]]
        want += [f"{100 * r[(s, 'KM recovered by 18')]:.0f}%" for s in ["real", "placebo"]]
        assert rows[label] == [want[0], want[1], want[2], want[3]], (label, rows[label], want)


def test_table_3_rounding_note():
    r = pd.read_csv("results/recovery_benchmark_fall20.csv").set_index(["sample", "measure"]).value
    note = paragraph(RAW, "**Table 3.**")
    assert f"sum to {100 * (r[('real', 'not recovered')] + r[('real', 'exited')]):.1f} percent" in note


# ---------------------------------------------------------------- notes outside the appendix
def test_quantity_estimates_and_interval_note():
    q = pd.read_csv("results/adcvd_stacked_qty.csv")
    q = q[(q.contrast == "after (0..18) vs reference (-18..-13)") & q["sample"].str.startswith("real, complete follow-up")]
    est = q.set_index("outcome").est
    qty, val = est["log quantity, positive only"], est["log value, positive only"]
    text = paragraph(RAW, "months with trade show quantity falling")
    assert f"quantity falling {-qty:.3f} log points and value {-val:.3f}" in text
    se = q.set_index("outcome").se
    for o in ["log quantity, positive only", "log value, positive only"]:
        assert est[o] - 1.96 * se[o] < 0 < est[o] + 1.96 * se[o], "the text says both 95 percent intervals include zero"
    assert qty <= val and est["PPML quantity, zeros in"] <= est["PPML value, zeros in"], \
        "the text says the quantity estimate is at least as negative as the value estimate"
    note = paragraph(RAW, "Table 2 gives standard errors")
    assert "Appendix J use 95 percent intervals, and all others are 90 percent" in note
    assert "[.025,.975]" in open("research/rush_2018/evaluate_rush.py").read()
    assert "1.96" in open("slides/fig_stacked.py").read()


def test_appendix_i_code_list_names_real_files():
    block = paragraph(RAW, "All code is in the repository.")
    paths = re.findall(r"`([\w./]+\.py)`", block)
    assert len(paths) > 30
    missing = [p for p in paths if not os.path.exists(p)]
    assert not missing, missing
    steps = constant("run_all.py", "STEPS")
    for s in ["forecast/model_family_check.py", "forecast/feature_ladder.py", "forecast/model_explain.py",
              "forecast/model_calibration.py", "forecast/model_recalibration.py"]:
        assert s in steps, s
    for s in ["research/rush_2018/evaluate_rush.py", "measure/coverage_share.py", "events/build_release_calendar.py"]:
        assert not any(x.split()[0] == s for x in steps), f"{s} is said to run separately"
