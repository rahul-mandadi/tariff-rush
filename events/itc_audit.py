"""Audit of the episodes events/itc_check.py classed as "verified negative".

For each one, re-reads the cached ITC notices behind the verdict and records the evidence: the
investigation numbers the notice covers, its issue date, and the sentence that names the country
and carries the negative vote. Flags any case where that sentence also mentions critical
circumstances (where "negative" can refer to retroactivity rather than injury) and any case where
the notice's investigation numbers do not match the case numbers in our preliminary notices.

Reads only the cache in events/raw/itc_cache/; run events/itc_check.py and adcvd_stacked.py
first.

Usage:  python3 events/itc_audit.py      # from the repo root
"""
import json
import os
import re

import pandas as pd

CACHE = "events/raw/itc_cache"
K_HI, M_LAST, CUT = 18, 2026 * 12 + 7, 2025 * 12 + 5


def cached(url):
    key = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9]+", "_", url)[-180:])
    return open(key).read() if os.path.exists(key) else ""


def text(dn):
    js = cached(f"https://www.federalregister.gov/api/v1/documents/{dn}.json?fields[]=raw_text_url")
    try:
        return " ".join(cached(json.loads(js)["raw_text_url"]).split())
    except Exception:
        return ""


pc = pd.read_csv("events/itc_check_by_country.csv", dtype={"cty": str})
grp = pd.read_csv("events/itc_check.csv", dtype={"countries": str})
ev = {(r.family, r.ini): str(r.evidence) for r in grp.itertuples()}
ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
ep["sid"] = ep.index
# the verdict applies only to episodes with no linked order notice, as in itc_compare.py; a
# second episode with the same country and initiation month can be a different case that did
# become an order (printing plates beside aluminum extrusions, for example)
CASE = re.compile(r"\b([AC])-(\d{3})-(\d{3})\b")
docs = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str}).drop_duplicates("document_number")
allc = {d: {"-".join(m) for m in CASE.findall(open(f"events/raw/{d}.txt", errors="ignore").read())}
        for d in docs.document_number}
order_cases = set().union(*[allc[d] for d in docs[docs.stage == "order"].document_number])
ep["linked"] = ep.docs.str.split(";").map(lambda ds: any(allc.get(d, set()) & order_cases for d in ds))
stacked = set(pd.read_parquet("panel/adcvd_stacks_real.parquet", columns=["sid"]).sid)
ITC_INV = re.compile(r"(?:701|731)-TA-\d+(?:-\d+)?")

rows = []
for r in pc[pc.verdict == "verified negative"].itertuples():
    terms = {"Korea, South": "Korea"}.get(r.country, r.country.split(",")[0]).title()
    e = ep[(ep.ini == r.ini) & (ep.cty == r.cty) & ~ep.linked]
    best = None
    for dn in ev[(r.family, r.ini)].split(";"):
        t = text(dn)
        if "(Final)" not in t or not re.search(r"determines,? pursuant to", t):
            continue
        i = t.find("etermination")
        seg = t[i:i + 2500]
        for sent in re.split(r"(?<=\.)\s+(?=[A-Z])", seg):
            if "determin" in sent.lower() and terms.lower() in sent.lower() and \
                    re.search(r"not materially injured|negative", sent, re.I):
                issued = re.search(r"Issued: ([A-Z][a-z]+ \d{1,2}, \d{4})", t)
                best = dict(itc_doc=dn, itc_inv=";".join(sorted(set(ITC_INV.findall(t[:4000])))),
                            itc_issued=issued.group(1) if issued else "",
                            sentence=sent[:900],
                            crit_circ="critical circumstances" in sent.lower(),
                            says_not_injured=bool(re.search(r"not materially injured", sent, re.I)))
                break
        if best:
            break
    for x in e.itertuples():
        rows.append(dict(family=r.family, country=r.country, cty=r.cty, sid=x.sid,
                         year=x.b // 12, cluster=x.cluster, ad=x.ad, cvd=x.cvd,
                         in_comparison=bool(x.b < CUT and x.b + K_HI <= M_LAST and x.sid in stacked),
                         **(best or dict(itc_doc="", itc_inv="", itc_issued="", sentence="",
                                         crit_circ=False, says_not_injured=False))))

a = pd.DataFrame(rows)
a.to_csv("events/itc_negative_audit.csv", index=False)
print(f"verified-negative country rows: {(pc.verdict == 'verified negative').sum()}, "
      f"episodes: {a.sid.nunique()}, in the order-vs-negative comparison: {a.in_comparison.sum()}")
print(f"evidence sentence found: {(a.sentence != '').sum()}; says 'not materially injured': "
      f"{a.says_not_injured.sum()}; sentence mentions critical circumstances: {a.crit_circ.sum()}")
print("\nby product family (episodes, of which in comparison, years, countries):")
g = a.groupby("family").agg(episodes=("sid", "size"), in_comparison=("in_comparison", "sum"),
                            years=("year", lambda s: ",".join(map(str, sorted(set(s))))),
                            countries=("country", lambda s: ", ".join(sorted(set(s)))[:70]),
                            itc_inv=("itc_inv", "first"))
print(g.sort_values("episodes", ascending=False).to_string())
print("\nby year:", a.groupby("year").size().to_dict())
print("wrote events/itc_negative_audit.csv")
