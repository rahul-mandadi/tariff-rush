# tariff-rush

**Borrowed or Real: Forecasting Import Surges Around U.S. Tariffs**

Rahul Reddy Mandadi, Raunaksingh Khalsa
DS 5500 Data Science Capstone, Northeastern University, Fall 2026

## Summary

United States tariffs are announced with a published effective date, which creates a window in
which importers can accelerate shipments to clear customs before the duty applies. This behavior,
known as front-loading, is followed by an extended period of below-normal imports, and the two
together are consequential for everyone downstream of the importer.

The difficulty is not seeing the surge. Terminals and carriers can see roughly three weeks ahead
from vessel schedules and manifest filings. The difficulty is that they commit longshore labor,
chassis and yard space on horizons of one to six months, and nothing in that forward view says
whether volume returns after a surge. That turns on whether the surge was inventory borrowed from
later months or a genuine rise in demand, which the import series does not resolve until long
after the commitment is made.

This project forecasts, using only information available on the day a tariff is announced, whether
the months following the effective date represent temporary payback of borrowed volume or a
durable reduction in demand. Two supporting quantities feed it, since any repayment is bounded by
what was borrowed: whether a surge occurs at all, and how large it is.

Across 11,178 surge episodes detected since 2015, 52 percent give back less than twenty percent of
the surge and are real increases, 35 percent give back more than sixty percent and were borrowed,
and 13 percent fall between. Roughly one surge in three is repaid, and the two kinds are not
distinguishable from the opening months of an episode.

## Data

| Source | Role |
| --- | --- |
| U.S. Census Bureau international trade API | monthly imports by product and partner, the outcome |
| Global Trade Alert | tariff events with announcement and effective dates |
| WTO-IMF Tariff Tracker | cross-check on rates and start dates |
| BTS TransBorder | truck and rail weight from Canada and Mexico, which Census omits |
| IMF PortWatch | daily port calls, within-month timing |
| University of Michigan Surveys of Consumers | independent corroboration of anticipatory buying |

All sources are public and free for research use.

## Pipeline

```
harvest.py    one Census API call per month, checkpointed to gzip per month
assemble.py   flatten to a tidy monthly panel
decomp.py     robust STL counterfactual, fit on pre-announcement data only
surges.py     episode detection and repayment-ratio labels
```

`harvest.py` reads a Census API key from the `CK` environment variable.

The panel is 1,035,855 rows covering 139 months (2015-01 to 2026-07), 98 HS chapters and 234
partners. `imports_hs2_panel.csv` is about 47 MB and is not tracked here; run `harvest.py` then
`assemble.py` to rebuild it. The derived outputs `anomalies_kg.csv` and `surge_events.csv` are
tracked.

Known issue: `harvest.py` and `decomp.py` currently expect a `panel/` subdirectory while the
committed CSVs sit at the repository root. Paths are being unified.

## Method

For each product-partner series, a seasonal-trend decomposition using LOESS (STL) is fit on log
volume using only data preceding the announcement date, and refit at every forecast origin, so a
surge cannot contaminate the baseline it is measured against. The trend is extrapolated from its
last 36 months and recombined with a seasonal profile averaged over three cycles, giving a
counterfactual path and a tolerance band.

The aftermath label follows from an accounting argument: volume pulled forward is repaid out of
the same inventory, so the cumulative deficit over the nine months after an episode is computed as
a fraction of the excess during it. A ratio near one that then flattens is payback; a deficit
running past the size of the surge means the demand level changed.

Because distinct tariff events number in the dozens, evaluation holds out whole events rather than
random months, since two months from the same action are not independent.

## Status

Panel built and validated. Counterfactual and episode labels implemented. Tariff event table,
TransBorder integration and modeling are in progress.
