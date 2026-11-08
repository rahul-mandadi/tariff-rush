"""Checks for the two rules added in November 2026: months with no comparison trade are missing, and
forecasts see only trade months Census had released by the decision date.

Run from the repository root:  python3 -m pytest tests -q
"""
import os

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
import recovery_lib as RL  # noqa: E402


def toy(target_values, rival_values):
    """One pair, months k = -18..18; target and one rival with the given monthly values."""
    ks = range(-18, 19)
    rows = [dict(sid=0, hs8="00000000", k=k, m=100 + k, value=v, treated=True) for k, v in zip(ks, target_values)]
    rows += [dict(sid=0, hs8="00000000", k=k, m=100 + k, value=v, treated=False) for k, v in zip(ks, rival_values)]
    return pd.DataFrame(rows)


def test_month_without_any_comparison_trade_is_missing_not_a_fall():
    # targeted country holds half the market throughout, except two months where nobody traded
    t = [1.0] * 37
    r = [1.0] * 37
    for k in (-2, -1):
        t[k + 18] = r[k + 18] = 0.0
    p = RL.categorize(toy(t, r), 18, {0: 100}, 200)
    assert p.category.iloc[0] == "no fall", p.to_dict("records")


def test_pair_with_no_measurable_fall_window_gets_no_label():
    t = [1.0] * 37
    r = [1.0] * 37
    for k in range(-2, 19):  # no trade by anyone from k = -2 on (a retired code)
        t[k + 18] = r[k + 18] = 0.0
    p = RL.categorize(toy(t, r), 18, {0: 100}, 200)
    assert p.empty


def test_targeted_country_alone_stopping_is_still_a_fall():
    t = [1.0] * 37
    r = [1.0] * 37
    for k in range(0, 19):
        t[k + 18] = 0.0
    p = RL.categorize(toy(t, r), 18, {0: 100}, 200)
    assert p.category.iloc[0] == "exited"


def test_release_calendar_is_complete_and_ordered():
    c = pd.read_csv("census_release_calendar.csv", parse_dates=["release"])
    assert c.m.diff().dropna().eq(1).all()
    assert c.release.is_monotonic_increasing
    gap = (c.release.dt.year * 12 + c.release.dt.month - 1) - c.m
    assert gap.between(1, 4).all()
    # the 2025 shutdown: August to October 2025 data came out in month m + 3
    assert (gap[c.m.isin([2025 * 12 + 7, 2025 * 12 + 8, 2025 * 12 + 9])] == 3).all()


def test_itc_vote_uses_only_released_trade_months():
    f = pd.read_csv("prediction_stage2_features.csv")
    f = f[f.point == "ITC"]
    ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
    fs = RL.final_stage(ep)
    rel = pd.read_csv("census_release_calendar.csv", parse_dates=["release"]).set_index("m").release
    seen = f.b + f.entry + 2  # last trade month used
    d_final = pd.to_datetime(f.sid.map(fs.d_final))
    assert (rel.reindex(seen).to_numpy() <= d_final.to_numpy()).all(), "a vote used a month not yet released"


@pytest.mark.parametrize("point", ["ITC final vote", "fall first visible"])
def test_decision_value_claims_match_the_bounds(point):
    d = pd.read_csv("decision_value.csv")
    x = d[d.point == point]
    cols = [c for c in x.columns if c.startswith("simlo_") and x[c].notna().all()]
    supported = x.threshold[(x[cols] > 0).all(axis=1)].round(2).tolist()
    joint = pd.read_csv("decision_value_joint.csv").set_index("point").supported_thresholds[point]
    assert joint == (", ".join(f"{t:.2f}" for t in supported) or "none")
    if point == "ITC final vote":
        other = [c for c in cols if c != "simlo_share only"]
        ahead = x.threshold[(x[other] > 0).all(axis=1)].round(2).tolist()
        assert ahead == [0.45, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8], ahead


def test_deck_numbers_match_the_csv():
    pptx = pytest.importorskip("pptx")
    r = pd.read_csv("recovery_benchmark_fall20.csv").set_index(["sample", "measure"])
    pct = lambda x: f"{100 * x:.0f}"  # noqa: E731
    want = (f"{pct(r.value[('real', 'no fall')])}% did not fall, {pct(r.value[('real', 'recovered')])}% fell and "
            f"recovered, {pct(r.value[('real', 'not recovered')])}% stayed down while trading, "
            f"{pct(r.value[('real', 'exited')])}% fell")
    km = r.loc[("real", "KM recovered by 18")]
    for fn in ["slides/Mandadi_Khalsa_Presentation2_v2.pptx", "slides/Mandadi_Khalsa_Final_Presentation.pptx"]:
        text = []
        for s in pptx.Presentation(fn).slides:
            text += [sh.text_frame.text for sh in s.shapes if sh.has_text_frame]
            if s.has_notes_slide:
                text.append(s.notes_slide.notes_text_frame.text)
        flat = " ".join(" ".join(text).split())
        assert want in flat, fn
        if "Final" in fn:
            assert f"{pct(km.value)}% ({pct(km.lo)} to {pct(km.hi)})" in flat


def test_both_programs_flag_uses_only_investigations_open_by_the_decision():
    ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str, "P": str})
    both = RL.both_programs_known(ep)
    e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
    pre = e[e.stage == "preliminary"].drop_duplicates("document_number").set_index("document_number")
    for s, r in ep[both].iterrows():
        own = pre.loc[pre.index.isin(str(r.docs).split(";"))]
        fd = pd.Timestamp(r.first_date)
        # every program counted from the episode's own notices was initiated by the decision date
        opened = pd.to_datetime(own.initiation_date, errors="coerce")
        assert ((pd.to_datetime(own.publication_date) <= fd) | (opened <= fd) | opened.isna()).all(), s
    assert both[288], "CVD case whose AD companion preliminary was negative: AD was still opened"
    assert (both | ~(ep.ad & ep.cvd)).all(), "every episode with both programs' preliminaries keeps the flag"


def test_both_programs_flag_needs_both_programs_public_by_the_decision():
    # fixtures from a real episode (Canada, 2017): CVD preliminary 2017-04-28 (its first_date) and AD
    # preliminary 2017-06-30, both investigations initiated 2016-12-22. Country set to a code with no
    # initiation notices, so only the episode's own preliminaries can count.
    ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str, "P": str})
    base = ep[ep.docs == "2017-08673;2017-13794"].iloc[0].copy()
    base["cty"] = "9999"
    cases = {
        "both open by the decision": (dict(), True),
        "CVD only (AD notice removed)": (dict(docs="2017-08673"), False),
        "AD only (CVD notice removed)": (dict(docs="2017-13794"), False),
        "decision before either was initiated": (dict(first_date="2016-12-21"), False),
    }
    fx = pd.DataFrame([{**base.to_dict(), **chg} for chg, _ in cases.values()], index=list(cases))
    got = RL.both_programs_known(fx)
    for k, (_, want) in cases.items():
        assert bool(got[k]) == want, k
    # and on the real table the flag is not trivially true: most single-program episodes stay False
    both = RL.both_programs_known(ep)
    single = ~(ep.ad & ep.cvd)
    assert (~both & single).sum() > (both & single).sum()
