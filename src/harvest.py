"""Pull monthly US imports from the Census international trade API.

One API call per month at HS2 x partner level, from 2015 onward. Each month is
cached as its own gzip in data/raw/census_hs2/, so a rerun skips months already
on disk. Stops at the first month Census has not published yet.

Needs a Census API key in CENSUS_API_KEY
(free: https://api.census.gov/data/key_signup.html).
"""
import gzip
import json
import os
import sys
import time
import urllib.request
from datetime import date

from paths import RAW_HS2

API = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
FIELDS = ("CTY_CODE,CTY_NAME,I_COMMODITY,GEN_VAL_MO,"
          "AIR_WGT_MO,VES_WGT_MO,CNT_WGT_MO,SUMMARY_LVL")
START_YEAR = 2015
MIN_ROWS = 50       # a published HS2 month has thousands of rows
TIMEOUT_S = 420     # full-partner HS2 queries are slow
TRIES = 3


def months(start_year):
    for year in range(start_year, date.today().year + 1):
        for month in range(1, 13):
            yield year, month


def fetch_month(key, year, month):
    """Download one month into RAW_HS2. Returns (status, rows fetched)."""
    path = RAW_HS2 / f"{year}-{month:02d}.json.gz"
    if path.exists() and path.stat().st_size > 2000:
        return "cached", 0
    url = (f"{API}?get={FIELDS}&YEAR={year}&MONTH={month:02d}"
           f"&COMM_LVL=HS2&I_COMMODITY=*&CTY_CODE=*&key={key}")
    for attempt in range(TRIES):
        try:
            body = urllib.request.urlopen(url, timeout=TIMEOUT_S).read()
            # Months not yet published come back empty or nearly empty.
            rows = json.loads(body) if body.strip() else []
        except Exception as e:  # timeouts, connection resets, truncated JSON
            if attempt == TRIES - 1:
                return f"error: {str(e)[:60]}", 0
            time.sleep(10 + 10 * attempt)
            continue
        if len(rows) < MIN_ROWS:
            return "empty", 0
        with gzip.open(path, "wt") as f:
            json.dump(rows, f)
        return "ok", len(rows) - 1


def main():
    key = os.environ.get("CENSUS_API_KEY")
    if not key:
        sys.exit("Set CENSUS_API_KEY "
                 "(free key: https://api.census.gov/data/key_signup.html)")
    RAW_HS2.mkdir(parents=True, exist_ok=True)

    fetched = total = 0
    for year, month in months(START_YEAR):
        status, n = fetch_month(key, year, month)
        label = f"{year}-{month:02d}"
        if status == "empty":
            print(f"{label}  not published yet, stopping", flush=True)
            break
        if status == "ok":
            fetched += 1
            total += n
            print(f"{label}  {n:>7,} rows   (cumulative {total:,})", flush=True)
        else:
            print(f"{label}  {status}", flush=True)
        if status != "cached":
            time.sleep(1)
    print(f"\nDone: {fetched} months fetched, {total:,} rows")


if __name__ == "__main__":
    main()
