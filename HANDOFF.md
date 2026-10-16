# What is already built

Orientation for a new contributor. Rewritten 2026-10-13.

The project asks, on the day a tariff is announced, whether the months after the effective date
are temporary payback of volume borrowed before it or a durable drop in demand. Two supporting
quantities feed that: whether a surge happens at all, and how big it is.

## The shape of the thing

Three pieces, all now built and joined:

1. **An import panel** at the product level tariffs are actually written at.
2. **A tariff event table**, from two sources, with dates and product scopes.
3. **A coverage map** connecting the two, which is what the first attempt was missing.

## 1. The import panel

```
harvest_hs10.py      -> panel/hs10/YYYY-MM.json.gz   one Census call per month, checkpointed
build_panel_hs8.py   -> panel/hs8/YYYY-MM.parquet    HS8 x partner x month
analysis_panel.py    -> panel/analysis.parquet       after the inclusion rules
eda_summary.py       -> eda/*.csv                    small views, committed, for the notebook
```

140 months, 2015-01 to 2026-08, 15.9M cells at HS8 x partner x month, 12,253 HS8 lines, 234
partners. Every month reconciles against a total row the API returns separately, and 2017 sums
to $2,340B against published imports of about $2.34 trillion.

HS10 is the pull level because tariff orders name HS8 lines and HS10 nests exactly inside HS8.
Pulling HS6 would have made every match approximate.

The raw caches are gitignored and take about an hour to rebuild. `eda/*.csv` is committed so
the notebook runs without them.

## 2. The tariff events

Two independent sources, because the first is too small on its own.

```
events/harvest_fr.py     -> events/fr_index.json      Section 232/301/IEEPA, 2,792 documents
events/build_event_table.py -> events/tariff_events.csv   134 actions
events/fix_effective_dates.py -> events/tariff_events_dates.csv

events/harvest_adcvd.py  -> events/adcvd_index.json   10,730 ITA notices, 2015-2026
events/parse_adcvd.py    -> events/adcvd_events.csv   antidumping/countervailing cases
```

The Section 232/301/IEEPA set gives 21 usable events with a median window of 23 days. The
AD/CVD set gives 1,064 preliminary determinations with a median window of 150 days, which is what
monthly data can actually resolve. The AD/CVD harvest exists because the original search used
five Section 232/301 phrases and caught these only by accident.

## 3. The coverage map

```
coverage/pull_hts99.py        -> the Chapter 99 schedule and its notes
coverage/build_coverage.py    -> which 9903 code covers what
coverage/explode_products.py  -> coverage/product_lines.csv, the actual HS8 lines
coverage_share.py             -> coverage/coverage_share.csv
```

A tariff order points at a list of HS8 subheadings, often published in a separate note. Until
those lists were read, the only option was to treat a whole chapter as tariffed. Measured in
dollars the median action covers 5.4 percent of its chapter, so that approach was labelling
mostly untreated trade as treated. This is why the first attempt at an effect found nothing.

## The analysis

```
within_product_test.py   three-bin treated vs untreated, with a placebo
event_study.py           month-by-month version, --diff for growth
adcvd_analysis.py        episode test on AD/CVD cases, always paired with a placebo
adcvd_event_study.py     month-by-month path around a preliminary determination
reversal_control.py      reversal ratio against untreated origins
counterfactual_hs8.py    reversal ratio against a fitted baseline (retired, see below)
```

Identification is within a product across origins: the control for a tariffed product from a
tariffed country is the same product from countries that were not tariffed, in the same month.
A price shock moves every origin together and cancels; a tariff moves one origin against the
rest.

**Every estimate is paired with a placebo** that shifts each event back 24 months. Three
estimators were discarded for failing it. PHASE2_RESULTS.md records those as carefully as the
ones that held, because the failures are why the survivor is believable.

## Where it stands

- The aftermath result is solid: a targeted origin loses about 27 percent against other origins
  of the same product and does not recover within eighteen months, p < 0.0001, flat pre-trend.
- The rush results are weaker, resting on 21 events, and differ by legal authority.
- `explore_data.ipynb` is the EDA, 21 cells, runs clean off `eda/*.csv`.

## Conventions

- Raw caches gitignored, rebuilt by the acquisition scripts.
- The Census API key is read from the `CK` environment variable and never written to a file.
- US spelling, no em dashes.
