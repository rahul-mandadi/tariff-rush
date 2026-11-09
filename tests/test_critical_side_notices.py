"""Critical-circumstances-only notices (fixed 2026-11-09): they never define an episode or its
k = 0, they stay available as dated information, and a forecast reads them only once published.

Run from the repository root:  python3 -m pytest tests -q
"""
import ast
import json
import os
import re

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
import recovery_lib as RL  # noqa: E402


def _literal(name):
    tree = ast.parse(open("adcvd_stacked.py").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} not found")


# titles that mention critical circumstances but carry a CVD preliminary ("Preliminary Affirmative
# Determination,", "(CVD) Determination", "Countervailing Duy Determination"), read 2026-11-09
NOT_SIDE = {"2015-20124", "2015-32215", "2018-08391", "2024-12114"}
# a side notice whose title names the LTFV investigation it belongs to
SIDE_EXTRA = {"2025-14337"}
MAIN = re.compile(r"less[- ]than[- ]fair[- ]value|countervailing duty determination|"
                  r"determinations? of sales|subsidy|countervailable", re.I)


def test_every_side_notice_title_is_in_cc_only():
    if not os.path.exists("events/adcvd_index.json"):
        pytest.skip("needs the git-ignored notice index (events/harvest_adcvd.py)")
    titles = {d["document_number"]: d.get("title") or "" for d in json.load(open("events/adcvd_index.json"))}
    e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
    pre = set(e[e.stage == "preliminary"].document_number)
    side = ({d for d in pre if "critical circumstances" in titles.get(d, "").lower()
             and not MAIN.search(titles.get(d, ""))} - NOT_SIDE) | SIDE_EXTRA
    cc = _literal("CC_ONLY")
    assert side - cc == set(), sorted(side - cc)
    assert cc - side == set(), sorted(cc - side)


def test_no_side_notice_defines_or_joins_an_episode():
    ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
    cc = _literal("CC_ONLY")
    inside = [(s, d) for s, ds in ep.docs.items() for d in ds.split(";") if d in cc]
    assert inside == [], inside


def test_side_notices_attach_to_their_own_country_and_case():
    ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
    side = pd.read_csv("events/cc_side_notices.csv", dtype={"cty": str, "sid": str}).fillna({"sid": ""})
    att = side[side.sid != ""]
    assert len(att) >= 25 and not att.sid.str.contains(";").any()
    for r in att.itertuples():
        s = int(r.sid)
        assert ep.cty[s] == r.cty, r
        m = pd.Timestamp(r.publication_date)
        assert ep.ini[s] <= m.year * 12 + m.month - 1, r
        assert r.document_number in str(ep.cc_docs[s]).split(";"), r
    # the duplicate episodes the side notices used to create (torsion springs, 2025) are gone:
    # one episode per country, holding its own AD and CVD preliminaries
    springs = ep[ep.docs.str.contains("2025-05758|2025-05759|2025-09944|2025-09945")]
    assert sorted(springs.cty) == ["5330", "5700"], springs[["cty", "ini", "b", "docs"]]


def test_side_notice_counts_only_once_published():
    t0, t1 = pd.Timestamp("2025-07-16"), pd.Timestamp("2025-07-29")
    crit_doc = {"own": False}
    assert not RL.crit_known(["own"], crit_doc, [t1], t0)
    assert RL.crit_known(["own"], crit_doc, [t1], t1)
    assert RL.crit_known(["own"], {"own": True}, [], t0)
    # negative findings in a multi-country side notice are not read as affirmative
    side = pd.read_csv("events/cc_side_notices.csv", dtype={"cty": str})
    wind = side[side.document_number == "2020-02696"].set_index("country").affirmative
    assert bool(wind["INDONESIA"]) and not wind["CANADA"] and not wind["VIETNAM"]


def test_misdated_initiation_no_longer_merges_two_cases():
    ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
    epoxy = ep[ep.docs.str.contains("2024-20885")]
    mono = ep[ep.docs.str.contains("2025-16653")]
    assert "2025-16653" not in epoxy.docs.iloc[0]
    assert "2025-17285" in mono.docs.iloc[0] and int(mono.ini.iloc[0]) == 2025 * 12 + 3
