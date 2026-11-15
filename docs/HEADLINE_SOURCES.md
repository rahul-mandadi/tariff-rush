# Where each headline number comes from

For writing the final report. Each row gives the result file and the CSV line (line 1 is the header,
so line 2 is the first data row), the columns that identify the row, and the values. Generated from
the result files on 2026-11-15, after the critical-circumstances fix (see below).

Two counts are printed by the scripts but not saved in a CSV: the 381 cases with all 18 months
(`measure/adcvd_stacked.py` output: "episodes with complete 18-month follow-up: 381") and the 326
permanent-duty cases in 125 groups (`measure/itc_compare.py` output: "stacks 326 ... clusters 125").
`python3 run_all.py` keeps that output in `logs/run_all/`. Percent changes from log points:
1 - exp(-0.373) = 0.31.

## Numbers the critical-circumstances fix changed

The "retroactive duties found" input was wrong for all countries in 109 preliminary notices and for
some countries in 10 more that cover several countries (see
`docs/FROZEN_FORECAST_NOTE.md` and `tests/test_critical_findings.py`). Only the forecasts and the
Report 1 retroactivity split use it; the measurement results (sections on the loss, the outcomes and
Section 301) are unchanged.

| claim | before | after |
|---|---|---|
| day-one forecast against the historical rate | gain 0.010, 90% interval 0.0005 to 0.018 | gain 0.006, interval -0.001 to 0.014: includes zero |
| month-4 boosting AUC | 0.7952 (80%) | 0.7950 (79%) |
| month-4 logistic AUC | 0.750 | 0.753 |
| review queue at 20%, forecast still down | 81.8% | 82.3% |
| latest share at 20% (Census share only) | 70.3% | 70.3%, unchanged |
| forecast minus latest share | +11.5 points [3.9, 15.7] | +12.0 points [3.9, 15.7] |
| review queue at 10% (forecast; difference) | 84.8%; +15.6 [7.7, 20.3] | 85.1%; +16.0 [7.6, 20.4] |
| relationships entering / leaving the top 20% over 44 months | | 3 / 3, in 3 months (2.4 of 187.2 review places) |
| decision value at the ITC vote, ahead of always, never and both historical rates | 0.45 and 0.55 to 0.80 | 0.45, 0.50 and 0.60 to 0.80 |
| decision value at the fall, simultaneous test | 0.70 | none |
| Taiwan epoxy resins, January 2025 list | 2nd of 36, 8.6% chance back, reviewed | 2nd of 36, 8.5%, reviewed |

## All headline numbers

