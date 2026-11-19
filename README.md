# tariff-rush

**Borrowed or Real: what happens to a supplier's U.S. trade after a duty**

Rahul Reddy Mandadi, Raunaksingh Khalsa
DS 5500 Data Science Capstone, Northeastern University, Fall 2026

The write-up is [FINAL_REPORT.md](FINAL_REPORT.md) (built to `Mandadi_Khalsa_Final_Report.pdf` by
`build_final_report.py`). The decks are `slides/Mandadi_Khalsa_Presentation2_v3.pptx` (Presentation 2, with its spoken
script in `slides/P2_SCRIPT.md`) and `slides/Mandadi_Khalsa_Final_Presentation.pptx`.

## Repository map

| where | what is there |
|---|---|
| `FINAL_REPORT.md`, `HANDOFF.md` | the final write-up; how every headline number is built, with one case and one prediction traced end to end |
| `run_all.py` | reruns the analysis in order, from the stacked panels to the figures (see Reproducing) |
| `data/` | fetching the Census trade data, building the product-level panel, and the category-level checks |
| `measure/` | the main measurement: the comparison against rival countries, the four outcomes, the panels the forecasts use |
| `forecast/` | the forecasts, the month-4 review queue and the methodology study |
| `section301/` | the same outcome rules and forecast applied to China's 2018 Section 301 tariffs |
| `report1/` | Report 1 as submitted (`report1/REPORT1.md`, unchanged), its EDA notebook (`report1/explore_data.ipynb`) and the scripts from that stage, kept because Report 1 and the early decks cite them |
| repository root | `modeling.py` and `recovery_lib.py` (code the scripts share), `build_final_report.py`, and the frozen forecast: `frozen_forecast.py`, its check, `frozen_forecast.csv`, its fingerprint and the check's result, plus the two inputs the check reads (`census_release_calendar.csv`, `recovery_pairs_decision_fall20.csv`), which stay at the root until the forecast is scored |
| `results/` | the result CSVs; every script runs from the repository root and writes its CSVs here (`adcvd_stacked*`, `recovery_*`, `prediction_*`, `decision_value*`, `review_queue_*`, `sec301_*`, ...) |
| `events/` | duty notices: Federal Register harvest and parsing, ITC outcomes, the Census release calendar, the critical-circumstances side notices |
| `coverage/` | which products and countries each tariff list names (the coverage result) |
| `eda/` | category-level exploration: the small tables the Report 1 notebook runs on |
| `evidence/` | public records that importers make this decision (ITC purchaser surveys, filings, trade press) |
| `slides/` | figure scripts (`fig/`), deck builders and decks |
| `tests/` | `python3 -m pytest tests -q`: timing rules, report tables against the CSVs, the November 2026 fixes |
| `archive/` | approaches tried and dropped, with why (`archive/README.md`); nothing in the final pipeline reads it |
| `docs/SCOPE.md`, `docs/METHODS.md` | the agreed scope; the design notes behind each script, moved out of the script headers |
| `docs/history/` | design notes, the phase-two results and the review log from earlier stages |

## The question

When the United States puts an antidumping or countervailing duty on one product from one country,
an analyst at a U.S. importer who monitors several product markets has more declines than they can
investigate at once. Which should they look at first? Is the fall in trade borrowed, coming back once the shock passes, or real,
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
  these historical rates (a gain whose interval includes zero). Among products whose fall is
  already visible and that are not yet back, a model re-estimated every month from what Census has
  published ranks a product that came back above one that did not in 79.5 percent of pairs at month 4
  (AUC 0.795) and 79.7 at month 5 (gradient boosting; logistic 0.753 at month 4). Most of the gain over the historical
  rate comes from the latest published share alone (about 70 percent at month 4); the model stays
  slightly ahead of a latest-share model in every month from 3 to 12, though no single month clears
  a joint test. The 16,781 product-month rows come from 1,712 products in 136 investigation groups.
- **A month-4 review queue** (`forecast/review_queue.py`). Each month's falling, not-yet-back relationships
  form one queue; with an assumed capacity of 20 percent of each queue, the forecast's picks
  remained down 82 percent of the time, against 70 percent ordering by the latest share and 62
  percent in a random order (the historical rate ranks nothing); 12.0 points over the latest share,
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
  above normal just before the tariff came back 60 percent of the time, against about 30. That is
  an observed association: a temporary spike can reverse on its own, and the split has no fake-date
  check.

All forecasts use only trade data Census had published by the decision (about five weeks after a
month ends), notices published by that date (critical-circumstances side notices included, each
once published), and comparison countries not yet named in another case.

## Reproducing

Large raw caches are not tracked (`.gitignore`); the acquisition scripts rebuild them. Fetching needs a
free Census API key in the `CK` environment variable, for example `CK=<key> python3 data/harvest_hs10.py`.
Every script runs from the repository root, for example `python3 forecast/prediction_landmark.py`,
and writes its result CSVs to `results/`.

`python3 run_all.py` reruns the analysis from `measure/adcvd_stacked.py` to the figures, in order,
and stops at the first failure (about an hour; `--list` shows the steps, `--from <step>` resumes).
It does not fetch data and does not touch the frozen forecast. The full order, fetching included:

