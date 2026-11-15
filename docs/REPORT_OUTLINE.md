# Final report outline (for Rahul and Raunak to write from)

Notes, not prose. Numbers updated 2026-11-15 after the critical-circumstances fix
(`docs/HEADLINE_SOURCES.md` lists what changed). Each section lists what it must say, the numbers (with the file each comes from)
and its figure. Write the sentences yourselves. Draft as of 2026-11-15.

Check on Canvas first: page or word limit, due date, required sections. The current
`FINAL_REPORT.md` is 6,628 words and 12 PDF pages, written in the style the instructor flagged.

## Rules from the Report 1 grading (7/25) and peer reviews

- Your own words, short sentences, readable by someone who knows nothing about trade law.
- Open with a motivating figure (instructor) and show a data sample (TA).
- Add one figure of the data cleaning and matching problem (instructor).
- Figures large enough to read: full width, big fonts.
- Define every term where it first appears: antidumping duty, countervailing duty, chapter
  (2-digit product category), Section 232, Section 301, IEEPA.
- Name the questions, not "Q1 to Q3" (readers took them for quarters).
- References numbered in the order they are cited. Appendices lettered A, B, C.
- Shorter than Report 1: cut descriptive passages, and move detail to the appendix.

## 1. Introduction (about 1 page)

- **Motivating figure (Figure 1):** copper in 2025 (`slides/fig/09_sankey.png`). A headline tariff
  taxes only part of a category.
- **Story bridge** (no bait and switch):
  - Headline tariffs hide the effect, because a list names a small slice of its category: median
    5.4% of its chapter's import value (`coverage/coverage_share.csv`).
  - Headline tariffs often hit every country, which leaves no untaxed comparison.
  - The U.S. has a second kind of tariff that names one product from one country, like mattresses
    from Vietnam: 502 cases since 2015, 275 of them in the Trump years (by first preliminary,
    `adcvd_episodes_collapsed.csv`).
  - Never present a result as being about the 2025 tariffs. Copper illustrates; China 2018 is a
    check.
- **The user and the decision:** a sourcing team at a company that buys many duty-hit products. It
  has more relationships to watch than it can review, so which first? The forecast is for the
  supplier country in a product, not for one supplier.
- **The three questions, with short names:** the rush (does trade surge before the duty?), the
  loss (how much is lost against rivals?), the recovery (does it come back, and can we tell
  early?).

## 2. Data (about 1 page)

- **Sources:**
  - Census trade API: 15.9M product x country x month rows, 2015-01 to 2026-08.
  - Federal Register notices.
  - ITC determinations.
  - Census release dates.
- **Data sample:** a small table of 5 rows from the panel (product, country, month, value,
  quantity).
- **Figure 2:** the matching funnel, `slides/fig/25_matching_funnel.png` (`slides/fig_funnel.py`).
  - 10,730 notices indexed.
  - 687 preliminary notices read (697 notice-country decisions).
  - These form 502 cases in 204 investigation groups and 63 countries; 457 can be compared with
    rivals; 381 have the full 18 months.
  - Product codes: 919 of the 935 named appear in the Census data.
  - What made it hard: product codes named in text, companion notices, side notices published
    later, and the date typo fixed in one notice.

## 3. Methods (about 1.5 pages)

- **Comparison:** the targeted country against rival countries selling the same product in the same
  month. The fake date (24 months earlier) is a falsification check: it can rule out some
  explanations but does not prove cause.
- **Four outcomes:**
  - fall: below 4/5 of the pre-case share within months 0 to 6;
  - back: three months at or above it by month 18;
  - leading to: no fall, fell and came back, fell and stayed down, fell with no imports.
- **Month-4 forecast:**
  - Uses only data Census had published by then (about five weeks after a month ends).
  - Trained only on earlier years.
  - Two models: logistic regression and gradient boosting.
- **Review queue:** each month's falling, not-yet-back relationships form one list. The team reviews
  20% of it (10% and 30% as checks). The main measure is the share of reviewed relationships still
  down at month 18.
- **Baselines:** the latest published share (what an analyst sees without a model), the historical
  rate, and a random order.

## 4. Results (about 3 pages)

