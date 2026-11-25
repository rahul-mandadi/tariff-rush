# Handoff: how the final results are built, and how to trace one case

Rewritten 2026-11-06 for the final report (`FINAL_REPORT.md`) and decks. Every number below is
read from the CSV named beside it.

## The results

| claim | number | source |
|---|---|---|
| a tariff list names a small slice of its chapter | median 5.4 percent of import value | `coverage/coverage_share.csv` |
| targeted country against rivals, cases that became orders | -0.37 log points (SE 0.065), 326 cases, 125 groups | `results/itc_compare.csv` |
| same, pooled over 381 cases | -0.19 (SE 0.11); fake date +0.06 | `results/adcvd_stacked.csv` |
| outcomes within 18 months, 380 cases (the historical benchmark) | 26 / 17 / 42 / 16 percent: did not fall / fell, came back / fell, still down / fell, never came back and no imports in months 13 to 18 (fake date 50 / 29 / 17 / 3) | `results/recovery_benchmark_fall20.csv` |
| day-one forecast | Brier 0.242 vs 0.248 for the historical rate, gain 0.007 [-0.001, 0.013] (interval includes zero; it cleared zero only just before the November 2026 critical-circumstances fix), AUC 0.633; 381 eligible cases, 241 scored | `results/prediction_test.csv` |
| monthly forecast, month 4 | boosting AUC 0.795 (logistic 0.753), gain over that month's historical rate 0.039 [0.026, 0.052]; the latest-share model alone gets about 70 percent of that gain (Brier 0.165 vs 0.192, boosting 0.154); 315 eligible cases, 198 scored | `results/prediction_landmark.csv`, `results/prediction_landmark_counts.csv` |
| monthly forecast against the latest-share model | boosting ahead by 0.003 to 0.013 in every month 3 to 12 (pointwise intervals above zero in months 4 to 6 and 11); no month clears a joint test over all months (`simlo_os_boosting`) | `results/prediction_landmark.csv` |
| ITC-vote forecast | logistic AUC 0.796, Brier 0.134 vs 0.174, 0.012 [0.003, 0.021] beyond the latest-share model (Brier 0.146); 329 eligible cases, 207 scored | `results/prediction_stage2.csv` |
| month-4 review queue, 20 percent of each month's queue (assumed) | reviewed relationships that remained down: forecast 82 percent, latest share 70, random order (historical rate) 62; forecast minus latest share +12.0 points [3.9, 15.7]; 10 and 30 percent, case weights and leaving out the largest group agree; 936 relationships, 198 cases, 66 groups, 44 decision months | `results/review_queue_eval.csv`, `results/review_queue_watchlist.csv` |
| decision value, simultaneous over 17 thresholds and all baselines | ITC vote: ahead of always/never qualifying and both historical rates at 0.45, 0.50 and 0.60 to 0.80, additional decision value over the latest-share model not established under the simultaneous test; at the fall and on day one none | `results/decision_value_joint.csv`, `results/decision_value.csv` |
| Section 301 Lists 1 to 3 | 35 / 24 / 36 / 6 percent (16 months; fake date 42 / 31 / 24 / 3); antidumping-trained logistic AUC 0.67 on Section 301 (Section 301's own model 0.73), +0.017 [0.011, 0.023] over Section 301's own rate | `results/s301_benchmark.csv`, `results/sec301_transfer_test.csv` |
| pooling Section 301 into training for later antidumping cases | logistic +0.005 [0.001, 0.010] | `results/sec301_pooling_gain.csv` |
| outside check, 2020 mattresses | panel matches published figures within 3 million dollars; Vietnam, Thailand, Cambodia stayed down or stopped, Indonesia did not | `results/recovery_pairs_real_fall20.csv`, `evidence/USE_EVIDENCE.md` |

Sample sizes to quote with any forecast: the monthly model has 16,781 product-month rows, but they
come from 1,712 products in 349 cases and 136 investigation groups, and the groups are the
effective sample. Held out: 1,157 products, 219 cases.

## Reproduction order

From the repository root. Raw caches are git-ignored and rebuilt by the first steps.

1. `data/harvest_hs10.py`, `data/build_panel_hs8.py`: the import panel (`panel/hs8/`).
2. `events/harvest_adcvd.py`, `events/parse_adcvd.py`, `events/parse_margins.py`: duty notices, products, rates.
3. `measure/adcvd_stacked.py` (about 40 minutes): measurement panels with hindsight comparison groups and the stacked estimates; `measure/adcvd_stacked_qty.py`, `data/analysis_panel.py` (writes `panel/analysis.parquet`), `report1/adcvd_analysis.py`.
4. `events/itc_check.py`, `events/itc_audit.py`, `measure/itc_compare.py`: final ITC outcomes and the order against no-injury split.
5. `measure/recovery_benchmark.py --fall 0.2` (also 0.1, 0.3), `measure/recovery_by_final_stage.py`: the four outcomes.
6. `events/build_release_calendar.py` (Census release date of each data month, from ALFRED), `measure/build_decision_stacks.py`: decision-time panels (only rivals and products known by the first preliminary, exact dates).
7. `forecast/prediction_test.py`, `forecast/prediction_stage2.py`, `forecast/prediction_landmark.py`, `forecast/calibrated_lookup.py`, `forecast/decision_value.py`, `forecast/review_queue.py`: the forecasts, their evaluation and the month-4 review queue; then the methodology study: `forecast/feature_ladder.py`, `forecast/review_queue_curves.py`, `forecast/model_explain.py`, `forecast/model_calibration.py`, `forecast/model_recalibration.py`. `frozen_forecast.py` made the frozen forecast on 2026-11-15 and must not be rerun over it; `frozen_forecast_check.py` scores it as outcomes arrive.
8. `events/build_301_lists.py`, `section301/sec301_benchmark.py`, `section301/sec301_transfer_test.py`: Section 301.
9. `measure/coverage_share.py`, `data/copper_split.py`: coverage and copper.
10. `slides/fig_stacked.py`, `slides/fig_sankey.py`, `build_final_report.py`, `slides/build_deck2b.py`, `slides/build_deck_final.py`: figures, report PDF, decks.

Checks: `python3 -m pytest tests -q` (74 tests: timing rules, headline and table numbers, the November 2026 fixes, critical-circumstances side notices and findings, the review queue, the methodology study, the report's Appendix K; the panel-based ones skip if the
ignored parquet files are absent). One of them was confirmed to fail on the hindsight panels, so it
does detect the leak it guards against.

## Walkthrough A: one historical case

Mattresses from Vietnam, the 2020 antidumping case (episode 258 in `results/adcvd_episodes_collapsed.csv`).

1. **Source notice.** Commerce's preliminary determination, Federal Register document 2020-24300,
   published November 3, 2020 (case A-552-827), preliminary rate 989.9 percent
   (`events/adcvd_events.csv`, `events/adcvd_margins.csv`). That month is k = 0.
2. **Products.** The notice names five eight-digit products: 9401.40.00, 9401.90.50, 9404.21.00,
   9404.29.10, 9404.29.90 (`events/adcvd_products.csv`).
3. **Comparison countries.** For each product, every other country that sold it to the U.S. in
   k -18 to -7 and before the case began: 36, 74, 44, 37 and 38 rivals. None had to be left out for
   being named in another case, so the measurement and decision-time panels agree here.
4. **Position and outcome label.** Vietnam's share of each product's imports among those
   countries, 3-month average, against its k -18 to -13 level. The three mattress lines fell below
   four-fifths of that level by month 1 (9404.21.00) or month 0 (9404.29.10, 9404.29.90) and never
   returned to it by month 18, while still trading: "fell, still down". The two seating lines never
   fell (`results/recovery_pairs_real_fall20.csv`).
5. **Final stage.** The ITC confirmed injury and the order was published May 14, 2021, month 6
   (`recovery_lib.final_stage`).

## Walkthrough B: one held-out prediction

The same case, product 9404.29.10 (mattresses, other), at the ITC vote (`forecast/prediction_stage2.py`).

1. **Decision date.** The order notice, May 14, 2021, k = 6. Census data through k = 4 (March
   2021) are published by then (`census_release_calendar.csv`); nothing later is used.
2. **Training data.** Only cases whose month-18 data were published before January 2020 (the test
   year is 2020, by the year of k = 0): 67 cases.
3. **Information at the decision** (`results/prediction_stage2_features.csv`): fall visible from month 0;
   latest smoothed share 0.000 of the pre-case level; duty confirmed (not lifted); preliminary rate
   989.9 percent; Vietnam's pre-case share 0.456.
4. **Prediction** (`results/prediction_stage2_heldout.csv`): logistic model P(back by month 18) = 0.015, so
   P(not back) = 0.985. Baselines: historical rate 0.210 back, rate for confirmed duties 0.172 back
   (P(not back) 0.828), latest-share model 0.094 back.
5. **Assumed action threshold.** At t = 0.75 (qualifying assumed to cost three-quarters of the
   avoidable loss), act if P(not back) >= 0.75: the model says qualify an alternative supplier, and
   so do the vote-split rate and the latest-share model. At t = 0.85 the vote-split rate (0.828)
   says wait while the model still says qualify. Across all held-out cases the model's lead over the
   latest-share model is not established at any threshold.
6. **Observed outcome.** The product did not come back by month 18 (y = 0), so acting was the
   right call at both thresholds. The monthly model scored the same product at month 4 at
   P(back) 0.048 (boosting) against 0.211 for that month's historical rate
   (`results/prediction_landmark_heldout.csv`).

## Limitations

- Data visibility follows Census's actual release dates (`census_release_calendar.csv`). At the vote
  the cutoff is the vote notice's own date. At the fall and the monthly points, notices are cut at
  the end of the month before, while a trade month counts if it was released by the end of the
  decision month (usually around day 5): a convention, not an exact date.
- Trade values are today's revised Census data, not the first-published figures.
- Critical-circumstances-only notices (30, `CC_ONLY` in `measure/adcvd_stacked.py`; fixed 2026-11-09) never
  define an episode or its k = 0. They are kept as dated information in `events/cc_side_notices.csv`
  (one row per notice and country, affirmative or not, read from each summary), attached to the
  same country's episode for the same product, and a forecast reads one only once it is published.
  Before the fix, seven of them sat among episode documents: two censored duplicate episodes
  (torsion springs, China and India 2025) and one episode dated a month early (polyester textured
  yarn, China 2019); the nine already excluded had dropped their findings from the forecasts. Two
  side notices have no episode to attach to (Taiwan corrosion-resistant steel 2015 and Japan
  hot-rolled steel 2015, whose own preliminaries were not kept). Two amendments that withdraw an
  earlier finding in part (2020-22179, 2024-05937) add no affirmative finding but do not remove the
  earlier one.
- One initiation date is corrected by hand (`INI_FIX`): 2025-16653 states "April 23, 2024" where its
  own footnote cites the initiation at 90 FR 17032 (April 23, 2025); the wrong year had merged
  Taiwan's monomers and oligomers case into its 2024 epoxy resins case.
- At the vote, a release on the vote notice's own date counts as available (Census releases at 8:30 a.m.,
  the Federal Register publishes at about 8:45); 35 rows in 12 episodes.
