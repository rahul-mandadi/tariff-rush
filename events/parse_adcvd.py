"""Parse antidumping and countervailing duty notices into tariff events with windows.

These are the largest source of product-specific, single-country tariff actions available,
and the project needs them: 21 Section 232/301/IEEPA events is too few to estimate repayment,
and their median announcement-to-effective window is days, which monthly data cannot resolve.
An AD/CVD case runs for months between becoming public and duties being collected.

What is extracted
  case number   A-570-053 / C-580-891. Letter is the programme, middle three digits
                Commerce's country code, so it links the stages of one case.
  stage         initiation -> preliminary -> final -> order. The preliminary determination
                is when duties start being collected, so it is the operative date.
  initiation    read out of the preliminary notice's own background section, because the
                initiation notice itself often falls outside the harvest window. Text is
                whitespace-normalised first: the source is hard-wrapped, which splits dates
                across lines and otherwise loses a third of them.
  scope         HTSUS numbers in the notice, truncated to HS8 to match the panel.
  country       from the title, which reads "<Product> From <Country>: <Action>". Titles
                naming several countries are split, since each is a separate treatment.

Outputs
  events/adcvd_events.csv     one row per document: case, stage, country, dates, window
  events/adcvd_products.csv   one row per document and HS8 line

Usage:  python3 events/parse_adcvd.py      # from the repo root
"""
import json, os, re
import pandas as pd
from dateutil import parser as dp

CASE = re.compile(r"\b([AC])-(\d{3})-(\d{3})\b")
HTS = [re.compile(r"\b(\d{4})\.(\d{2})\.(\d{2})\.(\d{2})\b"),
       re.compile(r"\b(\d{4})\.(\d{2})\.(\d{4})\b"),
       re.compile(r"\b(\d{4})\.(\d{2})\.(\d{2})\b(?!\.\d)")]
FROM = re.compile(r"\bFrom\s+(.+?)\s*(?=[:;]|$)")
D = r"([A-Z][a-z]+ \d{1,2}, \d{4})"
INIT = [rf"[Cc]ommerce initiated[^.]{{0,180}}?on {D}",
        rf"[Oo]n {D},[^.]{{0,80}}?Commerce initiated",
        rf"initiat\w+[^.]{{0,120}}?on {D}",
        rf"[Pp]etitions? (?:were|was) filed[^.]{{0,100}}?on {D}",
        rf"[Ii]nitiation [Nn]otice[^.]{{0,180}}?{D}",
        # the Background section usually opens by dating the initiation or the petition
        rf"[Bb]ackground[^.]{{0,200}}?on {D}",
        rf"[Tt]his investigation was initiated[^.]{{0,120}}?{D}",
        rf"{D}[^.]{{0,60}}?Commerce published[^.]{{0,60}}?initiation",
        rf"[Ss]ee [^.]{{0,80}}?Initiation[^.]{{0,120}}?{D}"]

KEEP = re.compile(
    r"(Preliminary\s+Determination|Affirmative\s+Preliminary|Preliminary\s+Affirmative"
    r"|Final\s+Determination|Final\s+Affirmative"
    r"|Antidumping\s+Duty\s+Order|Countervailing\s+Duty\s+Order"
    r"|Antidumping\s+and\s+Countervailing\s+Duty\s+Orders"
    r"|Initiation\s+of\s+Less-Than-Fair-Value|Initiation\s+of\s+Countervailing\s+Duty)", re.I)
DROP = re.compile(r"Administrative\s+Review|Sunset\s+Review|Changed\s+Circumstances"
                  r"|Scope\s+Ruling|Opportunity\s+to\s+Request", re.I)

STAGES = [("order", r"Antidumping Duty Order|Countervailing Duty Order|"
                    r"Antidumping and Countervailing Duty Orders"),
          ("initiation", r"Initiation of"),
          ("preliminary", r"Preliminary Determination|Affirmative Preliminary|"
                          r"Preliminary Affirmative"),
          ("final", r"Final Determination|Final Affirmative")]

