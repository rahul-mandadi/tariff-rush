"""Coverage rules for tariff actions that do not enumerate product lists.

Three authorities define scope three different ways:

  Section 301   enumerates HS8 subheadings in a U.S. note. Parsed directly; see build_coverage.py.
  Section 232   names a material or product class ("articles of aluminum"). The schedule itself
                states the core chapters: heading 9903.82.03 reads "Except for articles
                classifiable in chapters 72, 73, 74 or 76", which fixes the metals scope.
                Derivatives reach beyond those chapters and are listed separately.
  IEEPA         applies to a whole country with named carve-outs, so coverage is every chapter
                for that partner rather than a product list.

Each rule records where it comes from so it can be audited.
"""

# Section 232: surcharge prefix -> core HS chapters, with the source of the assignment
SECTION_232 = {
    "9903.82": dict(name="metals: aluminum, steel, copper",
                    chapters=["72", "73", "74", "76"],
                    source="9903.82.03 names chapters 72, 73, 74, 76 as the core scope"),
    "9903.85": dict(name="aluminum, Russia origin",
                    chapters=["76"],
                    source="description: aluminum articles, product of Russia"),
    "9903.91": dict(name="steel derivatives",
                    chapters=["72", "73"],
                    source="description: steel articles"),
    "9903.92": dict(name="steel derivatives",
                    chapters=["72", "73"],
                    source="description: steel articles"),
    "9903.94": dict(name="autos and light trucks",
                    chapters=["87"],
                    source="description: passenger vehicles, light trucks"),
    "9903.74": dict(name="medium and heavy duty vehicles",
                    chapters=["87"],
                    source="description: medium- and heavy-duty vehicles, buses"),
    "9903.76": dict(name="timber, lumber, furniture",
                    chapters=["44", "94"],
                    source="description: timber, lumber, furniture"),
    "9903.79": dict(name="semiconductors",
                    chapters=["85"],
                    source="description: semiconductors"),
    "9903.45": dict(name="solar safeguard (Section 201)",
                    chapters=["85"],
                    source="description: solar cells and modules"),
}

# IEEPA: surcharge prefix -> label. Coverage is country-wide, so chapters are resolved at join
# time as every chapter the partner actually ships, not a fixed list.
IEEPA = {
    "9903.01": "IEEPA, country-wide with carve-outs",
    "9903.02": "IEEPA reciprocal, country-wide",
    "9903.03": "IEEPA, country-wide",
    "9903.05": "IEEPA, country-wide",
}

# Chapters that are not products and must never be treated as outcomes.
EXCLUDE_CHAPTERS = {
    "98": "US goods returned, personal exemptions and similar accounting categories",
    "99": "the tariff surcharges themselves",
}

def classify(htsno):
    """Return (mechanism, detail) for a 9903 code: ENUMERATED, MATERIAL_CLASS or COUNTRY_WIDE."""
    pref = htsno[:7]
    if pref in SECTION_232: return "MATERIAL_CLASS", SECTION_232[pref]
    if pref in IEEPA:       return "COUNTRY_WIDE",   {"name": IEEPA[pref]}
    return "ENUMERATED", {}
