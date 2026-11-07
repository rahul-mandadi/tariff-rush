"""Harvest Federal Register documents that plausibly announce a US tariff action, 2018 onward.

Metadata from the search API, full text cached per document so parsing can run offline.
Checkpointed: a restart skips what is already on disk.
"""
import json, os, time, urllib.request, urllib.parse

API = "https://www.federalregister.gov/api/v1/documents.json"
OUT = "events/raw"
FIELDS = ["document_number","title","type","publication_date","signing_date",
          "president","agencies","citation","html_url","raw_text_url","presidential_document_number"]
TERMS = ["Section 232 tariff", "Section 301 tariff", "adjusting imports",
         "International Emergency Economic Powers Act tariff", "duty rate imports increase"]

def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return r.read()
        except Exception as e:
            if i == tries-1: raise
            time.sleep(2*(i+1))

def search(term):
    out, page = [], 1
    while page <= 10:
        q = {"per_page":100, "page":page, "order":"oldest",
             "conditions[term]": term,
             "conditions[publication_date][gte]":"2018-01-01"}
        qs = urllib.parse.urlencode(q) + "".join(f"&fields[]={f}" for f in FIELDS)
        d = json.loads(get(f"{API}?{qs}"))
        res = d.get("results") or []
        out += res
        if len(res) < 100: break
        page += 1
        time.sleep(0.4)
    return out

seen, docs = set(), []
for t in TERMS:
    r = search(t)
    new = [d for d in r if d["document_number"] not in seen]
    for d in new: seen.add(d["document_number"])
    docs += new
    print(f"  {t!r:55} {len(r):4d} hits, {len(new):4d} new")

json.dump(docs, open(f"{OUT}/../fr_index.json","w"), indent=1)
print(f"\nindex: {len(docs)} unique documents -> events/fr_index.json")

ok = fail = skip = 0
for i, d in enumerate(docs, 1):
    p = f"{OUT}/{d['document_number']}.txt"
    if os.path.exists(p) and os.path.getsize(p) > 200: skip += 1; continue
    u = d.get("raw_text_url")
    if not u: fail += 1; continue
    try:
        open(p,"wb").write(get(u)); ok += 1
    except Exception: fail += 1
    if i % 50 == 0: print(f"  text {i}/{len(docs)}  ok={ok} skip={skip} fail={fail}")
    time.sleep(0.15)
print(f"full text: ok={ok} skipped={skip} failed={fail}")
