"""Every headline number in the report, README and handoff must match the CSV it comes from.

Run from the repository root:  python3 -m pytest tests -q
"""
import os

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
REPORT = open("FINAL_REPORT.md").read()
README = open("README.md").read()
HANDOFF = open("HANDOFF.md").read()
pct = lambda x: f"{100 * x:.0f}"  # noqa: E731


def flat(s):
    return " ".join(s.split())


@pytest.fixture(scope="module")
def docs():
    return {"report": flat(REPORT), "readme": flat(README), "handoff": flat(HANDOFF)}


def test_outcome_shares(docs):
    r = pd.read_csv("recovery_benchmark_fall20.csv").set_index(["sample", "measure"]).value
    real = [pct(r[("real", k)]) for k in ["no fall", "recovered", "not recovered", "exited"]]
    fake = [pct(r[("placebo", k)]) for k in ["no fall", "recovered", "not recovered", "exited"]]
    assert real == ["25", "17", "42", "16"] and fake == ["49", "30", "18", "3"]
    t = docs["report"]
    for v, row in zip(real, ["did not fall", "fell, came back", "fell, still down", "fell, no imports 13-18"]):
        assert f"| {row} | {v}% [" in t, row
    assert "25 / 17 / 42 / 16" in docs["handoff"] and "49 / 30 / 18 / 3" in docs["handoff"]


def test_table3_rows(docs):
    t = docs["report"]
    d0 = pd.read_csv("prediction_test.csv").set_index("year").loc["pooled"]
    row0 = f"| duty starts | 384 ({int(d0.test_episodes)}) | {d0.brier_benchmark:.3f} | logistic, {d0.brier_model:.3f} |"
    assert row0 in t, row0
    lm = pd.read_csv("prediction_landmark.csv").set_index("L").loc[4]
    cnt = pd.read_csv("prediction_landmark_counts.csv").set_index("L").loc[4]
    row4 = (f"| month 4 | {cnt.cases} ({int(lm.cases)}) | {lm.brier_history:.3f} | boosting, {lm.brier_boosting:.3f} | "
            f"{lm.gain_boosting:.3f} [{lm.lo_boosting:.3f}, {lm.hi_boosting:.3f}] | {lm.auc_boosting:.2f} |")
    assert row4 in t, row4
    s2 = pd.read_csv("prediction_stage2.csv").set_index(["point", "model"])
    m, h = s2.loc[("ITC", "logit, + vote")], s2.loc[("ITC", "history")]
    yrs = pd.read_csv("prediction_stage2_years.csv")
    scored = int(yrs[yrs.point == "ITC"].test_episodes.sum())
    rowi = (f"| ITC final vote | 333 ({scored}) | {h.brier:.3f} | logistic, {m.brier:.3f} | "
            f"{m.gain_vs_history:.3f} [{m.lo_vs_history:.3f}, {m.hi_vs_history:.3f}] | {m.auc:.2f} |")
    assert rowi in t, rowi


def test_monthly_forecast_claims(docs):
    lm = pd.read_csv("prediction_landmark.csv").set_index("L")
    assert pct(lm.loc[4, "auc_boosting"]) == "78" and pct(lm.loc[4, "auc_logistic"]) == "75"
    assert pct(lm.loc[5, "auc_boosting"]) == "81"
    lo, hi = lm.loc[4:6, "over_share_boosting"].min(), lm.loc[4:6, "over_share_boosting"].max()
    assert f"{lo:.3f}" == "0.012" and f"{hi:.3f}" == "0.016"
    assert (lm.loc[4:6, "lo_os_boosting"] > 0).all(), "boosting's edge over the share model must be supported in months 4 to 6"
    assert (lm.loc[4:6, "lo_os_logistic"] <= 0).any(), "the text says logistic's edge includes zero"
    for k in ["report", "readme"]:
        assert "78 percent of pairs" in docs[k] and "81 percent" in docs[k]
    assert "0.012 to 0.016" in docs["report"]


def test_decision_value_support(docs):
    j = pd.read_csv("decision_value_joint.csv").set_index("point")
    assert j.loc["ITC final vote", "supported_thresholds"] == "0.75, 0.85"
    assert j.loc["fall first visible", "supported_thresholds"] == "0.65, 0.70"
    assert j.loc["duty starts", "supported_thresholds"] == "none"
    assert "0.75 and 0.85" in docs["report"] and "0.65 and 0.70" in docs["report"]
    assert "0.75 and 0.85" in docs["readme"] and "0.75 and 0.85" in docs["handoff"]
    for stale in ["0.25 to 0.90", "fixed in advance"]:
        assert stale not in docs["report"] and stale not in docs["readme"], stale


def test_section301_and_pooling(docs):
    t = pd.read_csv("sec301_transfer_test.csv")
    a = t[t.test.str.startswith("A:") & (t.model == "logistic")].iloc[0]
    ref = t[t.test.str.startswith("ref:") & (t.model == "logistic")].iloc[0]
    assert pct(a.auc) == "67" and pct(ref.auc) == "73"
    assert f"{a.gain_vs_target_rate:.3f} ({a.lo_t:.3f} to {a.hi_t:.3f})" in docs["report"]
    pg = pd.read_csv("sec301_pooling_gain.csv").set_index("model").loc["logistic"]
    assert f"{pg.pooling_gain:.3f}, {pg.lo:.3f} to {pg.hi:.3f}" in docs["report"]
    b = pd.read_csv("s301_benchmark.csv").set_index(["sample", "measure"]).value
    s301 = [pct(b[("Section 301, real", k)]) for k in ["no fall", "recovered", "not recovered", "exited"]]
    assert " / ".join(s301) in docs["handoff"]