| step | scripts | what they make |
|---|---|---|
| import panel | `data/harvest_hs10.py`, `data/build_panel_hs8.py` | `panel/hs8/*.parquet`, 15.9M product x partner x month rows, 2015-01 to 2026-08 |
| duty notices | `events/harvest_adcvd.py`, `events/parse_adcvd.py`, `events/parse_margins.py` | `events/adcvd_events.csv`, products, preliminary duty rates |
| aftermath | `measure/adcvd_stacked.py` (about 10 to 40 minutes), `measure/adcvd_stacked_qty.py`, `data/analysis_panel.py`, `report1/adcvd_analysis.py` | stacked event study, quantity check, retroactivity split |
| final outcomes | `events/itc_check.py`, `events/itc_audit.py`, `measure/itc_compare.py` | ITC verdicts, the no-injury audit, order against no-injury |
| outcome rates | `measure/recovery_benchmark.py --fall 0.2` (also 0.1, 0.3), `measure/recovery_by_final_stage.py` | the four outcome shares, Kaplan-Meier recovery |
| forecasts | `events/build_release_calendar.py`, `measure/build_decision_stacks.py`, `forecast/prediction_test.py`, `forecast/prediction_stage2.py`, `forecast/prediction_landmark.py`, `forecast/calibrated_lookup.py`, `forecast/decision_value.py`, `forecast/review_queue.py` | decision-time panels; day-one, at-the-fall, ITC-vote and monthly forecasts; the lookup; decision value; the month-4 review queue |
| methodology study (`docs/SCOPE.md` section 5) | `forecast/feature_ladder.py`, `forecast/review_queue_curves.py`, `forecast/model_explain.py`, `forecast/model_calibration.py`, `forecast/model_recalibration.py`, `forecast/model_family_check.py` | where the forecast's information comes from; the capacity curve and months 6 and 8; what drives it; calibration and errors; recalibration on earlier years (exploratory); elastic net and random forest as a check |
| frozen forecast | `frozen_forecast.py` (made 2026-11-15, do not rerun), `frozen_forecast_check.py` (run as outcomes arrive) | a ranking of 197 relationships in 12 monthly lists whose outcomes were unknown when committed; the 184 in the 11 lists whose outcome months were still unpublished are scored: the one test not run on years already looked at |
| Section 301 | `events/build_301_lists.py`, `section301/sec301_benchmark.py`, `section301/sec301_transfer_test.py` | product lists, outcomes, transfer tests |
| coverage | `measure/coverage_share.py`, `data/copper_split.py` | how much of a category a list names; copper |
| outputs | `slides/fig_stacked.py`, `slides/fig_sankey.py`, `slides/fig_funnel.py` (notices to cases), `slides/fig_taiwan_example.py` (the report's opening example), `slides/fig_talk.py` (Presentation 2 v3 figures), `build_final_report.py`, `slides/build_deck2c.py` with `slides/write_script2.py` (Presentation 2 v3 and its spoken script), `slides/build_deck_final.py` | figures, report PDF, decks |
| category level (appendix) | `data/eda_summary.py`, `data/chapter_quantity.py` (chapter tables in `eda/`, from the HS8 panel), `slides/fig_units.py`, `data/pharma_mix.py`, `data/deflation_check.py` | the dollars-against-quantity comparison; the import-price check (BLS series kept in `eda/bls_import_prices.csv`) |
| broad tariff actions (Report 1, not reported in the final) | `data/harvest.py`, `data/assemble.py` (HS2 panel), `events/harvest_fr.py`, `events/fetch_text.py`, `events/build_event_table.py`, `events/fix_effective_dates.py`, `coverage/*.py`, `report1/build_treatment.py`, `report1/within_product_test.py`, `report1/event_study.py` | the tariff-action table and the rush analysis whose source documents the final audit found wrong |
| earlier decks and Report 1 | `report1/adcvd_event_study.py`, `slides/fig_event.py`, `slides/gen_figures.py`, `slides/fig_copper_split.py`, `slides/build_deck.py`, `slides/build_deck2.py`, `slides/build_deck2b.py`, `report1/build_report.py` | Presentation 1, Presentation 2 as first submitted and its v2 resubmission, Report 1's PDF |
| notebook and speaking notes | `report1/build_nb.py` (writes `report1/explore_data.ipynb`), `slides/speech.py`, `slides/write_script.py`, `slides/write_raunak.py`, `slides/dump_text.py`, `slides/render_preview.py` | the EDA notebook; the talk script; proofreading and previews |

Each script writes the CSV its numbers come from, in `results/`. `python3 -m pytest tests -q` checks the timing
rules (exact-date rival exclusions, day-one product lists, monthly eligibility, training cutoffs,
the net-benefit formula). `HANDOFF.md` traces one case and one held-out prediction end to end. `modeling.py` holds what the forecasting scripts share (the two models and their settings, tuning, the review rule, recalibration). `recovery_lib.py` holds the outcome rules shared
by the Section 301 and forecasting scripts; `section301/sec301_benchmark.py` checks that it reproduces
`measure/recovery_benchmark.py` exactly.

## Open, as stated in the report

- The rush before broad tariff actions (Section 232, 301, IEEPA): 13 of the 19 documents behind the
  earlier analysis need correcting, and actions that hit nearly every country leave no untaxed
  comparison.
- Where the lost trade goes: gains spread across many rival countries and are not predictable from
  the tariff (`report1/q3_absorbers.py`, `docs/history/PHASE2_RESULTS.md`).
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
