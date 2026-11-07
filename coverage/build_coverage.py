"""Map each HTS chapter 99 surcharge code to the products and countries it covers.

A surcharge code says a duty exists. What it applies to is either written in the code's own
description or delegated to a U.S. note published separately. Chapter 99 has several subchapters
with independent note numbering, and the tariff actions live in subchapter III, so notes are
parsed within that span only.

Outputs
  coverage/surcharge_codes.csv   one row per 9903 code: rate, countries, note reference, status
  coverage/coverage_map.csv      one row per 9903 code and HS chapter it touches
  coverage/unresolved.csv        codes whose product scope could not be determined
"""
import json, re
import pandas as pd

HS8    = re.compile(r"\b(\d{4})\.(\d{2})\.(\d{2})\b")
# two reference styles appear: "U.S. note 20(b)" and "subdivision (c) of U.S. note 16".
# the second may name a range, "subdivisions (c)(i)-(v)", which still resolves to subdivision (c).
NOTEREF_A = re.compile(r"U\.S\.\s+note\s+(\d{1,2})\(([a-z]{1,3})\)")
NOTEREF_B = re.compile(r"subdivisions?\s+((?:\([a-z]{1,3}\)(?:\([ivx]+\))?[^a-z]{0,6})+)of\s+U\.S\.\s+note\s+(\d{1,2})")

def note_refs(desc):
    out = []
    for a, b in NOTEREF_A.findall(desc or ""):
        out.append((int(a), b))
    for subs, num in NOTEREF_B.findall(desc or ""):
        for letter in re.findall(r"\(([a-z]{1,3})\)", subs):
            if letter not in ("i","ii","iii","iv","v","vi","vii","viii","ix","x"):
                out.append((int(num), letter))
    seen, uniq = set(), []
    for k in out:
        if k not in seen: seen.add(k); uniq.append(k)
    return uniq
COUNTRY = re.compile(r"products?\s+of\s+([A-Z][A-Za-z\- ]{2,40}?)(?=[,;\.\s]|\s+that|\s+as|\s+which|$)")

def subchapter_iii(text):
    heads = [(m.start(), m.group(1)) for m in re.finditer(r"\n\s*SUBCHAPTER\s+([IVX]+)\s*\n", text)]
    for i, (pos, num) in enumerate(heads):
        if num == "III":
            end = heads[i+1][0] if i+1 < len(heads) else len(text)
            return text[pos:end]
    raise RuntimeError("subchapter III not found")

def parse_notes(span):
    """{(number, letter): body}. A numbered note opens at 'N. (a)' and runs to the next one;
    inside it, lettered paragraphs are bounded by the next lettered paragraph."""
    # a note opens with its number; some carry a title before the first lettered subdivision,
    # so accept any numbered line that has an "(a)" within reach.
    cand = [(m.start(), int(m.group(1))) for m in re.finditer(r"\n\s{0,12}(\d{1,2})\.\s+\S", span)]
    starts = [(pos, num) for pos, num in cand if "(a)" in span[pos:pos+3000]]
    notes = {}
    for i, (pos, num) in enumerate(starts):
        end = starts[i+1][0] if i+1 < len(starts) else len(span)
        body = span[pos:end]
        marks = [(m.start(), m.group(1))
                 for m in re.finditer(r"\n\s{0,12}(?:\d{1,2}\.\s+)?\(([a-z]{1,3})\)\s", body)]
        for j, (p, letter) in enumerate(marks):
            e = marks[j+1][0] if j+1 < len(marks) else len(body)
            notes.setdefault((num, letter), body[p:e])
    return notes

def products_in(body):
    return sorted({f"{a}.{b}.{c}" for a, b, c in HS8.findall(body) if not a.startswith("99")})