| claim | file and row (line 1 is the header) | values |
|---|---|---|
| a list names a small slice of its chapter: median 5.4% | `coverage/coverage_share.csv`, all 1,350 rows (one per Chapter 99 heading) | median of share 0.0535 |
| permanent duty: -0.37 log points (about 31%), SE 0.065 | `itc_compare.csv` line 2 (sample = final stage: order; outcome = PPML value, zeros in; contrast = after (0..18) vs reference (-18..-13)) | est -0.373, se 0.065 |
| ITC finds no injury: no lasting fall | `itc_compare.csv` line 23 (sample = final stage: negative; outcome = PPML value, zeros in; contrast = after (0..18) vs reference (-18..-13)) | est 0.057, se 0.027 |
| all cases pooled: -0.19, SE 0.11 | `adcvd_stacked.csv` line 2 (sample = real, complete follow-up; outcome = PPML value, zeros in; contrast = after (0..18) vs reference (-18..-13)) | est -0.187, se 0.108 |
| fake date, pooled: +0.06 | `adcvd_stacked.csv` line 44 (sample = placebo, 24 months earlier; outcome = PPML value, zeros in; contrast = after (0..18) vs reference (-18..-13)) | est 0.055, se 0.032 |
| no surge before the duty, all cases: +0.02 | `adcvd_stacked.csv` line 4 (sample = real, complete follow-up; outcome = PPML value, zeros in; contrast = pre-case (-12..-7) vs reference (-18..-13)) | est 0.022, se 0.042 |
| no surge before the duty, permanent duties: +0.07 | `itc_compare.csv` line 4 (sample = final stage: order; outcome = PPML value, zeros in; contrast = pre-case (-12..-7) vs reference (-18..-13)) | est 0.075, se 0.057 |
| outcomes, real: 26% no fall | `recovery_benchmark_fall20.csv` line 2 (sample = real; measure = no fall) | value 0.256, lo 0.219, hi 0.297 |
| outcomes, real: 17% fell and came back | `recovery_benchmark_fall20.csv` line 3 (sample = real; measure = recovered) | value 0.171, lo 0.147, hi 0.193 |
| outcomes, real: 42% fell and stayed down | `recovery_benchmark_fall20.csv` line 4 (sample = real; measure = not recovered) | value 0.415, lo 0.376, hi 0.455 |
| outcomes, real: 16% fell, no imports in months 13-18 | `recovery_benchmark_fall20.csv` line 5 (sample = real; measure = exited) | value 0.158, lo 0.113, hi 0.204 |
| outcomes, fake date: 50% | `recovery_benchmark_fall20.csv` line 10 (sample = placebo; measure = no fall) | value 0.499 |
| outcomes, fake date: 29% | `recovery_benchmark_fall20.csv` line 11 (sample = placebo; measure = recovered) | value 0.293 |
| outcomes, fake date: 17% | `recovery_benchmark_fall20.csv` line 12 (sample = placebo; measure = not recovered) | value 0.174 |
| outcomes, fake date: 3% | `recovery_benchmark_fall20.csv` line 13 (sample = placebo; measure = exited) | value 0.033 |
| outcomes cover 380 cases | `recovery_pairs_real_fall20.csv`, cases with a category other than censored | 380 cases |
| day one: Brier 0.242 against 0.248, AUC 0.63 | `prediction_test.csv` line 8 (year = pooled) | brier_model 0.242, brier_benchmark 0.248, auc_model 0.633, test_episodes 241.000 |
| day one: gain 0.006, 90% interval -0.001 to 0.014 (includes zero) | `prediction_test_bootstrap.csv`, all 2,000 rows (90% interval) | 5th and 95th percentiles -0.0007, 0.0135 |
| month 4: AUC 0.795 boosting (rounds to 79%), 0.75 logistic, latest share alone 0.68 | `prediction_landmark.csv` line 3 (L = 4) | auc_boosting 0.795, auc_logistic 0.753, auc_share only 0.677, products 936.000, cases 198.000 |
| month 4: gain over the historical rate 0.039 [0.026, 0.052]; latest share alone 0.028 | `prediction_landmark.csv` line 3 (L = 4) | gain_boosting 0.039, lo_boosting 0.026, hi_boosting 0.052, gain_share only 0.028 |
| month 4, all years: 1,376 relationships, 315 cases, 122 groups | `prediction_landmark_counts.csv` line 3 (L = 4) | products 1376, cases 315, groups 122 |
| review queue at 20%, reviewed still down: forecast (boosting) 82%, +12.0 points [3.9, 15.7] over latest share | `review_queue_eval.csv` line 2 (capacity = 0.2; weighting = relationship; ranking = forecast (boosting); measure = precision) | value 0.823, diff_vs_latest share 0.120, lo_vs_latest share 0.039, hi_vs_latest share 0.157 |
| review queue at 20%, reviewed still down: latest share 70% | `review_queue_eval.csv` line 6 (capacity = 0.2; weighting = relationship; ranking = latest share; measure = precision) | value 0.703, diff_vs_latest share nan, lo_vs_latest share nan, hi_vs_latest share nan |
| review queue at 20%, reviewed still down: historical rate 62% (random order) | `review_queue_eval.csv` line 8 (capacity = 0.2; weighting = relationship; ranking = historical rate; measure = precision) | value 0.623, diff_vs_latest share -0.080, lo_vs_latest share -0.106, hi_vs_latest share -0.015 |
| capacity curve at 5%: forecast ahead of latest share | `review_queue_capacity.csv` line 2 (L = 4; capacity = 0.05; ranking = forecast (boosting)) | precision 0.884, vs_latest 0.192, vs_latest_lo 0.100 |
| capacity curve at 50%: forecast ahead of latest share | `review_queue_capacity.csv` line 38 (L = 4; capacity = 0.5; ranking = forecast (boosting)) | precision 0.775, vs_latest 0.054, vs_latest_lo 0.020 |
| month 6 checkpoint, forecast (boosting) | `review_queue_checkpoints.csv` line 6 (L = 6; ranking = forecast (boosting)) | precision 0.882 |
| month 6 checkpoint, latest share | `review_queue_checkpoints.csv` line 8 (L = 6; ranking = latest share) | precision 0.757 |
| month 8 checkpoint, forecast (boosting) | `review_queue_checkpoints.csv` line 10 (L = 8; ranking = forecast (boosting)) | precision 0.892 |
| month 8 checkpoint, latest share | `review_queue_checkpoints.csv` line 12 (L = 8; ranking = latest share) | precision 0.811 |
| decision value, ITC vote: ahead of always, never and both historical rates at 0.45, 0.50 and 0.60 to 0.80 | `decision_value.csv` lines 43, 44, 46, 47, 48, 49, 50 (point = ITC final vote; every simlo above 0 except share only) | thresholds 0.45, 0.50, 0.60, 0.65, 0.70, 0.75, 0.80 |
| decision value, simultaneous test: over the latest share not established | `decision_value_joint.csv` line 4 (point = ITC final vote) | n_supported 0 |
| decision value, simultaneous test: at the fall, none | `decision_value_joint.csv` line 3 (point = fall first visible) | n_supported 0 |
| decision value, simultaneous test: day one, none | `decision_value_joint.csv` line 2 (point = duty starts) | n_supported 0 |
| information: case facts plus latest share, 11-input logistic | `feature_ladder.csv` line 3 (model = logistic; step = b + latest share) | inputs 11.000, precision20 0.839, auc 0.778, vs_latest 0.136 |
| information: full boosting model, all inputs | `feature_ladder.csv` line 11 (model = boosting; step = e + rivals already under duty) | inputs 22.000, precision20 0.825, auc 0.772 |
| most important input: latest share | `model_importance.csv` line 2 (feature = latest) | brier_increase 0.042, lo 0.033, hi 0.051 |
| calibration: predicts 19% come back, 26% did | `model_calibration.csv` line 2 (sample = all) | mean_pred 0.191, realized 0.256, slope 1.108 |
| recalibration: raw | `model_recalibration.csv` line 2 (sample = all; model = raw) | mean_pred 0.191, gap -0.065, brier_gain_vs_raw 0.000, brier_gain_lo 0.000, brier_gain_hi 0.000 |
| recalibration: calibrated | `model_recalibration.csv` line 3 (sample = all; model = calibrated) | mean_pred 0.222, gap -0.034, brier_gain_vs_raw 0.004, brier_gain_lo 0.001, brier_gain_hi 0.007 |
| weakest on small suppliers: AUC, smallest third | `model_errors.csv` line 8 (by = size; group = smallest third) | auc 0.690 |
| weakest on small suppliers: AUC, largest third | `model_errors.csv` line 10 (by = size; group = largest third) | auc 0.827 |
| AD/CVD-trained on Section 301: AUC 0.67 | `sec301_transfer_test.csv` line 4 (test = A: all AD/CVD -> Section 301; model = logistic) | auc 0.665 |
| Section 301's own model: AUC 0.73 | `sec301_transfer_test.csv` line 24 (test = ref: Section 301 in-domain, by chapter; model = logistic) | auc 0.730 |
| Section 301 outcomes: no fall | `s301_benchmark.csv` line 2 (sample = Section 301, real; measure = no fall) | value 0.346 |
| Section 301 outcomes: recovered | `s301_benchmark.csv` line 3 (sample = Section 301, real; measure = recovered) | value 0.242 |
| Section 301 outcomes: not recovered | `s301_benchmark.csv` line 4 (sample = Section 301, real; measure = not recovered) | value 0.357 |
| Section 301 outcomes: exited | `s301_benchmark.csv` line 5 (sample = Section 301, real; measure = exited) | value 0.055 |
| Section 301: share more than a quarter above normal came back 60%, others about 30% | `sec301_transfer_heldout_A.csv`, all rows split at rush 1.25 (checked in `tests/test_report_tables.py`) | rush > 1.25: 717 products, 0.598 back; rest 2,411, 0.302 |
| frozen forecast: 197 relationships, 54 cases, 29 groups | `frozen_forecast.csv` (all rows), `frozen_forecast_meta.json` | 197 rows, 54 cases, 29 groups; made 2026-11-15 |

