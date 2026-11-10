"""The month-4 review queue (review_queue.py): tie handling, same-month queues, and Table 4.

Run from the repository root:  python3 -m pytest tests -q
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
REPORT = " ".join(open("FINAL_REPORT.md").read().split())


def _reviewed():
    src = open("review_queue.py").read()
    start = src.index("def reviewed(")
    ns = {"np": np}
    exec(src[start:src.index("\ndef evaluate(")], ns)
    return ns["reviewed"]


def test_capacity_is_exact_and_ties_share_it():
    reviewed = _reviewed()
    r = reviewed([0.9, 0.5, 0.5, 0.5, 0.1], np.ones(5), 0.2)       # one review for five
    assert np.isclose(r.sum(), 1.0) and r[0] == 1.0 and (r[1:] == 0).all()
    r = reviewed([0.9, 0.5, 0.5, 0.5, 0.1], np.ones(5), 0.4)       # two reviews: one left for three tied
    assert np.allclose(r, [1, 1 / 3, 1 / 3, 1 / 3, 0])
    r = reviewed([0.0] * 4, np.ones(4), 0.2)                          # all tied, as the historical rate is
    assert np.allclose(r, 0.2)


def test_queues_rank_only_relationships_at_the_same_checkpoint():
    P = pd.read_csv("prediction_landmark_heldout.csv")
    P = P[P.L == 4]
    W = pd.read_csv("review_queue_watchlist.csv")
    assert len(W) == len(P)
    m = W.decision_month.str[:4].astype(int) * 12 + W.decision_month.str[5:].astype(int) - 1
    b = pd.Series(P.b.values + 4).sort_values().values
    assert (np.sort(m.values) == b).all(), "each queue is the calendar month k = 4 of its cases"
    # history is one number per queue, so it orders nothing
    assert (W.groupby("decision_month").history_not_recovered.nunique() == 1).all()


def test_table4_matches_the_csv():
    E = pd.read_csv("review_queue_eval.csv")
    E = E[E.weighting == "relationship"]
    for cap in [0.1, 0.2, 0.3]:
        g = E[E.capacity == cap].set_index(["ranking", "measure"]).value
        cells = [f"{100 * g[(r, 'precision')]:.0f}% ({100 * g[(r, 'capture')]:.0f}%)"
                 for r in ["forecast (boosting)", "latest share", "historical rate"]]
        d = E[(E.capacity == cap) & (E.ranking == "forecast (boosting)") & (E.measure == "precision")].iloc[0]
        diff = (f"+{100 * d['diff_vs_latest share']:.1f} [{100 * d['lo_vs_latest share']:.1f}, "
                f"{100 * d['hi_vs_latest share']:.1f}]")
        line = f"| {100 * cap:.0f}% | " + " | ".join(cells) + f" | {diff} |"
        assert line in REPORT, line
    # the stated decision rule: the forecast is the ranking only if it clears the latest share at 20%
    d = E[(E.capacity == 0.2) & (E.ranking == "forecast (boosting)") & (E.measure == "precision")].iloc[0]
    assert d["lo_vs_latest share"] > 0
