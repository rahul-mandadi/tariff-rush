# tariff-rush

**Borrowed or Real: Forecasting Import Surges Around U.S. Tariffs**

Rahul Reddy Mandadi, Raunaksingh Khalsa
DS 5500 Data Science Capstone, Northeastern University, Fall 2026

## Summary

United States tariffs are announced with a published effective date, which creates a window in
which importers can accelerate shipments to clear customs before the duty applies. This behavior,
known as front-loading, is followed by an extended period of below-normal imports.

The difficulty is not seeing the surge. Terminals and carriers can see roughly three weeks ahead
from security and manifest filings. The difficulty is that they commit capacity on horizons
measured in months, and nothing in that forward view says whether volume returns after a surge.
That turns on whether the surge was inventory borrowed from later months or a genuine rise in
demand, which the import series does not resolve until long after the commitment is made.

This project forecasts, using only information available on the day a tariff is announced, whether
the months following the effective date represent temporary payback of borrowed volume or a
durable reduction in demand. Two supporting quantities feed it, since any repayment is bounded by
what was borrowed: whether a surge occurs at all, and how large it is.

## Status

Exploratory phase complete. The repository is being restructured as a numbered pipeline before
modeling begins.

Established during exploration, to be rebuilt inside the new pipeline:

- A monthly U.S. import panel from the Census international trade API: 1,035,855
  product-partner-month observations, 139 months (2015-01 to 2026-07), 98 HS chapters, 234
  partners, with weight split by air, vessel and containerized movement.
- A counterfactual built from robust STL on pre-event data only, applied across 97 chapters. In
  the first half of 2025, 31 chapters exceeded their own tolerance band, led by lead, cocoa, tin,
  aluminum and copper.
- An episode detector using a leak-free trailing baseline: 11,178 surge episodes across 5,007
  product-partner cells. By repayment ratio, 52 percent are real increases, 35 percent were
  borrowed, 13 percent fall between.
- A tariff event table built from 2,792 Federal Register documents since 2018, of which 134 are
  tariff actions and 2,658 are rejected with a stated reason. Of the 134, 68 are scope changes,
  leaving 66 genuine actions: 47 Section 232, 30 Section 301, 27 IEEPA.

## Planned structure

```
01_acquire_census.py     raw Census monthly pulls
02_acquire_fedreg.py     raw Federal Register documents
03_build_panel.py        tidy monthly import panel
04_build_events.py       deduplicated tariff events with dates, authority, rate
05_build_coverage.py     event x chapter x partner treatment map
06_build_labels.py       surge occurrence, magnitude, reversal ratio
07_build_features.py     announcement-day features only
08_split.py              leave-one-event-out splits, frozen before modeling
09_model_*.py            hurdle model and aftermath classifier
```

Large raw caches are not tracked and are rebuilt by stages 01 and 02.

## Known open problems

1. Tariff events carry HTS Chapter 99 surcharge codes rather than product chapters, so they do not
   yet join to the import panel. Resolving 9903 codes to covered product chapters is the blocking
   task.
2. Partner extraction conflates the included set with the exception set.
3. Documents are not yet deduplicated into distinct events.
4. Census shipping weight covers air and vessel only. For aluminum in 2024 this leaves roughly 69
   percent of Canadian and 97 percent of Mexican tonnage unobserved, and those partners are 48
   percent of aluminum import value. BTS TransBorder closes the gap and is not yet integrated.

## Data sources

Census international trade API, Global Trade Alert, WTO-IMF Tariff Tracker, BTS TransBorder, IMF
PortWatch, University of Michigan Surveys of Consumers. All public and free for research use.