## One real example from the month-4 review list

Certain epoxy resins from Taiwan, product 3907.30.00, in the January 2025 list (held out: the model
was trained only on earlier years).

**The case.** The investigation opened in April 2024. The countervailing duty preliminary was
published September 13, 2024 (month 0, when collection starts); the antidumping preliminary on
November 13, 2024, with an all-others rate of 14.81 percent (`events/adcvd_margins.csv` line 936).
Episode row: `adcvd_episodes_collapsed.csv` line 470.

**What was public at month 4.** The decision is made in January 2025. Notices count if published by
December 31, 2024; Census data count if released by the end of January 2025, which means data
through November 2024 (month 2, released January 7, 2025; `census_release_calendar.csv` line 180).
From those:

- Taiwan's pre-case share of U.S. imports of this product, among the 43 countries compared, averaged
  10.3 percent (months -18 to -13, March to August 2023; about 5.2 million dollars a month against
  46.3 million for the rivals).
- Its 3-month average share through November 2024 was 4.4 percent: 42 percent of the pre-case level
  (the "latest share"). It had already dropped below four fifths of that level at month 0.
- Both an antidumping and a countervailing preliminary, rate 14.81 percent, no retroactive-duty
  finding (correct before and after the fix), ITC final vote not yet published.
- Model inputs: `panel/landmark_features.parquet`, row sid 468, hs8 39073000, L 4 (git-ignored,
  rebuilt by `forecast/prediction_landmark.py`).

