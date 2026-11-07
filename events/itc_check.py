"""Bounded check: which preliminaries with no linked order were negative at the ITC?

A preliminary whose case numbers appear in no harvested order notice is either a case that ended
without an order (usually a negative final injury vote at the ITC) or a harvest gap. This script
classifies each unlinked investigation group (product family x initiation month) by searching the
Federal Register API for (a) the ITC's final determination notice and (b) a Commerce order notice
the harvest missed. Responses are cached in events/raw/itc_cache/ so the result can be retraced.

Classes per group:
  verified order       a Commerce order notice exists, or the ITC final is affirmative for all
  verified negative    the ITC final determination is negative for every country named
  mixed                the ITC final is affirmative for some countries and negative for others
  unresolved           nothing found, or the text could not be read

Descriptive only: whether a case becomes an order is itself selected.

Usage:  python3 events/itc_check.py      # from the repo root
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

import pandas as pd

API = "https://www.federalregister.gov/api/v1/documents.json"
CACHE = "events/raw/itc_cache"
os.makedirs(CACHE, exist_ok=True)
CASE = re.compile(r"\b([AC])-(\d{3})-(\d{3})\b")


def get(url):
    key = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9]+", "_", url)[-180:])
    if os.path.exists(key):
        return open(key).read()
    for i in range(3):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                txt = r.read().decode("utf-8", "ignore")
            open(key, "w").write(txt)
            time.sleep(0.3)
            return txt
        except Exception:
            time.sleep(2 * (i + 1))
    return ""


def search(agency, term, lo, hi):
    q = {"conditions[agencies][]": agency, "conditions[term]": f'"{term}"',
         "conditions[publication_date][gte]": lo, "conditions[publication_date][lte]": hi,
         "per_page": 100}
    qs = urllib.parse.urlencode(q) + "".join(
        f"&fields[]={f}" for f in ["title", "document_number", "publication_date", "raw_text_url"])
    txt = get(f"{API}?{qs}")
    try:
        return json.loads(txt).get("results", [])
    except Exception:
        return []


def family(title):
    t = " ".join(title.split())
    t = re.sub(r"^(antidumping( duty)?( and countervailing duty)?|countervailing duty)"
               r" investigations? of ", "", t, flags=re.I)
    t = t.split(" From ")[0]
    t = re.sub(r"^certain ", "", t, flags=re.I)
    return t.strip()


e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
docs = e.drop_duplicates("document_number")
allc = {d: {"-".join(m) for m in CASE.findall(open(f"events/raw/{d}.txt", errors="ignore").read())}
        for d in docs.document_number}
order_cases = set().union(*[allc[d] for d in docs[docs.stage == "order"].document_number])

ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
ep["first_doc"] = ep.docs.str.split(";").str[0]
title = docs.set_index("document_number").title
ep["family"] = ep.first_doc.map(title).map(family)
ep["linked"] = ep.docs.str.split(";").map(lambda ds: any(allc.get(d, set()) & order_cases for d in ds))
ep["b_date"] = pd.to_datetime(((ep.b // 12).astype(str) + "-" + (ep.b % 12 + 1).astype(str) + "-01"))
old = ep[ep.b_date < "2025-06-01"]
un = old[~old.linked]
groups = un.groupby(["family", "ini"])
print(f"episodes before mid-2025: {len(old)}; unlinked: {len(un)} in {groups.ngroups} groups")

NEG = re.compile(r"(not materially injured|negative determination|determines?,? pursuant to "
                 r"section 735\(b\)[^.]{0,300}?not)", re.I)
AFF = re.compile(r"materially injured by reason of imports", re.I)
rows = []
for (fam, ini), g in groups:
    lo = g.b_date.min().strftime("%Y-%m-%d")
    hi = (g.b_date.max() + pd.DateOffset(months=14)).strftime("%Y-%m-%d")
    term = " ".join(fam.split()[:6])
    itc = [r for r in search("international-trade-commission", term, lo, hi)
           if "determination" in r["title"].lower() or "from" in r["title"].lower()]
    ita = [r for r in search("international-trade-administration", term, lo, hi)
           if re.search(r"(antidumping|countervailing) duty orders?\b|\border\b", r["title"], re.I)
           and not re.search(r"review|initiation|preliminary", r["title"], re.I)]
    verdict, evidence = "unresolved", ""
    if ita:
        verdict, evidence = "verified order", ita[0]["document_number"]
    finals = []
    for r in itc:
        t = get(r["raw_text_url"]) if r.get("raw_text_url") else ""
        t = " ".join(t.split())
        if "(Final)" in t or "final phase" in t.lower():
            i = t.find("etermination")
            seg = t[i:i + 3000]
            finals.append((r["document_number"], bool(NEG.search(seg)), bool(AFF.search(seg)), seg[:300]))
    if finals and verdict == "unresolved":
        neg = any(f[1] for f in finals)
        aff = any(f[2] and not f[1] for f in finals)
        verdict = "mixed" if (neg and aff) else ("verified negative" if neg else
                                                ("verified order" if aff else "unresolved"))
        evidence = ";".join(f[0] for f in finals)
    rows.append(dict(family=fam, ini=ini, episodes=len(g), countries=";".join(sorted(g.cty)),
                     verdict=verdict, evidence=evidence,
                     snippet=finals[0][3] if finals else ""))
    print(f"  {verdict:<18} {len(g):>3}  {fam[:60]}")

out = pd.DataFrame(rows)
out.to_csv("events/itc_check.csv", index=False)
print("\n", out.groupby("verdict").agg(groups=("family", "size"), episodes=("episodes", "sum")))
print("wrote events/itc_check.csv")


# ---- second pass: per country, since ITC votes often split by country -------------------------
names = (pd.read_parquet("panel/hs8/2018-01.parquet", columns=["cty", "cty_name"])
         .drop_duplicates("cty").set_index("cty").cty_name.str.title().to_dict())
ALIAS = {"Korea, South": ["Korea"], "China": ["China"], "Vietnam": ["Vietnam", "Viet Nam"],
         "Taiwan": ["Taiwan"], "Russia": ["Russia"], "Turkey": ["Turkey", "Turkiye"]}


def country_terms(code):
    n = names.get(str(code), "")
    for k, v in ALIAS.items():
        if k.lower() in n.lower():
            return v
    return [n.split(",")[0]] if n else []


per = []
for _, row in out.iterrows():
    texts = []
    for dn in str(row.evidence).split(";"):
        if not dn or dn == "nan":
            continue
        meta = search("international-trade-commission", dn, "2014-01-01", "2026-12-31")
        url = f"https://www.federalregister.gov/documents/full_text/text/{dn}.txt"
        # the raw text URL needs the publication path; fetch it from the document endpoint
        js = get(f"https://www.federalregister.gov/api/v1/documents/{dn}.json?fields[]=raw_text_url")
        try:
            url = json.loads(js)["raw_text_url"]
        except Exception:
            continue
        t = " ".join(get(url).split())
        # determination notices only; scheduling notices say "to determine whether ... is
        # materially injured by reason of imports from ...", which reads as affirmative
        if "(Final)" not in t or not re.search(r"determines,? pursuant to", t):
            continue
        i = t.find("etermination")
        texts.append(t[i:i + 2500])
    for c in row.countries.split(";"):
        terms = country_terms(c)
        neg = aff = False
        for seg in texts:
            for sent in re.split(r"(?<=\.)\s+(?=[A-Z])", seg):
                if "determin" in sent.lower() and any(tm and tm.lower() in sent.lower() for tm in terms):
                    if re.search(r"not materially injured|negative", sent, re.I):
                        neg = True
                    elif re.search(r"materially injured|affirmative", sent, re.I):
                        aff = True
        v = row.verdict
        if row.verdict in ("verified negative", "mixed"):
            v = ("verified negative" if neg and not aff else
                 "verified order" if aff and not neg else "unresolved")
        per.append(dict(family=row.family, ini=row.ini, cty=c, country=names.get(str(c), ""),
                        verdict=v, group_verdict=row.verdict))
pc = pd.DataFrame(per)
pc.to_csv("events/itc_check_by_country.csv", index=False)
print("\nper-country verdicts (episodes):")
print(pc.verdict.value_counts())
print(pd.crosstab(pc.group_verdict, pc.verdict))
print("wrote events/itc_check_by_country.csv")
