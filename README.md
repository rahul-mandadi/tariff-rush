# tariff-rush

**Borrowed or Real: what happens to a supplier's U.S. trade after a duty**

Rahul Reddy Mandadi, Raunaksingh Khalsa
DS 5500 Data Science Capstone, Northeastern University, Fall 2026

The write-up is [FINAL_REPORT.md](FINAL_REPORT.md) (built to `Mandadi_Khalsa_Final_Report.pdf` by
`build_final_report.py`). The decks are `slides/Mandadi_Khalsa_Presentation2_v2.pptx` and
`slides/Mandadi_Khalsa_Final_Presentation.pptx`.

## The question

When the United States puts a duty on one product from one country, an importer buying that
product has to decide whether to start qualifying another supplier or wait for the business to come
back. Is the fall in trade borrowed, coming back once the shock passes, or real? And how early can
anyone tell?

## What we found

- **A tariff list names a small slice of its category.** The median list names 5.4 percent of its
  2-digit chapter's import value, so this work is done at eight digits.
- **Where an antidumping or countervailing duty becomes permanent, the targeted country loses about
  31 percent against rival suppliers of the same product** (-0.37 log points, SE 0.065, 329 cases),
  and keeps falling for the 18 months we observe. Where the trade commission finds no injury, there
  is no lasting fall. Pooled over all 384 cases: -0.19 (SE 0.11). Every estimate is checked against
  the same cases moved 24 months earlier (the fake date).
- **What usually happens to a targeted product within 18 months** (384 cases): 25 percent do not
  fall, 17 percent fall and come back, 42 percent fall and stay down, and 16 percent fall, never
  come back and have no imports in months 13 to 18 (fake date: 49 / 30 / 18 / 3).
- **Forecasting, on held-out later years.** On the day the duty starts, case facts add no reliable
  gain over these historical rates. By the trade commission's final vote, a logistic model ranks a
  product that will come back above one that will not 81 percent of the time and cuts the Brier
  score by a quarter (0.134 against 0.179); the latest published share alone gives part of that, and
  the other facts add 0.018 (0.009 to 0.029).
- **The model carries over to China's 2018 Section 301 tariffs** (6,844 listed products): trained on
  antidumping cases, it ranks Section 301 products correctly 69 percent of the time, against 76 for a
  model trained on Section 301 itself. There, products whose China share ran more than a quarter
  above normal just before the tariff came back 60 percent of the time, against about 30: that part
  of the fall was borrowed.

All forecasts use only trade data Census had published by the decision (about five weeks after a
month ends), notices published by that date, and comparison countries not yet named in another case.

## Reproducing

Large raw caches are not tracked (`.gitignore`); the acquisition scripts rebuild them. Run from the
repository root, in this order:

| step | scripts | what they make |
|---|---|---|
| import panel | `harvest_hs10.py`, `build_panel_hs8.py` | `panel/hs8/*.parquet`, 15.9M product x partner x month rows, 2015-01 to 2026-08 |
| duty notices | `events/harvest_adcvd.py`, `events/parse_adcvd.py`, `events/parse_margins.py` | `events/adcvd_events.csv`, products, preliminary duty rates |
| aftermath | `adcvd_stacked.py` (about 40 minutes), `adcvd_stacked_qty.py`, `adcvd_analysis.py` | stacked event study, quantity check, retroactivity split |
| final outcomes | `events/itc_check.py`, `events/itc_audit.py`, `itc_compare.py` | ITC verdicts, the no-injury audit, order against no-injury |
| outcome rates | `recovery_benchmark.py --fall 0.2` (also 0.1, 0.3), `recovery_by_final_stage.py` | the four outcome shares, Kaplan-Meier recovery |
| forecasts | `build_decision_stacks.py`, `prediction_test.py`, `prediction_stage2.py`, `calibrated_lookup.py` | decision-time panels, day-one, at-the-fall and ITC-vote tests, the lookup |
| Section 301 | `events/build_301_lists.py`, `sec301_benchmark.py`, `sec301_transfer_test.py` | product lists, outcomes, transfer tests |
| coverage | `coverage_share.py`, `copper_split.py` | how much of a category a list names; copper |
| outputs | `slides/fig_stacked.py`, `slides/fig_sankey.py`, `build_final_report.py`, `slides/build_deck2b.py`, `slides/build_deck_final.py` | figures, report PDF, decks |

Each script writes the CSV its numbers come from. `recovery_lib.py` holds the outcome rules shared
by the Section 301 and forecasting scripts; `sec301_benchmark.py` checks that it reproduces
`recovery_benchmark.py` exactly.

## Open, as stated in the report

- The rush before broad tariff actions (Section 232, 301, IEEPA): 13 of the 19 documents behind the
  earlier analysis need correcting, and actions that hit nearly every country leave no untaxed
  comparison.
- Where the lost trade goes: gains spread across many rival countries and are not predictable from
  the tariff (`q3_absorbers.py`, `PHASE2_RESULTS.md`).
- The importer use case is grounded in the duty timeline but not validated with importers.

An earlier version of this work named port and terminal operators as the user; that was tested and
dropped, because displaced volume arrives through substantially the same U.S. customs districts.
`PHASE2_RESULTS.md` records what failed as well as what held.

## Data sources

Census international trade API, Federal Register API, USITC Harmonized Tariff Schedule (Chapter 99
notes), U.S. International Trade Commission determination notices. All public and free for research
use.
