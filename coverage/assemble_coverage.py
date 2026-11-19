"""Combine parsed product lists with rule-based scope into one coverage table.

Output: coverage/coverage_final.csv, one row per surcharge code and chapter, carrying how the
scope was determined so that anything rule-based can be audited or overridden later.
"""
import json, re
import pandas as pd
from rules import SECTION_232, IEEPA, EXCLUDE_CHAPTERS, classify

codes = json.load(open("coverage/raw/hts99_codes.json"))
parsed = pd.read_csv("coverage/coverage_map.csv", dtype={"chapter": str})
meta   = pd.read_csv("coverage/surcharge_codes.csv")
meta_by = {r.htsno: r for r in meta.itertuples()}

rows = []

# Rules take precedence over parsed lists for the two authorities that do not enumerate.
# A country-wide IEEPA tariff must not be reduced to whatever stray codes appear in its note,
# and a Section 232 material class is defined by the schedule, not by an incidental list.
ruled = {h for h in parsed.htsno if classify(h)[0] != "ENUMERATED"}
ruled |= {(c.get("htsno") or "") for c in codes
          if re.fullmatch(r"9903\.\d{2}\.\d{2}", c.get("htsno") or "")
          and classify(c["htsno"])[0] != "ENUMERATED"}
seen_enumerated = set(parsed.htsno) - ruled

for _, r in parsed.iterrows():
    if r.chapter in EXCLUDE_CHAPTERS or r.htsno in ruled: continue
    rows.append(dict(htsno=r.htsno, chapter=r.chapter, mechanism="ENUMERATED",
                     n_products=r.n_products_in_chapter, countries=r.countries,
                     rate_pct=r.rate_pct, basis=r.scope_source))

for c in codes:
    h = (c.get("htsno") or "").strip()
    if not re.fullmatch(r"9903\.\d{2}\.\d{2}", h) or h in seen_enumerated: continue
    mech, detail = classify(h)
    m = meta_by.get(h)
    ctys = getattr(m, "countries", "") if m is not None else ""
    rate = getattr(m, "rate_pct", None) if m is not None else None
    if mech == "MATERIAL_CLASS":
        for ch in detail["chapters"]:
            rows.append(dict(htsno=h, chapter=ch, mechanism=mech, n_products=None,
                             countries=ctys, rate_pct=rate, basis=detail["source"]))
    elif mech == "COUNTRY_WIDE":
        rows.append(dict(htsno=h, chapter="ALL", mechanism=mech, n_products=None,
                         countries=ctys, rate_pct=rate, basis=detail["name"]))

out = pd.DataFrame(rows)
out.to_csv("coverage/coverage_final.csv", index=False)

print(f"coverage rows: {len(out):,}\n")
print(out.mechanism.value_counts().to_string())
print(f"\ndistinct surcharge codes covered: {out.htsno.nunique()} of 637")
print(f"chapters named (excluding country-wide): {out[out.chapter!='ALL'].chapter.nunique()}")
print(f"\ncodes still with no scope at all: "
      f"{637 - out.htsno.nunique()}")
print("\nby mechanism, example codes:")
for mech, g in out.groupby("mechanism"):
    ex = g.htsno.unique()[:3]
    print(f"  {mech:<16} {g.htsno.nunique():>4} codes   e.g. {', '.join(ex)}")
