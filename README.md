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
  gain over these historical rates. Among products whose fall is already visible and that are not
  yet back, a model re-estimated every month from what Census has published ranks a product that
  came back above one that did not in 78 percent of pairs at month 4 and 81 percent at month 5
  (gradient boosting; logistic 75 at month 4), and in months 4 to 6 boosting outperformed a model
  of the latest published share. The eligible products change by month, and the 16,969
  product-month rows come from 1,735 products in 139 investigation groups.
- **Decision value is narrower.** As potential benefit under assumed costs, tested against every
  baseline (always or never qualify, the historical rate, the rate by vote, the latest-share model)
  at all 17 thresholds at once, the logistic vote-time forecast is supported only at cost ratios of
  0.75 and 0.85 of the avoidable loss; on day one, at none.
- **Supplier switching around these cases is common and slow.** In the commission's final staff
  reports, about half of responding purchasers changed suppliers during the investigations (27 of 54
  for aluminum extrusions, 23 of 45 for steel nails), mostly for reasons other than the duty, and
  qualifying a new supplier took from days to 18 months. Floor & Decor's 2020 annual report
  describes moving its Chinese tile sourcing after the 2019 preliminary duties. This shows the
  decision exists; it does not validate the forecasts. For the 2020 mattress cases our panel
  matches published import figures within 3 million dollars.
- **The model carries over to China's 2018 Section 301 tariffs** (6,844 listed products): trained on
  antidumping cases, it ranks Section 301 products correctly 67 percent of the time, against 73 for a
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
| forecasts | `build_decision_stacks.py`, `prediction_test.py`, `prediction_stage2.py`, `prediction_landmark.py`, `calibrated_lookup.py`, `decision_value.py` | decision-time panels; day-one, at-the-fall, ITC-vote and monthly forecasts; the lookup; decision value |
| Section 301 | `events/build_301_lists.py`, `sec301_benchmark.py`, `sec301_transfer_test.py` | product lists, outcomes, transfer tests |
| coverage | `coverage_share.py`, `copper_split.py` | how much of a category a list names; copper |
| outputs | `slides/fig_stacked.py`, `slides/fig_sankey.py`, `build_final_report.py`, `slides/build_deck2b.py`, `slides/build_deck_final.py` | figures, report PDF, decks |

Each script writes the CSV its numbers come from. `python3 -m pytest tests -q` checks the timing
rules (exact-date rival exclusions, day-one product lists, monthly eligibility, training cutoffs,
the net-benefit formula). `HANDOFF.md` traces one case and one held-out prediction end to end. `recovery_lib.py` holds the outcome rules shared
by the Section 301 and forecasting scripts; `sec301_benchmark.py` checks that it reproduces
`recovery_benchmark.py` exactly.

## Open, as stated in the report

- The rush before broad tariff actions (Section 232, 301, IEEPA): 13 of the 19 documents behind the
  earlier analysis need correcting, and actions that hit nearly every country leave no untaxed
  comparison.
- Where the lost trade goes: gains spread across many rival countries and are not predictable from
  the tariff (`q3_absorbers.py`, `PHASE2_RESULTS.md`).
- The importer use case rests on public records (commission purchaser surveys, company filings, trade
  press; see `evidence/USE_EVIDENCE.md`), not on interviews, and the forecasts are for a supplier
  country, not one importer's own supplier.

An earlier version of this work named port and terminal operators as the user; that was tested and
dropped, because displaced volume arrives through substantially the same U.S. customs districts.
`PHASE2_RESULTS.md` records what failed as well as what held.

## Data sources

Census international trade API, Federal Register API, USITC Harmonized Tariff Schedule (Chapter 99
notes), U.S. International Trade Commission determination notices. All public and free for research
use.
