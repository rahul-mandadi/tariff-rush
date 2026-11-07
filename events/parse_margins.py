"""Preliminary duty rate per AD/CVD preliminary notice, read from the notice's own rate table.

Commerce publishes each preliminary determination with a table of company rates in percent: an
estimated weighted-average dumping margin (AD) or an ad valorem subsidy rate (CVD). Most tables
end with an "All Others" row, the rate for exporters not individually examined; non-market
economy cases instead carry a country-wide entity rate (for example "China-wide entity"). That
row is the rate most of the country's trade faces, so it is the feature:

  rate      All Others row if present, else the country-wide entity row, else the largest rate
            in the table
  rate_src  which of the three it came from; blank if no table was found
  rate_max  the largest company rate in the table(s)

Read from the fixed-width text the Federal Register serves (events/raw/), where each table row
ends in its rate(s). Page markers and footnote markers are ignored. Rates above 500 percent are
kept only if they sit on an All Others or entity row, since a bare number that large in a table is
more often a page number than a rate.

Usage:  python3 events/parse_margins.py      # from the repo root
"""
import re

import pandas as pd

HEAD = re.compile(r"\(percent\)|percent\)\s*$|\(percent ad valorem\)", re.I)
ROW = re.compile(r"^(?P<name>.*?)[ .]{2,}(?P<r1>\d{1,3}(?:,\d{3})?\.\d{1,2})(?:\s+(?P<r2>\d{1,3}\.\d{1,2}))?\s*$")
OTHERS = re.compile(r"all[- ]?others", re.I)
ENTITY = re.compile(r"-?wide entity|entity\b", re.I)


def tables(text):
    """Rows (name, rate) from every block that follows a '(percent)' header."""
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        if HEAD.search(lines[i]):
            j = i + 1
            # skip the rule under the header
            while j < len(lines) and (set(lines[j].strip()) <= {"-", ""} and lines[j].strip()):
                j += 1
            name = ""
            blanks = 0
            while j < len(lines) and blanks < 6:   # a page break inside a table adds three or four blank lines
                ln = lines[j]
                s = ln.strip()
                if s.startswith("[[Page") or not s:
                    blanks += (not s)
                    j += 1
                    continue
                blanks = 0
                if set(s) <= {"-"}:
                    break
                m = ROW.match(ln)
                if m:
                    out.append(((name + " " + m.group("name")).strip(),
                                float(m.group("r1").replace(",", ""))))
                    name = ""
                else:
                    name = (name + " " + s)[-200:]
                j += 1
            i = j
        else:
            i += 1
    return out


def rate(doc):
    t = open(f"events/raw/{doc}.txt", errors="ignore").read()
    rows = tables(t)
    if not rows:
        return None, "", None
    ok = [(n, r) for n, r in rows if r <= 500 or OTHERS.search(n) or ENTITY.search(n)]
    if not ok:
        return None, "", None
    others = [r for n, r in ok if OTHERS.search(n)]
    entity = [r for n, r in ok if ENTITY.search(n) and not OTHERS.search(n)]
    mx = max(r for _, r in ok)
    if others:
        return others[-1], "all_others", mx
    if entity:
        return max(entity), "entity", mx
    return mx, "table_max", mx


if __name__ == "__main__":
    e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
    pre = e[e.stage == "preliminary"].drop_duplicates("document_number")
    rows = []
    for d in pre.document_number:
        r, src, mx = rate(d)
        rows.append(dict(document_number=d, rate=r, rate_src=src, rate_max=mx))
    out = pd.DataFrame(rows)
    out.to_csv("events/adcvd_margins.csv", index=False)
    print(out.rate_src.replace("", "none").value_counts())
    print(out.rate.describe().round(2))
    print("wrote events/adcvd_margins.csv")