- Forecasts are for a supplier country's position in a product, not for one importer's supplier.
- Decision value is potential benefit under assumed costs; it treats the country-level outcome as
  the importer's loss and assumes qualifying at the decision date can still avoid it. Nothing here
  measures a saving.
- The public evidence (`evidence/USE_EVIDENCE.md`) shows supplier switching and its timing exist;
  most purchaser switching in the ITC reports had other causes, and it does not validate these
  forecasts.
- Monthly forecasts concern products already falling and not yet back; that set changes by month,
  so the curve is not the same products over time.
- Intervals hold fitted models fixed and resample investigation groups; the effective sample is
  about 150 groups (antidumping) and three list dates (Section 301).
- Model choices: logistic regression is the common model for decision value and the Section 301
  transfer as a consistency choice; it was not preregistered. Table 3 shows the best of the
  pre-specified models; all models are in the CSVs.
- The Section 301 product lists come from the 2026 tariff schedule; product exclusions are not
  removed.

## What still needs you

- **Deck PDFs**: PowerPoint's and Keynote's scripted exports both stall on a dialog. Open
  `slides/Mandadi_Khalsa_Presentation2_v2.pptx` (14 slides) and
  `slides/Mandadi_Khalsa_Final_Presentation.pptx` (18 slides) and use File > Export > PDF.
- **Length limits**: the only written limit found locally is Report 1's (five pages excluding
  references and appendix, recorded in `docs/history/REPORT_STATUS.md`). The final report follows it; check the
  final's own instructions, and the presentation time limit, against Kylie's announcement.
- **Merge** `feature/event-table` into `main` when the above is done (fast-forward).