1. **Loss** (Figure 3, `slides/fig/12_order_vs_negative.png`; `adcvd_stacked.csv`,
   `itc_compare.csv`):
   - Permanent duty: -0.37 log points (about 31% lost against rivals; SE 0.065; 326 cases), still
     falling at month 18.
   - ITC finds no injury: no lasting fall.
   - All 381 cases pooled: -0.19 (SE 0.11).
2. **Rush:** none before these duties (+0.02 overall, +0.07 for permanent duties), so the fall is
   from a normal level. This answers the peer reviewer's "surge or lasting loss?" question.
3. **Recovery rates** (Figure 4, `slides/fig/14_outcomes.png`; `recovery_benchmark_fall20.csv`):
   - Real cases: 26% no fall, 17% fell and came back, 42% stayed down, 16% fell with no imports in
     months 13 to 18.
   - Fake date: 50 / 29 / 17 / 3.
4. **Forecast** (Figure 5, `slides/fig/19_monthly_forecast.png`; `prediction_landmark.csv`):
   - On day one, case facts add nothing measurable: gain 0.006 over the historical rate, 90% interval
     -0.001 to 0.014 (`prediction_test.csv`, `prediction_test_bootstrap.csv`).
   - At month 4: AUC 0.795 for boosting (79.5%), 0.75 for logistic.
   - A model with the latest share only: AUC 0.68, and about 70% of the boosting model's Brier
     gain over the historical rate (0.028 of 0.039).
5. **Review queue at 20%** (Figure 6, `slides/fig/21_capacity_curve.png`; `review_queue_eval.csv`,
   `review_queue_capacity.csv`, `review_queue_checkpoints.csv`):
   - Reviewed relationships still down: 82.3% with the forecast, 70.3% with the latest share, 62% in
     random order.
   - Forecast minus latest share: +12.0 points (90% interval 3.9 to 15.7).
   - The forecast stays ahead at every capacity from 5% to 50%.
   - Months 6 and 8: 88 against 76, and 89 against 81 (`review_queue_checkpoints.csv`).
6. **Where the forecast's information comes from** (methodology study; `feature_ladder.csv`,
   `model_importance.csv`, Figure 7 `slides/fig/22_model_explain.png`):
   - Case facts plus the latest share: an 11-input logistic matches the full model.
   - Other countries' pickup and rivals already under duty add nothing.
   - The latest share is by far the most important input; next come the pre-case rush, size and
     concentration.
7. **Calibration** (`model_calibration.csv`, `model_recalibration.csv`, Figure 8
   `slides/fig/23_reliability.png` or `24_recalibration.png`):
   - The model predicts 19% come back; 26% did.
   - Recalibrating on earlier years halves the gap. The rest is drift over time.
   - Weakest on small suppliers: AUC 0.69 for the smallest third against 0.83 for the largest.
8. **Section 301 check** (`sec301_transfer_test.csv`):
   - Trained on antidumping cases, the model ranks China 2018 products right 67% of the time,
     against 73% for a model trained on them.
   - Products with a rush came back 60% of the time, against about 30% otherwise.
9. **Frozen forecast:**
   - 197 open relationships (54 cases, 29 groups), ranked on 2026-11-15 and locked with a
     fingerprint before the outcomes exist.
   - Scored as Census publishes the months, from December 2026.

## 5. Discussion (about 0.5 page)

- **Answer to the title:** closer to real. 57% fall and do not come back within 18 months.
- **What is shown:** ordering a review list beats the latest share at assumed capacities.
- **What is not shown:**
  - decision value over the latest share under assumed costs;
  - benefit to a real importer (a proposed use, not tested with users).
- **Limits:**
  - the forecast is for a country in a product, not a supplier;
  - descriptive, not causal;
  - where the lost trade goes is not estimable.
- **Callback to the opening story:** 2018 and 2025 tariffs.

## 6. Contributions, references, appendices

- **Contributions:** who did what (agree with Raunak).
- **References:** in citation order.
- **Appendix A, lookup table for a sourcing team:** a month-4 queue example.
- **Appendix B, decision value under assumed costs:** `slides/fig/18_decision_value.png`.
- **Appendix C, Section 301 details.**
- **Appendix D, dollars against quantity at the category level.**
- **Appendix E, limitations, and changes since Report 1:** the broad-tariff rush whose source
  documents were found wrong.