# names that legitimately contain "and", protected before the title is split
COMPOUND = ["Trinidad and Tobago", "Bosnia and Herzegovina", "Antigua and Barbuda",
            "Saint Kitts and Nevis", "Saint Vincent and the Grenadines",
            "Sao Tome and Principe", "Turks and Caicos Islands",
            "Heard Island and McDonald Islands", "Svalbard and Jan Mayen",
            "Wallis and Futuna", "Saint Pierre and Miquelon"]
# leading formal styling that the panel's names do not carry
STYLE = re.compile(
    r"^(the\s+)?((socialist|federative|federal|bolivarian|islamic|argentine|italian|"
    r"french|portuguese|hellenic|oriental|co-?operative|plurinational|arab|dominican|"
    r"eastern|lao people's democratic|people's democratic|people's)\s+)?"
    r"(republic|kingdom|state|states|commonwealth|sultanate|principality|emirate|"
    r"union|federation|territory)\s+of\s+", re.I)

ALIAS = {
    "people's republic of china": "CHINA", "people’s republic of china": "CHINA",
    "republic of korea": "KOREA, SOUTH", "korea": "KOREA, SOUTH",
    "socialist republic of vietnam": "VIETNAM", "social republic of vietnam": "VIETNAM",
    "republic of turkey": "TURKEY", "turkiye": "TURKEY", "republic of turkiye": "TURKEY",
    "türkiye": "TURKEY", "republic of türkiye": "TURKEY", "south korea": "KOREA, SOUTH",
    "peoples's republic of china": "CHINA", "people's republic": "CHINA",
    "russian federation": "RUSSIA", "kingdom of thailand": "THAILAND",
    "sultanate of oman": "OMAN", "republic of india": "INDIA",
    "federative republic of brazil": "BRAZIL", "united mexican states": "MEXICO",
    "republic of south africa": "SOUTH AFRICA", "kingdom of spain": "SPAIN",
    "italian republic": "ITALY", "republic of indonesia": "INDONESIA",
    "kingdom of morocco": "MOROCCO", "federal republic of germany": "GERMANY",
    "kingdom of saudi arabia": "SAUDI ARABIA", "arab republic of egypt": "EGYPT",
    "sultanate of brunei": "BRUNEI", "republic of chile": "CHILE",
    "separate customs territory of taiwan, penghu, kinmen and matsu": "TAIWAN",
    "united kingdom of great britain and northern ireland": "UNITED KINGDOM",
}


def stage_of(t):
    for n, rx in STAGES:
        if re.search(rx, t, re.I):
            return n
    return None


def countries_of(title, name2cty):
    """Split a title's country list and resolve each name to a Schedule C code."""
    m = FROM.search(title)
    if not m:
        return []
    chunk = re.split(r"\s*:\s*", m.group(1))[0]
    # protect multi-word names containing "and" so the split below does not break them
    holds = {}
    for i, c in enumerate(COMPOUND):
        if re.search(re.escape(c), chunk, re.I):
            tok = f"@@{i}@@"
            chunk = re.sub(re.escape(c), tok, chunk, flags=re.I)
            holds[tok] = c
    parts = re.split(r",\s*and\s+|\s+and\s+|,\s*", chunk)

    out = []
    for p in parts:
        p = p.strip()
        for tok, full in holds.items():          # a token can sit inside "Republic of X"
            p = p.replace(tok, full)
        p = p.strip(" .;")
        p = re.sub(r"^the\s+", "", p, flags=re.I).strip()
        if not p or len(p) > 70:
            continue
        # try, in order: alias table, the name as written, the name with formal
        # styling stripped ("Republic of Armenia" -> "Armenia")
        for cand in (ALIAS.get(p.lower()), p.upper(), STYLE.sub("", p).strip().upper()):
            if cand and cand in name2cty:
                if cand not in out:
                    out.append(cand)
                break
        else:
            out.append(("?", p.upper()))
    return out


def codes_in(txt):
    out = set()
    for rx in HTS:
        for m in rx.finditer(txt):
            g = "".join(m.groups())
            if len(g) >= 8 and not g.startswith("99"):
                out.add(g[:8])
    return out


