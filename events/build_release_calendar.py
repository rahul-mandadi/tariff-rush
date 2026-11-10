"""Census release date of each month's detailed trade data (FT-900), for "published by the decision".

Source: ALFRED (St. Louis Fed), vintage dates of series BOPGSTB, the trade balance published in each
FT-900 release (https://alfred.stlouisfed.org/series?seid=BOPGSTB, read 2026-11-07). Each release adds
one new data month, in order. ALFRED has no vintage for the March 2020 release; it was May 5, 2020
(BEA 20-21 / CB 20-66, archived on FRASER as bea_newsreleases_20200505). Gaps in the list are real:
no release in January 2019 or October 2025 (federal shutdowns), with catch-up releases after.
Months before October 2014 are assumed released on day 5 of month m + 2; no decision in the
project depends on them.

Usage:  python3 events/build_release_calendar.py      # writes census_release_calendar.csv
"""
import pandas as pd

RELEASES = """2014-12-05 2015-01-07 2015-02-05 2015-03-06 2015-04-02 2015-05-05 2015-06-03 2015-07-07 2015-08-05
2015-09-03 2015-10-06 2015-11-04 2015-12-04 2016-01-06 2016-02-05 2016-03-04 2016-04-05 2016-05-04 2016-06-03
2016-07-06 2016-08-05 2016-09-02 2016-10-05 2016-11-04 2016-12-06 2017-01-06 2017-02-07 2017-03-07 2017-04-04
2017-05-04 2017-06-02 2017-07-06 2017-08-04 2017-09-06 2017-10-05 2017-11-03 2017-12-05 2018-01-05 2018-02-06
2018-03-07 2018-04-05 2018-05-03 2018-06-06 2018-07-06 2018-08-03 2018-09-05 2018-10-05 2018-11-02 2018-12-06
2019-02-06 2019-03-06 2019-03-27 2019-04-17 2019-05-09 2019-06-06 2019-07-03 2019-08-02 2019-09-04 2019-10-04
2019-11-05 2019-12-05 2020-01-07 2020-02-05 2020-03-06 2020-04-02 2020-05-05 2020-06-04 2020-07-02 2020-08-05
2020-09-03 2020-10-06 2020-11-04 2020-12-04 2021-01-07 2021-02-05 2021-03-05 2021-04-07 2021-05-04 2021-06-08
2021-07-02 2021-08-05 2021-09-02 2021-10-05 2021-11-04 2021-12-07 2022-01-06 2022-02-08 2022-03-08 2022-04-05
2022-05-04 2022-06-07 2022-07-07 2022-08-04 2022-09-07 2022-10-05 2022-11-03 2022-12-06 2023-01-05 2023-02-07
2023-03-08 2023-04-05 2023-05-04 2023-06-07 2023-07-06 2023-08-08 2023-09-06 2023-10-05 2023-11-07 2023-12-06
2024-01-09 2024-02-07 2024-03-07 2024-04-04 2024-05-02 2024-06-06 2024-07-03 2024-08-06 2024-09-04 2024-10-08
2024-11-05 2024-12-05 2025-01-07 2025-02-05 2025-03-06 2025-04-03 2025-05-06 2025-06-05 2025-07-03 2025-08-05
2025-09-04 2025-11-19 2025-12-11 2026-01-08 2026-01-29 2026-02-19 2026-03-12 2026-04-02 2026-05-05 2026-06-09
2026-07-07 2026-08-04 2026-09-03 2026-10-06 2026-11-04""".split()
FIRST = 2014 * 12 + 9  # October 2014, the data month of the first listed release

rel = pd.to_datetime(RELEASES)
cal = pd.DataFrame({"m": range(FIRST, FIRST + len(rel)), "release": rel, "source": "ALFRED BOPGSTB vintage"})
cal.loc[cal.release == pd.Timestamp("2020-05-05"), "source"] = "BEA 20-21 / CB 20-66 (missing from ALFRED)"
early = pd.DataFrame({"m": range(2010 * 12, FIRST)})
early["release"] = [pd.Timestamp(year=(m + 2) // 12, month=(m + 2) % 12 + 1, day=5) for m in early.m]
early["source"] = "assumed day 5 of month m + 2 (no decision uses these)"
cal = pd.concat([early, cal], ignore_index=True)
cal["ref"] = [pd.Timestamp(year=m // 12, month=m % 12 + 1, day=1) for m in cal.m]
assert cal.release.is_monotonic_increasing
assert ((cal.release.dt.year * 12 + cal.release.dt.month - 1) - cal.m).between(1, 4).all()
cal[["m", "ref", "release", "source"]].to_csv("census_release_calendar.csv", index=False)
print(f"wrote census_release_calendar.csv: {len(cal)} months, last data month {cal.ref.iloc[-1]:%Y-%m}")
