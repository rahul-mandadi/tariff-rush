# The frozen forecast and the November 2026 critical-circumstances fix

The frozen forecast (`frozen_forecast.csv`, made 2026-11-15, fingerprint in `frozen_forecast_meta.json`)
is the test to score. It stays exactly as committed, and `frozen_forecast_check.py` scores it as the
outcome months are released.

## What was wrong in its inputs

One input, "retroactive duties found" (`crit`), was read from each notice with a pattern that counted
"critical circumstances do not exist" as a finding that they do, and also counted the names of other
cases a notice cites and petitioners' allegations. `events/parse_adcvd.py` now reads each notice's own
finding per country (`critical_finding`: affirmative, negative, mixed or none; tests in
`tests/test_critical_findings.py`). Nothing else in the forecast's inputs changed.

The forecast was affected in two separate ways.

1. **Its own rows.** 35 of its 197 relationships, in 7 of its 54 cases, had `crit` = 1 and now have 0:
   hardwood plywood from Vietnam (17), MDI from China (9), active anode material from China (4), silicon
   metal from Angola (2), and one each for paper file folders from Sri Lanka, rebar from Algeria and
   corrosion-resistant steel from South Africa. Each of these notices states a negative finding or
   none. The other 162 relationships' own inputs are unchanged.
2. **The model it was trained on.** 2,451 of the 16,781 training rows (59 cases) change from 1 to 0;
   the share of training rows with `crit` = 1 falls from 35.3 to 20.7 percent. A model trained on the
   corrected rows can rank any relationship differently, including the 162 whose own inputs did not
   change.

## Sensitivity check: the same procedure on corrected data

`frozen_forecast.py` was rerun in a separate folder, never over the committed files. Run first on the
original inputs, it reproduces `frozen_forecast.csv` byte for byte, so the differences below come only
from the corrected flag. The result is in `frozen_forecast_crit_sensitivity.csv`, one row per
relationship with both ranks, both chances of staying down, both review shares at 20 percent, and
whether the row's own input changed.

| | all 12 queues | the 11 scored queues |
|---|---|---|
| relationships | 197 | 184 |
| rank changed | 99 | 95 |
| of which own input changed | 22 | 22 |
| of which only the retrained model | 77 | 73 |
| entered the top 20 percent of their month | 7 | 7 |
| left it | 7 | 7 |
| entering or leaving with their own input changed | 2 of 14 | 2 of 14 |
| review places that moved | 6.4 of 39.4 | 6.0 of 36.8 |

The latest-share ranks are identical in both. The 2025-07 queue is left out of the scored test because
its outcome month was already public when the forecast was frozen.

## How to use this

Score the original frozen forecast as planned. The corrected ranking is a sensitivity check: when the
outcomes arrive, it can be scored with the same rule to show whether the flag error changed the
result. It was made after the fix and is not a pre-registered forecast.
