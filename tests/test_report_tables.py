"""The report's tables and remaining in-text numbers must match the CSVs they come from.

Complements test_headlines.py, which covers the abstract-level claims. Run from the repository
root:  python3 -m pytest tests -q
"""
import os

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
REPORT = " ".join(open("FINAL_REPORT.md").read().split())
pct = lambda x: f"{100 * x:.0f}"  # noqa: E731
sgn = lambda x: f"{x:+.2f}" if round(x, 2) > 0 else f"{x:.2f}"  # noqa: E731


def ref_rows(df, sample):
    d = df[(df["sample"] == sample) & df.outcome.str.startswith("PPML value")].set_index("contrast")
    return [d.loc[c] for c in ["after (0..18) vs reference (-18..-13)",
                               "months 13..18 vs reference (-18..-13)",
                               "pre-case (-12..-7) vs reference (-18..-13)"]]


def test_table1():
    s, i = pd.read_csv("adcvd_stacked.csv"), pd.read_csv("itc_compare.csv")
    rows = {"all, full follow-up | 381 (147)": ref_rows(s, "real, complete follow-up"),
            "became an order | 326 (125)": ref_rows(i, "final stage: order"),
            "ITC found no injury | 45 (18)": ref_rows(i, "final stage: negative"),
            "fake date | 283 (107)": ref_rows(s, "placebo, 24 months earlier")}
    for label, (a, b, c) in rows.items():
        first = f"**{sgn(a.est)}**" if "order" in label or "all" in label else sgn(a.est)
        line = f"| {label} | {first} ({a.se:.2f}) | {sgn(b.est)} ({b.se:.2f}) | {sgn(c.est)} ({c.se:.2f}) |"
        assert line in REPORT, line


def test_table2_intervals_and_final_stage():
    r = pd.read_csv("recovery_benchmark_fall20.csv").set_index(["sample", "measure"])
    f = pd.read_csv("recovery_by_final_stage.csv").set_index(["stage", "category"]).value
    labels = {"no fall": "did not fall", "recovered": "fell, came back",
              "not recovered": "fell, still down", "exited": "fell, no imports 13-18"}
    for k, lab in labels.items():
        re_, pl = r.loc[("real", k)], r.loc[("placebo", k)]
        line = (f"| {lab} | {pct(re_.value)}% [{pct(re_.lo)}, {pct(re_.hi)}] | "
                f"{pct(pl.value)}% [{pct(pl.lo)}, {pct(pl.hi)}] | "
                f"{pct(f[('order', k)])}% | {pct(f[('negative', k)])}% |")
        assert line in REPORT, line


def test_section3_3_text():
    r = pd.read_csv("recovery_benchmark_fall20.csv").set_index(["sample", "measure"]).value
    matched = [pct(r[("real, fake-date-matched", k)]) for k in ["no fall", "recovered", "not recovered", "exited"]]
    assert f"the real shares are {matched[0]}, {matched[1]}, {matched[2]} and {matched[3]}" in REPORT
    assert f"{pct(r[('real', 'KM recovered by 18')])} percent of products that fall are back" in REPORT
    assert f"against {pct(r[('placebo', 'KM recovered by 18')])} percent on the fake date" in REPORT
    ev = pd.read_csv("recovery_benchmark_eval_fall20.csv")
    wins = int((ev.brier_benchmark < ev.brier_uniform).sum())
    words = {4: "four", 5: "five", 6: "six"}
    assert f"beat a uniform guess in {words[wins]} of {words[len(ev)]} test years" in REPORT
    p = pd.read_csv("recovery_pairs_real_fall20.csv")
    p = p[p.follow >= 18]
    w = 1 / p.groupby("sid").sid.transform("size")
    none = ((~p.traded_13_18.astype(bool)) * w).sum() / w.sum()
    assert f"{pct(none)} percent have none then" in REPORT


def test_itc_vote_text():
    s2 = pd.read_csv("prediction_stage2.csv").set_index(["point", "model"])
    v = s2.loc[("ITC", "history by vote")]
    assert f"the vote itself adds {v.gain_vs_history:.3f} ({v.lo_vs_history:.3f} to {v.hi_vs_history:.3f})" in REPORT
    d = pd.read_csv("decision_value.csv")
    x = d[(d.point == "ITC final vote") & (d["lo_share only"] > 0)].threshold
    assert f"the share model from {x.min():.2f} to {x.max():.2f}" in REPORT
    assert np.allclose(np.diff(x.values), 0.05), "pointwise support over the share model is not one unbroken range"


def test_sample_counts():
    ep = pd.read_csv("adcvd_episodes_collapsed.csv")
    assert len(ep) == 504 and ep.cluster.nunique() == 205
    assert f"{(ep.k_ini > -13).sum()} of {len(ep)} episodes" in REPORT


def test_section301_tables():
    b = pd.read_csv("s301_benchmark.csv").set_index(["sample", "measure"])
    for k, lab in [("no fall", "did not fall"), ("recovered", "fell, came back"),
                   ("not recovered", "fell, still down"), ("exited", "fell, then no imports in months 11 to 16")]:
        cells = [b.loc[(s, k)] for s in ["Section 301, real", "Section 301, placebo", "AD/CVD, same horizon"]]
        line = f"| {lab} | " + " | ".join(f"{pct(c.value)}% [{pct(c.lo)}, {pct(c.hi)}]" for c in cells) + " |"
        assert line in REPORT, line
    sh = b.value
    assert f"from {100 * sh[('Section 301, real', 'China share before')]:.1f} to " \
           f"{100 * sh[('Section 301, real', 'China share late')]:.1f} percent" in REPORT
    t = pd.read_csv("sec301_transfer_test.csv")
    t = t[t.model == "logistic"].set_index(t[t.model == "logistic"].test.str[:2])
    for key in ["A:", "B:", "C:", "D:", "E:", "re"]:
        r = t.loc[key]
        cell = f"| {r.test_n:,} | {r.auc:.2f} | {r.brier:.3f} | {r.gain_vs_target_rate:.3f} [{r.lo_t:.3f}, {r.hi_t:.3f}] |"
        assert cell in REPORT, (key, cell)


def test_section301_rush_split():
    a = pd.read_csv("sec301_transfer_heldout_A.csv")
    hi, lo = a[a.rush > 1.25], a[a.rush <= 1.25]
    assert pct(np.average(hi.y, weights=hi.w)) == "60" and pct(np.average(lo.y, weights=lo.w)) == "30"
    assert "came back 60 percent of the time, against about 30" in REPORT


@pytest.mark.parametrize("point", ["fall", "ITC"])
def test_lookup_table(point):
    c = pd.read_csv("calibrated_lookup.csv")
    for _, r in c[c.point == point].iterrows():
        cell = f"{100 * r.expected:.0f} / {100 * r.came_back:.0f} ({r.cases})"
        assert cell in REPORT, cell