**How each rule ranked it in that month's list** (36 relationships from ten cases;
`review_queue_watchlist.csv` lines 825 to 860, this one line 826; predictions in
`prediction_landmark_heldout.csv` line 10513):

| ranking | its score | its place among 36 | reviewed at 20 percent (7.2 places)? |
|---|---|---|---|
| forecast (boosting) | 8.5 percent chance of coming back | 2nd | yes |
| latest share, lowest first | 42 percent of pre-case | 20th (ten relationships at zero come first) | no |
| historical rate | 21.4 percent came back, the same for every row | all tied | a random share |

**What happened by month 18** (March 2026; `recovery_pairs_decision_fall20.csv` line 2779): it did
not come back. Taiwan's 3-month average share was 2.7 percent at month 18, 26 percent of the
pre-case level, and never stayed at the pre-case level for three months. It kept trading, so it is
"fell and stayed down", not "no imports". The final determinations were published April 3, 2025
and the orders in May 2025, after the decision.

**The whole month, so the example is not read alone.** At 20 percent, the forecast reviewed ranks 1
to 7 and part of 8: 83 percent stayed down, against 80 percent for the latest share and 56 percent
in random order. Five relationships were reviewed by the forecast and not by the latest share (ranks
2 to 6); four stayed down and one came back (2,4-D acid from India, rank 5). One month is an
illustration, not evidence; the evidence is the 44 months in `review_queue_eval.csv`.
