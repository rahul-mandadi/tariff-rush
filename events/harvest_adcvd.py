"""Harvest antidumping and countervailing duty notices from the Federal Register.

The original harvest (harvest_fr.py) searched five Section 232/301/IEEPA phrases, so AD/CVD
notices were only caught incidentally: 155 documents in 2018 but 14 in 2025, which tracks the
search terms rather than Commerce's actual caseload. AD/CVD actions are the largest source of
product-specific, single-country tariff events available, and the project needs them because
21 Section 232/301/IEEPA events is too few to estimate repayment.

Strategy: pull the whole International Trade Administration index by year, which is where
AD/CVD lives, then fetch full text only for the notices whose titles mark a stage that starts
or changes duties. Investigations are kept and administrative reviews are dropped, because a
review adjusts the rate on an order that already exists while an investigation is what creates
the duty importers would front-load against.

Outputs
  events/adcvd_index.json   metadata for every ITA notice found
  events/raw/<doc>.txt      full text, shared with the existing harvest

Usage:  python3 events/harvest_adcvd.py      # from the repo root
"""
import json, os, re, time, urllib.request, urllib.parse

API = "https://www.federalregister.gov/api/v1/documents.json"
OUT = "events/raw"
AGENCY = "international-trade-administration"
FIELDS = ["document_number", "title", "type", "publication_date", "signing_date",
          "agencies", "citation", "html_url", "raw_text_url"]
YEARS = range(2015, 2027)

# stages that start or change a duty. "Determination" belongs to an investigation;
# "Results" belongs to an administrative review of an order that already exists.
KEEP = re.compile(
    r"(Preliminary\s+Determination|Affirmative\s+Preliminary|Preliminary\s+Affirmative"
    r"|Final\s+Determination|Final\s+Affirmative"
    r"|Antidumping\s+Duty\s+Order|Countervailing\s+Duty\s+Order"
    r"|Antidumping\s+and\s+Countervailing\s+Duty\s+Orders"
    r"|Initiation\s+of\s+Less-Than-Fair-Value"
    r"|Initiation\s+of\s+Countervailing\s+Duty)", re.I)
DROP = re.compile(r"Administrative\s+Review|Sunset\s+Review|Changed\s+Circumstances"
                  r"|Scope\s+Ruling|Opportunity\s+to\s+Request", re.I)


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))


def index_year(y):
    out, page = [], 1
    while page <= 20:
        q = {"per_page": 100, "page": page, "order": "oldest",
             "conditions[agencies][]": AGENCY,
             "conditions[publication_date][gte]": f"{y}-01-01",
             "conditions[publication_date][lte]": f"{y}-12-31"}
        qs = urllib.parse.urlencode(q) + "".join(f"&fields[]={f}" for f in FIELDS)
        d = json.loads(get(f"{API}?{qs}"))
        res = d.get("results") or []
        out += res
        if len(res) < 100:
            break
        page += 1
        time.sleep(0.3)
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    docs = []
    for y in YEARS:
        r = index_year(y)
        docs += r
        print(f"  {y}  {len(r):>5} ITA notices", flush=True)
        time.sleep(0.3)

    seen, uniq = set(), []
    for d in docs:
        if d["document_number"] not in seen:
            seen.add(d["document_number"])
            uniq.append(d)
    json.dump(uniq, open("events/adcvd_index.json", "w"), indent=1)
    print(f"\nindex: {len(uniq):,} unique ITA notices")

    want = [d for d in uniq
            if KEEP.search(d.get("title") or "") and not DROP.search(d.get("title") or "")]
    print(f"duty-starting stages after title filter: {len(want):,}")
    by_year = {}
    for d in want:
        by_year[d["publication_date"][:4]] = by_year.get(d["publication_date"][:4], 0) + 1
    print("  " + "  ".join(f"{k}:{v}" for k, v in sorted(by_year.items())))

    ok = skip = fail = 0
    for i, d in enumerate(want, 1):
        p = f"{OUT}/{d['document_number']}.txt"
        if os.path.exists(p) and os.path.getsize(p) > 200:
            skip += 1
            continue
        u = d.get("raw_text_url")
        if not u:
            fail += 1
            continue
        try:
            open(p, "wb").write(get(u))
            ok += 1
        except Exception:
            fail += 1
        if i % 100 == 0:
            print(f"  text {i}/{len(want)}  ok={ok} skip={skip} fail={fail}", flush=True)
        time.sleep(0.12)
    print(f"\nfull text: ok={ok} already had={skip} failed={fail}")
