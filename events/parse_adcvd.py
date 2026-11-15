"""Read each duty notice: its stage, case number, country, products and dates.

Reads:  events/adcvd_index.json, events/raw/, panel/hs8/2024-06.parquet (country names)
Writes: events/adcvd_events.csv, events/adcvd_products.csv
Run:    python3 events/parse_adcvd.py      (after events/harvest_adcvd.py)
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



# ---------------------------------------------------------------- critical circumstances
# Commerce writes its own finding with the phrase in lower case ("critical circumstances do not
# exist for ..."); names of other cases it cites carry it in Title Case ("...Affirmative
# Preliminary Determination of Critical Circumstances, 79 FR 1234"), so those are not read.
# Sentences that only report an allegation, quote the statute or describe a later step are skipped.
# Until November 2026 one pattern read the whole text and was wrong both ways: "critical
# circumstances do not exist" counted as affirmative, and so did any cited title or allegation.
CC = r"(?:critical|Critical) circumstances"
CC_SKIP = re.compile(r"\balleg|\bwhether\b|provides that|\bwill (?:preliminarily )?determine\b"
                     r"|\bmay exist\b|\brequest", re.I)
CC_VERB = re.compile(r"\b(?:find|finds|found|finding|determine|determines|determined|reached|"
                     r"determination)\b", re.I)
CC_NEG = re.compile(rf"{CC} (?:do|does|did) not exist|not (?:find|found|determine) that {CC} exist"
                    rf"|\bnegative\b[^.]{{0,40}}{CC}|{CC}[^.]{{0,15}}\bnegative\b|\bno {CC}"
                    r"|\b(?:do|does|did) not exist\b")
CC_AFF = re.compile(rf"{CC} (?:do |does |did )?exist(?:s|ed)?\b|\b(?:they|it) do(?:es)? exist\b"
                    r"|\b(?:but|while|and) do(?:es)? exist\b"
                    rf"|\baffirmative\b[^.]{{0,40}}{CC}|{CC}[^.]{{0,15}}\baffirmative\b"
                    rf"|reason to believe or suspect that {CC} exist")
CC_TITLE_NEG = re.compile(r"Negative (?:Preliminary )?(?:Determinations? (?:of )?)?Critical Circumstances", re.I)
CC_TITLE_AFF = re.compile(r"Affirmative (?:Preliminary )?(?:Determinations? (?:of )?)?Critical Circumstances", re.I)
# words a notice uses for a country whose panel name differs
CC_WORDS = {"CHINA": ["China", "PRC", "Chinese"], "KOREA, SOUTH": ["Korea", "Korean"], "RUSSIA": ["Russia"],
            "TURKEY": ["Turkey", "Türkiye", "Turkiye"], "UNITED ARAB EMIRATES": ["United Arab Emirates", "UAE"],
            "BOSNIA AND HERZEGOVINA": ["Bosnia"], "VIETNAM": ["Vietnam"]}


def cc_sentences(txt):
    # footnote markers (\9\) and rule lines (-----) glue sentences together; break on them first
    txt = re.sub(r"-{5,}", ". ", re.sub(r"\\\d+\\", " ", re.sub(r"\s+", " ", txt)))
    return re.split(r"(?<=[.;])\s+(?=[A-Z(`'\[])", txt)


def cc_names(country, text):
    words = CC_WORDS.get(country, [country.title().split(",")[0]])
    return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)


def critical_findings(txt, title, countries):
    """This notice's own critical-circumstances finding for each country: "affirmative",
    "negative", "mixed" (affirmative for some exporters, negative for others) or "none".
    With several countries in one notice, a clause counts only for the countries it names."""
    multi = len(countries) > 1
    found = {c: [False, False] for c in countries}
    for s in cc_sentences(txt):
        if not re.search(CC, s) or CC_SKIP.search(s) or not CC_VERB.search(s):
            continue
        parts = re.split(r";|\bwhile\b|\bbut\b|,? and (?=(?:that )?(?:they |critical circumstances )?(?:do|does|did) not\b)",
                         s) if multi else [s]
        for part in parts:
            neg = bool(CC_NEG.search(part))
            aff = bool(CC_AFF.search(CC_NEG.sub("", part)))
            for c in ([c for c in countries if cc_names(c, part)] if multi else countries):
                found[c][0] |= aff
                found[c][1] |= neg
    if not multi and countries:
        t = re.sub(r"\s+", " ", title)
        ta, tn = bool(CC_TITLE_AFF.search(t)), bool(CC_TITLE_NEG.search(t))
        c = countries[0]
        found[c][0] |= ta
        found[c][1] |= tn or (ta and bool(re.search(r"in part", t, re.I)))
    return {c: "mixed" if a and n else "affirmative" if a else "negative" if n else "none"
            for c, (a, n) in found.items()}


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
        retro = bool(re.search(r"90 days (?:prior|before)|retroactiv", txt, re.I))

        named = countries_of(title, name2cty)
        finding = critical_findings(raw, title, [n for n in named if not isinstance(n, tuple)])
        for nm in named:
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
                             critical_circ=crit, critical_affirm=finding[nm] in ("affirmative", "mixed"),
                             critical_finding=finding[nm], retroactive=retro,
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
