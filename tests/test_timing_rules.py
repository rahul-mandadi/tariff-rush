"""Regression checks for the timing rules every forecast depends on.

Run from the repository root:  python3 -m pytest tests -q

The panel-based checks need the git-ignored parquet files (rebuilt by adcvd_stacked.py,
build_decision_stacks.py and sec301_benchmark.py) and skip if they are absent.
"""
import ast
import os

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def _exclude():
    tree = ast.parse(open("adcvd_stacked.py").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "EXCLUDE":
            return set(ast.literal_eval(node.value))
    raise AssertionError("EXCLUDE not found")


@pytest.fixture(scope="module")
def notices():
    e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
    p = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
    prods = {d: set(g.hs8) for d, g in p.groupby("document_number")}
    e = e[(e.stage == "preliminary") & e.window_days.notna() & (e.window_days >= 60)]
    e = e[e.document_number.isin(prods) & ~e.document_number.isin(_exclude())].copy()
    e["date"] = pd.to_datetime(e.publication_date)
    e["b"] = e.date.dt.year * 12 + e.date.dt.month - 1
    e["P"] = e.document_number.map(prods)
    return e


@pytest.fixture(scope="module")
def episodes(notices):
    ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
    date = notices.drop_duplicates("document_number").set_index("document_number").date
    P = notices.drop_duplicates("document_number").set_index("document_number").P
    first, p0 = [], []
    for ds in ep.docs:
        ds = ds.split(";")
        f = min(date[d] for d in ds)
        first.append(f)
        p0.append(set().union(*[P[d] for d in ds if date[d] <= f]))
    ep["first_date"], ep["P0"] = first, p0
    return ep


def _named(notices):
    named = {}
    for r in notices.itertuples():
        for h in r.P:
            named.setdefault((h, r.cty), []).append((r.b, r.date))
    return named


def _load(path, **kw):
    if not os.path.exists(path):
        pytest.skip(f"{path} not built")
    return pd.read_parquet(path, **kw)


def test_decision_panels_use_only_products_named_by_the_first_preliminary(episodes):
    d = _load("panel/adcvd_stacks_decision.parquet", columns=["sid", "hs8"]).drop_duplicates()
    bad = [(s, h) for s, h in d.itertuples(index=False) if h not in episodes.P0[s]]
    assert not bad, f"{len(bad)} products named only by a later companion notice, e.g. {bad[:3]}"


def test_decision_panels_drop_rivals_only_for_cases_published_by_the_first_preliminary(notices, episodes):
    d = _load("panel/adcvd_stacks_decision.parquet", columns=["sid", "hs8", "cty", "treated"])
    kept = d[~d.treated][["sid", "hs8", "cty"]].drop_duplicates()
    named = _named(notices)
    leaks = [(s, h, c) for s, h, c in kept.itertuples(index=False)
             if any(episodes.b[s] - 36 <= bb and fd <= episodes.first_date[s] for bb, fd in named.get((h, c), []))]
    assert not leaks, f"{len(leaks)} kept rivals were already named by a published case, e.g. {leaks[:3]}"


def test_section301_strict_sample_uses_exact_dates(notices):
    st = _load("panel/s301_stacks.parquet", columns=["sid", "hs8", "cty", "treated", "sample"])
    info = pd.read_csv("s301_stacks_info.csv")
    lists = pd.read_csv("events/s301_products.csv", dtype={"hs8": str})
    start = {r.list: pd.Timestamp(r.start) for r in lists.drop_duplicates("list").itertuples()}
    strict = st[st["sample"] == "real, strict"]
    named = _named(notices)
    for sid, g in strict.groupby("sid"):
        row = info.set_index("sid").loc[sid]
        b0, s0 = int(row.b), start[row.list]
        for h, c in g[~g.treated][["hs8", "cty"]].drop_duplicates().itertuples(index=False):
            assert not any(b0 - 36 <= bb and fd <= s0 for bb, fd in named.get((h, c), [])), (sid, h, c)
        china = g[g.treated].hs8.unique()
        assert not any(any(b0 - 36 <= bb and fd <= s0 for bb, fd in named.get((h, "5700"), [])) for h in china)


def test_monthly_forecast_rows_are_eligible_only_on_visible_data():
    P = pd.read_csv("prediction_landmark_heldout.csv", dtype={"hs8": str})
    pairs = pd.read_csv("recovery_pairs_decision_fall20.csv", dtype={"hs8": str})
    pairs["hs8"] = pairs.hs8.str.zfill(8)
    P["hs8"] = P.hs8.str.zfill(8)
    m = P.merge(pairs[["sid", "hs8", "fell_at", "rec_at"]], on=["sid", "hs8"], how="left")
    assert m.fell_at.notna().all()
    kv = m.L - 2
    assert (m.fell_at <= kv).all(), "a product scored before its fall was visible"
    assert not (m.rec_at.notna() & (m.rec_at + 2 <= kv)).any(), "a product scored after it was visibly back"
    assert ((m.y == 1) == m.rec_at.notna()).all()


def test_training_labels_are_published_before_each_test_year():
    ep = pd.read_csv("adcvd_episodes_collapsed.csv")
    yrs = pd.read_csv("prediction_stage2_years.csv")
    D = pd.read_csv("prediction_stage2_features.csv")
    for r in yrs.itertuples():
        d = D[D.point == r.point]
        tr = d[(d.b + 18 + 2) < r.year * 12]
        assert tr.sid.nunique() == r.train_episodes
        assert (tr.b + 18 + 2 < r.year * 12).all()


def test_net_benefit_formula_on_a_hand_example():
    import decision_value as DV
    d = pd.DataFrame({"bad": [1, 1, 0, 0], "w": [1.0, 1.0, 1.0, 1.0], "model": [0.9, 0.2, 0.8, 0.1]})
    nb = DV.nb_matrix(d, ["model"])
    j = list(DV.T).index(0.5)
    # at t = 0.5 the model acts on rows 0 and 2: one true bad, one false alarm, weight t/(1-t) = 1
    assert np.isclose(nb["model"][j], 1 / 4 - 1 / 4 * 1.0)
    assert np.isclose(nb["always act"][j], 2 / 4 - 2 / 4 * 1.0)
    assert np.allclose(nb["never act"], 0.0)


def test_decision_panels_drop_no_rival_on_later_information(notices, episodes):
    """The leak direction that was fixed: a rival that traded the product before the case must stay
    in the decision panel unless a case naming it on that product was published by the episode's
    first preliminary. Checked on a fixed sample of 40 episodes against the raw panel."""
    d = _load("panel/adcvd_stacks_decision.parquet", columns=["sid", "hs8", "cty"])
    import recovery_lib as RL
    rng = np.random.default_rng(0)
    sids = rng.choice(sorted(d.sid.unique()), 40, replace=False)
    sub = d[d.sid.isin(sids)]
    kept = sub.groupby(["sid", "hs8"]).cty.apply(set).to_dict()
    hs = {h for _, h in kept}
    raw = RL.load_raw(hs, int(episodes.b.min()) - 18, int(episodes.b.max()))
    named = _named(notices)
    for (s, h), ctys in kept.items():
        b, ini, tc = int(episodes.b[s]), int(episodes.ini[s]), episodes.cty[s]
        pre = raw[(raw.hs8 == h) & raw.m.between(b - 18, min(b - 7, ini - 1))]
        dropped = set(pre.cty) - ctys - {tc}
        for c in dropped:
            assert any(b - 36 <= bb and fd <= episodes.first_date[s] for bb, fd in named.get((h, c), [])), \
                f"episode {s}, product {h}: rival {c} dropped without a case published by the first preliminary"
