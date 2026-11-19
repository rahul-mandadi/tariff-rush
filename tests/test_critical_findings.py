"""How a notice's own critical-circumstances finding is read (events/parse_adcvd.py).

Until November 2026 one pattern over the whole text read "critical circumstances do not exist" as
affirmative, and also counted cited case titles and allegations. These tests pin the corrected rule
on affirmative, negative and mixed wording, and check the parsed events file on known notices.
Run from the repository root:  python3 -m pytest tests -q
"""
import os
import sys

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "events"))
from parse_adcvd import critical_findings  # noqa: E402

ONE = ["INDIA"]


def test_affirmative():
    txt = "We preliminarily determine that critical circumstances exist for imports produced or exported by all Indian exporters."
    assert critical_findings(txt, "", ONE) == {"INDIA": "affirmative"}


def test_negative_do_not_exist():
    # the wording the old pattern read as affirmative (ferrosilicon from Kazakhstan, 2024-25795)
    txt = ("In accordance with section 733(e) of the Act and 19 CFR 351.206, Commerce preliminarily finds that "
           "critical circumstances do not exist for YDD, TNC Kazchrome JSC (Kazchrome), and all other companies "
           "not individually examined.")
    title = ("Ferrosilicon From Kazakhstan: Preliminary Affirmative Determination of Sales at Less Than Fair Value, "
             "Preliminary Negative Determination of Critical Circumstances")
    assert critical_findings(txt, title, ["KAZAKHSTAN"]) == {"KAZAKHSTAN": "negative"}


def test_negative_do_not_find():
    txt = "With respect to all other producers and exporters, we preliminarily do not find that critical circumstances exist."
    assert critical_findings(txt, "", ONE) == {"INDIA": "negative"}


def test_mixed_across_exporters():
    txt = ("We preliminarily determine that critical circumstances do not exist for GITI and the Sailun Group, "
           "while they do exist for all non-individually investigated companies and the PRC-wide entity.")
    assert critical_findings(txt, "", ["CHINA"]) == {"CHINA": "mixed"}


def test_mixed_with_but_do_exist():
    # wire rod from Spain, 2017-23650: the old pattern and a first draft of the fix both read this negative
    txt = ("In accordance with section 733(e) of the Act and 19 CFR 351.206, the Department preliminarily finds "
           "that critical circumstances do not exist for CELSA and all-other companies, but do exist for AME.")
    assert critical_findings(txt, "", ["SPAIN"]) == {"SPAIN": "mixed"}


def test_mixed_from_title_in_part():
    title = "Certain Tires From India: Preliminary Affirmative Critical Circumstances Determination, in Part"
    assert critical_findings("", title, ONE) == {"INDIA": "mixed"}


def test_several_countries_each_get_their_own_finding():
    txt = ("Commerce preliminarily determines that in the countervailing duty investigations on utility scale "
           "wind towers, critical circumstances exist with respect to imports of wind towers from Indonesia and do "
           "not exist with respect to imports of wind towers from Canada and Vietnam.")
    assert critical_findings(txt, "", ["CANADA", "INDONESIA", "VIETNAM"]) == {
        "CANADA": "negative", "INDONESIA": "affirmative", "VIETNAM": "negative"}
    txt = ("Commerce preliminarily determines that critical circumstances exist with respect to imports of CORE "
           "from the United Arab Emirates (UAE) and that critical circumstances do not exist with respect to "
           "imports of CORE from South Africa.")
    assert critical_findings(txt, "", ["UNITED ARAB EMIRATES", "SOUTH AFRICA"]) == {
        "UNITED ARAB EMIRATES": "affirmative", "SOUTH AFRICA": "negative"}


def test_a_country_not_named_in_any_finding_gets_none():
    txt = ("We preliminarily determine that critical circumstances exist with respect to imports of silicon metal "
           "exported by PCC Bakki and all other producers/exporters from Iceland.")
    assert critical_findings(txt, "", ["BOSNIA AND HERZEGOVINA", "ICELAND"]) == {
        "BOSNIA AND HERZEGOVINA": "none", "ICELAND": "affirmative"}


@pytest.mark.parametrize("txt", [
    # an allegation is not a finding
    "On August 18, 2025, the petitioner alleged that critical circumstances exist with respect to imports from India.",
    # the statute describes the test, it does not apply it
    "Section 733(e)(1) of the Act provides that Commerce will preliminarily determine that critical circumstances "
    "exist if there is a reasonable basis to believe or suspect that imports were massive.",
    # the name of another case Commerce cites, in Title Case
    "See Notice of Final Determination and Affirmative Preliminary Determination of Critical Circumstances: "
    "Magnesium Metal from the People's Republic of China, 70 FR 5606 (February 3, 2005).",
])
def test_not_a_finding(txt):
    assert critical_findings(txt, "", ONE) == {"INDIA": "none"}


# preliminary notices whose text says only "critical circumstances do not exist" (checked by hand,
# November 2026); the old pattern flagged every one of them affirmative
NEGATIVE_38 = """2015-32758 2017-03631 2017-22065 2017-23646 2017-23647 2018-23719 2019-10282 2019-26818
2019-26819 2020-02962 2020-02963 2020-15841 2020-21547 2020-22803 2020-22805 2020-24299 2020-24302
2020-25483 2020-25486 2020-25488 2021-02082 2022-10051 2023-09350 2023-18027 2023-18029 2023-28940
2023-28942 2024-11026 2024-15978 2024-17755 2024-25795 2024-25796 2024-26257 2024-26259 2024-29114
2026-01187 2026-04002 2026-06450""".split()


def test_parsed_events_file():
    e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
    if "critical_finding" not in e:
        pytest.skip("events/adcvd_events.csv predates the critical_finding column")
    got = e.set_index(["document_number", "country"]).critical_finding
    assert len(NEGATIVE_38) == 38
    assert all(got[d].eq("negative").all() for d in NEGATIVE_38)
    assert got[("2020-27316", "ICELAND")] == "affirmative"
    assert got[("2020-27316", "BOSNIA AND HERZEGOVINA")] == "none"
    assert got[("2017-13794", "CANADA")] == "mixed"
    assert (e.critical_affirm == e.critical_finding.isin(["affirmative", "mixed"])).all()
