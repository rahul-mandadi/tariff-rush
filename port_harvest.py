"""Pull district-level imports for the products in selected AD/CVD cases.

The stakeholder review's objection: every number so far is denominated in dollars at HS8 by
country, while capacity is committed at a facility. If displaced volume arrives at different
districts than it left, there is a lane story. If it arrives at the same districts from
different origins, an operator does not care, and we should say so.

Census publishes DISTRICT on the same imports/hs endpoint, and it supports HS10 detail. Two
traps on this endpoint that the country-only endpoint does not have:
  - rows come at SUMMARY_LVL DET and CGP, and only DET is detail
  - CTY_CODE here includes region aggregates such as 0003 EUROPEAN UNION and 0014 PACIFIC RIM
    alongside real countries, all of them 4 digits, so they cannot be filtered by shape

MONTH=* returns a whole year in one call, so the pull is one call per HS4 prefix per year.

Output: port/raw/<hs4>-<year>.json.gz

Usage:  CK=<census key> python3 port_harvest.py
"""
import json, gzip, os, time, urllib.request, urllib.error
import pandas as pd

K = os.environ["CK"]
B = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
F = ("DISTRICT,DIST_NAME,CTY_CODE,CTY_NAME,I_COMMODITY,GEN_VAL_MO,"
     "AIR_VAL_MO,VES_VAL_MO,SUMMARY_LVL")
OUT = "port/raw"


def fetch(hs4, year, tries=3):
    p = f"{OUT}/{hs4}-{year}.json.gz"
    if os.path.exists(p) and os.path.getsize(p) > 400:
        return "cached", 0
    q = (f"{B}?get={F}&YEAR={year}&MONTH=*&COMM_LVL=HS10"
         f"&I_COMMODITY={hs4}*&CTY_CODE=*&DISTRICT=*&key={K}")
    for t in range(tries):
        try:
            r = urllib.request.urlopen(q, timeout=600)
            raw = r.read()
            if r.status == 204 or not raw.strip():
                return "empty", 0
            d = json.loads(raw.decode())
            tmp = p + ".tmp"
            with gzip.open(tmp, "wt") as f:
                json.dump(d, f)
            os.replace(tmp, p)
            return "ok", len(d) - 1
        except urllib.error.HTTPError as e:
            if e.code == 204:
                return "empty", 0
            if t == tries - 1:
                return f"http {e.code}", 0
            time.sleep(10 + 15 * t)
        except Exception as e:
            if t == tries - 1:
                return f"err {type(e).__name__}", 0
            time.sleep(10 + 15 * t)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    tg = pd.read_csv("port_test_cases.csv", dtype=str)
    jobs = set()
    for _, r in tg.iterrows():
        y0, y1 = int(r.year_from), int(r.year_to)
        for h4 in str(r.hs4_list).split(";"):
            for y in range(y0, y1 + 1):
                jobs.add((h4, y))
    jobs = sorted(jobs)
    print(f"{len(jobs)} (HS4, year) pulls for {tg.case_id.nunique()} cases")

    tot = 0
    for i, (h4, y) in enumerate(jobs, 1):
        st, n = fetch(h4, y)
        tot += n
        print(f"[{i:>3}/{len(jobs)}] {h4} {y}  {st:<10}{n:>8,} rows  cum {tot:>10,}", flush=True)
        time.sleep(0.4)
    mb = sum(os.path.getsize(f"{OUT}/{f}") for f in os.listdir(OUT)
             if f.endswith(".json.gz")) / 1e6
    print(f"\n{tot:,} rows, {mb:.1f} MB on disk")