def init_date(txt, pub):
    for rx in INIT:
        m = re.search(rx, txt)
        if m:
            try:
                d = pd.Timestamp(dp.parse(m.group(1)))
                if pd.Timestamp("2005-01-01") < d < pub:
                    return d
            except Exception:
                pass
    return None


def main():
    idx = json.load(open("events/adcvd_index.json"))
    docs = [d for d in idx
            if KEEP.search(d.get("title") or "") and not DROP.search(d.get("title") or "")]
    print(f"ITA notices indexed: {len(idx):,}   duty-starting stages: {len(docs):,}")

    pan = pd.read_parquet("panel/hs8/2024-06.parquet", columns=["cty", "cty_name"]).drop_duplicates()
    name2cty = dict(zip(pan.cty_name, pan.cty))

    rows, prods, miss = [], [], []
    no_text = 0
    for d in docs:
        dn = d["document_number"]
        p = f"events/raw/{dn}.txt"
        if not os.path.exists(p):
            no_text += 1
            continue
        raw = open(p, errors="ignore").read()
        txt = re.sub(r"\s+", " ", raw)
        title = d.get("title") or ""
        pub = pd.Timestamp(d["publication_date"])

        stage = stage_of(title)
        hs8 = codes_in(raw)
        cases = sorted({f"{a}-{b}-{c}" for a, b, c in CASE.findall(txt)})
        ini = init_date(txt, pub) if stage in ("preliminary", "order", "final") else None
        # AD/CVD duties can reach back 90 days before suspension of liquidation, or to the
        # initiation notice, whichever is later. Where Commerce finds critical circumstances
        # the whole front-loading window is exposed, so buying ahead is taxed anyway. This
        # flag lets the rush be compared across cases that do and do not carry that risk.
        crit = bool(re.search(r"critical circumstances", txt, re.I))
        crit_aff = bool(re.search(r"critical circumstances (?:do |does )?(?!do not|does not)"
                                  r"[^.]{0,60}?(?:exist|affirmative)|affirmative[^.]{0,40}?"
                                  r"critical circumstances", txt, re.I))
        retro = bool(re.search(r"90 days (?:prior|before)|retroactiv", txt, re.I))

        for nm in countries_of(title, name2cty):
            if isinstance(nm, tuple):
                miss.append(nm[1])
                continue
            cty = name2cty.get(nm)
            if not cty:
                miss.append(nm)
                continue
            rows.append(dict(document_number=dn, title=title[:110], stage=stage,
                             case=cases[0] if cases else "", n_cases=len(cases),
                             country=nm, cty=cty, n_hs8=len(hs8),
                             critical_circ=crit, critical_affirm=crit_aff, retroactive=retro,
                             publication_date=pub.date(),
                             initiation_date=ini.date() if ini is not None else None,
                             window_days=(pub - ini).days if ini is not None else None))
        for h in sorted(hs8):
            prods.append(dict(document_number=dn, hs8=h))

    e = pd.DataFrame(rows)
    pr = pd.DataFrame(prods).drop_duplicates()
    e.to_csv("events/adcvd_events.csv", index=False)
    pr.to_csv("events/adcvd_products.csv", index=False)

    print(f"documents without cached text: {no_text}")
    print(f"\ndocument x country rows: {len(e):,}   documents: {e.document_number.nunique():,}")
    print(f"  distinct cases:     {e[e.case != ''].case.nunique():,}")
    print(f"  distinct countries: {e.cty.nunique()}")
    print(f"  distinct HS8 lines: {pr.hs8.nunique():,}")
    print("\nby stage (document x country rows):")
    print(e.stage.value_counts(dropna=False).to_string())

    w = e[e.window_days.notna() & (e.stage == "preliminary")]
    print(f"\npreliminary determinations: {(e.stage=='preliminary').sum():,} rows, "
          f"{w.shape[0]:,} with an initiation date "
          f"({100*w.shape[0]/max(1,(e.stage=='preliminary').sum()):.0f}%)")
    if len(w):
        print("window days:")
        print(w.window_days.describe(percentiles=[.25, .5, .75]).round(0).to_string())
    if miss:
        print("\ntop unmatched country strings:")
        print(pd.Series(miss).value_counts().head(8).to_string())


if __name__ == "__main__":
    main()
