"""Flatten the monthly Census gzips into one tidy HS2 x partner panel.

Keeps single-country rows (SUMMARY_LVL == DET, which drops country groupings),
drops the all-countries total and rows with no value and no weight, then prints
sanity checks. Writes data/interim/imports_hs2_panel.csv.
"""
import collections
import csv
import gzip
import json
import sys

from paths import PANEL_HS2, RAW_HS2

NUMERIC = ("GEN_VAL_MO", "AIR_WGT_MO", "VES_WGT_MO", "CNT_WGT_MO")
COLUMNS = ["year", "month", "cty_code", "cty_name", "chapter",
           "value_usd", "air_kg", "ves_kg", "cnt_kg"]


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def read_month(path):
    """Return (rows read, tidy rows kept) for one monthly gzip."""
    year, month = path.name.removesuffix(".json.gz").split("-")
    with gzip.open(path, "rt") as f:
        header, *rows = json.load(f)
    col = {name: i for i, name in enumerate(header)}
    kept = []
    for row in rows:
        if row[col["SUMMARY_LVL"]] != "DET":
            continue
        name = (row[col["CTY_NAME"]] or "").strip()
        if name == "TOTAL FOR ALL COUNTRIES":
            continue
        chapter = (row[col["I_COMMODITY"]] or "").strip()
        if len(chapter) != 2:
            continue
        values = [to_int(row[col[k]]) for k in NUMERIC]
        if not any(values):
            continue
        kept.append([year, month, row[col["CTY_CODE"]], name, chapter, *values])
    return len(rows), kept


def main():
    files = sorted(RAW_HS2.glob("*.json.gz"))
    if not files:
        sys.exit(f"No monthly files in {RAW_HS2}; run harvest.py first.")
    print(f"monthly files on disk: {len(files)}")

    PANEL_HS2.parent.mkdir(parents=True, exist_ok=True)
    n_read = n_kept = 0
    chapters, partners = set(), set()
    value_by_month = collections.Counter()
    with open(PANEL_HS2, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        for path in files:
            n, rows = read_month(path)
            writer.writerows(rows)
            n_read += n
            n_kept += len(rows)
            for year, month, _, name, chapter, value, *_ in rows:
                chapters.add(chapter)
                partners.add(name)
                value_by_month[f"{year}-{month}"] += value

    months = sorted(value_by_month)
    print(f"rows read   : {n_read:,}")
    print(f"rows kept   : {n_kept:,}")
    print(f"months      : {len(months)}  ({months[0]} to {months[-1]})")
    print(f"chapters    : {len(chapters)}")
    print(f"partners    : {len(partners)}")
    print("\ntotal US imports per month, sanity check (expect ~$200-300B):")
    for ym in months[:2] + months[-3:]:
        print(f"  {ym}  ${value_by_month[ym] / 1e9:,.0f}B")
    print(f"\npanel written: {PANEL_HS2}  ({PANEL_HS2.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
