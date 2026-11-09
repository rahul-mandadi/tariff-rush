# tariff-rush

**Borrowed or Real: what happens to a supplier's U.S. trade after a duty**

Rahul Reddy Mandadi, Raunaksingh Khalsa
DS 5500 Data Science Capstone, Northeastern University, Fall 2026

The write-up is [FINAL_REPORT.md](FINAL_REPORT.md) (built to `Mandadi_Khalsa_Final_Report.pdf` by
`build_final_report.py`). The decks are `slides/Mandadi_Khalsa_Presentation2_v2.pptx` and
`slides/Mandadi_Khalsa_Final_Presentation.pptx`.

## Repository map

| where | what is there |
|---|---|
| `FINAL_REPORT.md`, `HANDOFF.md` | the final write-up; how every headline number is built, with one case and one prediction traced end to end |
| repository root, `*.py` | the final pipeline, run from the root in the order under Reproducing; each script writes the CSV beside it that its numbers come from |
| repository root, `*.csv` | those results (`adcvd_stacked*`, `recovery_*`, `prediction_*`, `decision_value*`, `review_queue_*`, `sec301_*`, ...) |
| `events/` | duty notices: Federal Register harvest and parsing, ITC outcomes, the Census release calendar, the critical-circumstances side notices |
| `coverage/` | which products and countries each tariff list names (the coverage result) |
| `eda/`, `explore_data.ipynb` | category-level exploration and the small tables the notebook runs on |
| `evidence/` | public records that importers make this decision (ITC purchaser surveys, filings, trade press) |
| `slides/` | figure scripts (`fig/`), deck builders and decks |
| `tests/` | `python3 -m pytest tests -q`: timing rules, report tables against the CSVs, the November 2026 fixes |
| `archive/` | approaches tried and dropped, with why (`archive/README.md`); nothing in the final pipeline reads it |
| `docs/history/` | design notes, the phase-two results and the review log from earlier stages |
| `REPORT1.md` | Report 1 as submitted (unchanged) |

## The question

When the United States puts an antidumping or countervailing duty on one product from one country,
a sourcing team has more tariff-hit product-country relationships than it can review at once. Which
should it look at first? Is the fall in trade borrowed, coming back once the shock passes, or real,
and how early can anyone tell which? We predict the supplier country's recovery in a product, not
one supplier's failure; the output is meant to be read alongside the company's own supplier
information, and its benefit to an importer is a proposed use not yet validated with users.

## What we found

- **A tariff list names a small slice of its category.** The median list names 5.4 percent of its
  2-digit chapter's import value, so this work is done at eight digits.
- **Where an antidumping or countervailing duty becomes permanent, the targeted country loses about
  31 percent against rival suppliers of the same product** (-0.37 log points, SE 0.065, 326 cases),
  and keeps falling for the 18 months we observe. Where the trade commission finds no injury, there
  is no lasting fall. Pooled over all 381 cases: -0.19 (SE 0.11). Every estimate is checked against
  the same cases moved 24 months earlier (the fake date), a falsification check that does not rule
  out selection or other explanations; the findings are descriptive.
- **The historical benchmark, within 18 months** (380 cases): 26 percent do not fall, 17 percent
  fall and come back, 42 percent fall and stay down, and 16 percent fall, never come back and have
  no imports in months 13 to 18 (fake date: 50 / 29 / 17 / 3).
- **Forecasting, on held-out later years.** On the day the duty starts, case facts add little over
  these historical rates (a gain whose interval only just clears zero). Among products whose fall is
  already visible and that are not yet back, a model re-estimated every month from what Census has
  published ranks a product that came back above one that did not in 80 percent of pairs at month 4
  and at month 5 (gradient boosting; logistic 75 at month 4). Most of the gain over the historical
  rate comes from the latest published share alone (about 70 percent at month 4); the model stays
  slightly ahead of a latest-share model in every month from 3 to 12, though no single month clears
  a joint test. The 16,781 product-month rows come from 1,712 products in 136 investigation groups.
- **A month-4 review queue** (`review_queue.py`). Each month's falling, not-yet-back relationships
  form one queue; with an assumed capacity of 20 percent of each queue, the forecast's picks
  remained down 82 percent of the time, against 70 percent ordering by the latest share and 62
  percent in a random order (the historical rate ranks nothing); 11.5 points over the latest share,
  90 percent interval 3.9 to 15.7 over investigation groups, and similar at 10 and 30 percent.
