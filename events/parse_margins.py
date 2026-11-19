"""Read the preliminary duty rate from each notice's rate table.

Uses the rate for all other exporters, or the country-wide rate.

Reads:  events/adcvd_events.csv, events/raw/
Writes: events/adcvd_margins.csv
Run:    python3 events/parse_margins.py      (after events/parse_adcvd.py)
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
