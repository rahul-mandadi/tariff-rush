# Archive: approaches tried and dropped

These scripts and their outputs are earlier stages of the project. None of the final report's
numbers come from them, and the final pipeline (see the repository README) does not read anything
here. They are kept so the record of what was tried, and why it was dropped, can be checked.
`docs/history/PHASE2_RESULTS.md` gives the results in full.

They were written to run from the repository root and were moved here unchanged, so they no longer
run as they are: their input and output paths point at the root. Report 1 (`REPORT1.md`, submitted)
cites some of them at their old root paths.

## The surge counterfactual and the payback ratio (the proposal's Q2)

| script | what it tried | why it was dropped |
| --- | --- | --- |
| `decomp.py` | STL counterfactual for tariff front-loading at the chapter level | its extrapolated baseline drifts when placebo-tested; replaced by comparisons with rival countries |
| `surges.py` | surge episodes and their reversal ratio, trailing-only baseline | the ratio of two noisy cumulative sums is unstable |
| `label_bands.py` | ordinal bands of the reversal ratio as a prediction target | depends on the ratio above |
| `counterfactual_hs8.py` | the same counterfactual per product-country cell at HS8 | placebo cells sit 0.115 log points below their own projection after 12 months; the baseline manufactures reversals |
| `reversal_control.py` | the ratio against untreated origins instead of a projected trend | fake events 24 months earlier produced more surges than real ones |
| `event_reversal.py` | the ratio per tariff event instead of per cell | calibration fixed, but too few events for power |
| `cell_density.py` | whether HS8 cells are deep enough for per-cell baselines | answered (they are); the per-cell design was then dropped |

## Where the displaced trade goes, and port operators as the user

| script | what it tried | why it was dropped |
| --- | --- | --- |
| `substitution_test.py` | split the targeted country's fall into own loss and other origins' gain | other origins' rise does not separate from the fake date (4.2 against 6.4 percent, p = 0.28) |
| `substitution_levels.py` | the same decomposition in levels | confirmed the log version was confounded with market share; the 79/21 split was withdrawn |
| `absorber_model.py` | predict which single origin absorbs displaced volume | a sort by incumbent size beat both models |
| `absorber_regression.py` | predict each origin's share of the displaced volume | did not beat simple benchmarks |
| `port_harvest.py`, `port_test.py` | whether displaced volume arrives through different customs districts | it arrives through substantially the same districts, so port operators were dropped as the user |

## Early versions of the antidumping aftermath

| script | what it tried | why it was dropped |
| --- | --- | --- |
| `adcvd_cohort_check.py` | whether the monthly event study survives on a fixed set of cases | showed the result was sensitive to who is measured; replaced by the fixed-cohort stacked design in `adcvd_stacked.py` |
| `retention_model.py` | predict how much of a product's trade survives a duty | period effects (the year of the case) dominated the outcome; replaced by the comparison with rival countries and the recovery outcomes |

## Outputs

The CSVs here are those scripts' outputs: `absorber_*_folds`, `adcvd_cohort_*`, `anomalies_kg`
(`decomp.py`), `counterfactual_episodes_value`, `event_reversal_*`, `port_test_real`, `retention_*`,
`reversal_episodes*`, `substitution_*`, `surge_events`, `surge_labels`. `port_test_cases.csv` and
`port_test_targets.csv` are the port test's inputs, the seven cases chosen for the district pull; no
committed script writes them.