- **Decision value under assumed costs is narrower.** Tested against every baseline at all 17
  thresholds at once, the logistic vote-time forecast beats always or never qualifying and the
  historical rates at most cost ratios from 0.45 to 0.80 of the avoidable loss; additional decision
  value over the latest-share model was not established under the simultaneous test; on day one,
  none.
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
  above normal just before the tariff came back 60 percent of the time, against about 30, as
  borrowed trade would.

All forecasts use only trade data Census had published by the decision (about five weeks after a
month ends), notices published by that date (critical-circumstances side notices included, each
once published), and comparison countries not yet named in another case.

## Reproducing

Large raw caches are not tracked (`.gitignore`); the acquisition scripts rebuild them. Run from the
repository root, in this order:

| step | scripts | what they make |
|---|---|---|
| import panel | `harvest_hs10.py`, `build_panel_hs8.py` | `panel/hs8/*.parquet`, 15.9M product x partner x month rows, 2015-01 to 2026-08 |
| duty notices | `events/harvest_adcvd.py`, `events/parse_adcvd.py`, `events/parse_margins.py` | `events/adcvd_events.csv`, products, preliminary duty rates |
| aftermath | `adcvd_stacked.py` (about 10 to 40 minutes), `adcvd_stacked_qty.py`, `analysis_panel.py`, `adcvd_analysis.py` | stacked event study, quantity check, retroactivity split |
| final outcomes | `events/itc_check.py`, `events/itc_audit.py`, `itc_compare.py` | ITC verdicts, the no-injury audit, order against no-injury |
| outcome rates | `recovery_benchmark.py --fall 0.2` (also 0.1, 0.3), `recovery_by_final_stage.py` | the four outcome shares, Kaplan-Meier recovery |
| forecasts | `events/build_release_calendar.py`, `build_decision_stacks.py`, `prediction_test.py`, `prediction_stage2.py`, `prediction_landmark.py`, `calibrated_lookup.py`, `decision_value.py`, `review_queue.py` | decision-time panels; day-one, at-the-fall, ITC-vote and monthly forecasts; the lookup; decision value; the month-4 review queue |
| Section 301 | `events/build_301_lists.py`, `sec301_benchmark.py`, `sec301_transfer_test.py` | product lists, outcomes, transfer tests |
| coverage | `coverage_share.py`, `copper_split.py` | how much of a category a list names; copper |
| outputs | `slides/fig_stacked.py`, `slides/fig_sankey.py`, `build_final_report.py`, `slides/build_deck2b.py`, `slides/build_deck_final.py` | figures, report PDF, decks |
| category level (appendix) | `eda_summary.py`, `chapter_quantity.py` (chapter tables in `eda/`, from the HS8 panel), `slides/fig_units.py`, `pharma_mix.py`, `deflation_check.py` | the dollars-against-quantity comparison; the import-price check (BLS series kept in `eda/bls_import_prices.csv`) |
| broad tariff actions (Report 1, not reported in the final) | `harvest.py`, `assemble.py` (HS2 panel), `events/harvest_fr.py`, `events/fetch_text.py`, `events/build_event_table.py`, `events/fix_effective_dates.py`, `coverage/*.py`, `build_treatment.py`, `within_product_test.py`, `event_study.py` | the tariff-action table and the rush analysis whose source documents the final audit found wrong |
| earlier decks and Report 1 | `adcvd_event_study.py`, `slides/fig_event.py`, `slides/gen_figures.py`, `slides/fig_copper_split.py`, `slides/build_deck.py`, `slides/build_deck2.py`, `build_report.py` | Presentation 1, Presentation 2 as submitted, Report 1's PDF |
| notebook and speaking notes | `build_nb.py` (writes `explore_data.ipynb`), `slides/speech.py`, `slides/write_script.py`, `slides/write_raunak.py`, `slides/dump_text.py`, `slides/render_preview.py` | the EDA notebook; the talk script; proofreading and previews |

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
  the tariff (`q3_absorbers.py`, `docs/history/PHASE2_RESULTS.md`).
- The importer use case rests on public records (commission purchaser surveys, company filings, trade
  press; see `evidence/USE_EVIDENCE.md`), not on interviews, and the forecasts are for a supplier
  country, not one importer's own supplier.

An earlier version of this work named port and terminal operators as the user; that was tested and
dropped, because displaced volume arrives through substantially the same U.S. customs districts.
`docs/history/PHASE2_RESULTS.md` records what failed as well as what held, and `archive/README.md`
lists the scripts of the dropped approaches.

## Data sources

Census international trade API, Federal Register API, USITC Harmonized Tariff Schedule (Chapter 99
notes), U.S. International Trade Commission determination notices. All public and free for research
use.