def rate_of(general):
    g = (general or "").strip()
    m = re.search(r"applicable subheading\s*(?:\+|plus)\s*(\d+(?:\.\d+)?)\s*%", g)
    if m: return float(m.group(1)), "additional"
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*%", g)
    if m: return float(m.group(1)), "absolute"
    if g.lower().startswith("free"): return 0.0, "absolute"
    return None, None

def countries_of(desc):
    out = []
    for c in COUNTRY.findall(desc or ""):
        c = c.strip().rstrip(",.")
        if c and c.lower() not in {"the", "a", "such"} and c not in out:
            out.append(c)
    return out

def main():
    codes = json.load(open("coverage/raw/hts99_codes.json"))
    text  = open("coverage/raw/hts99_notes.txt", errors="ignore").read()
    notes = parse_notes(subchapter_iii(text))
    print(f"subchapter III note sections parsed: {len(notes)}")

    rows, cov, unres = [], [], []
    for c in codes:
        h = (c.get("htsno") or "").strip()
        if not re.fullmatch(r"9903\.\d{2}\.\d{2}", h): continue
        desc = c.get("description") or ""
        rate, kind = rate_of(c.get("general"))
        ctys = countries_of(desc)
        refs = note_refs(desc)

        # a code often cites several notes: one defining the action, another enumerating
        # the subheadings. Take the richest list rather than the first non-empty one.
        prods, source = [], ""
        best = []
        for key in refs:
            if key in notes:
                p = products_in(notes[key])
                if len(p) > len(best):
                    best, source = p, f"note {key[0]}({key[1]})"
        prods = best
        if not prods:
            p = products_in(desc)
            if p: prods, source = p, "own description"

        chapters = sorted({x[:2] for x in prods})
        rows.append(dict(htsno=h, rate_pct=rate, rate_kind=kind, countries=";".join(ctys),
                         note_ref=";".join(f"{a}({b})" for a, b in refs),
                         n_products=len(prods), n_chapters=len(chapters), scope_source=source))
        for ch in chapters:
            cov.append(dict(htsno=h, chapter=ch,
                            n_products_in_chapter=sum(1 for x in prods if x[:2] == ch),
                            countries=";".join(ctys), rate_pct=rate, scope_source=source))
        if not chapters:
            unres.append(dict(htsno=h, rate_pct=rate, countries=";".join(ctys),
                              note_ref=";".join(f"{a}({b})" for a, b in refs),
                              has_note_ref=bool(refs), description=desc[:240]))

    r  = pd.DataFrame(rows);  r.to_csv("coverage/surcharge_codes.csv", index=False)
    cm = pd.DataFrame(cov);   cm.to_csv("coverage/coverage_map.csv", index=False)
    u  = pd.DataFrame(unres); u.to_csv("coverage/unresolved.csv", index=False)

    print(f"\nsurcharge codes           {len(r)}")
    print(f"  with a rate             {r.rate_pct.notna().sum()}")
    print(f"  naming a country        {(r.countries != '').sum()}")
    print(f"  product scope resolved  {(r.n_products > 0).sum()}")
    print(f"  unresolved              {len(u)}")
    if len(u):
        print(f"    of which referenced a note we could not match: {u.has_note_ref.sum()}")
    print(f"\ncoverage_map rows (code x chapter): {len(cm):,}   chapters touched: {cm.chapter.nunique()}")

    print("\nvalidation, Section 301 List 1 should be ~800 lines in chapters 28,40,84-90:")
    k = (20, "b")
    if k in notes:
        p = products_in(notes[k])
        print(f"  note 20(b): {len(p)} products, chapters {sorted({x[:2] for x in p})}")

    print("\nwidest-reaching codes:")
    for h, g in sorted(cm.groupby("htsno"), key=lambda kv: -len(kv[1]))[:6]:
        print(f"  {h}  {len(g):>2} chapters  {g.n_products_in_chapter.sum():>5} lines  "
              f"{(g.countries.iloc[0] or '(none named)')[:28]}")

if __name__ == "__main__":
    main()
