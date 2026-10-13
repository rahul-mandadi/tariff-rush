# Phase two results

Internal. Not presentation material. Run 2026-10-12 on the HS8 panel.

## What was run

The within-product test from DESIGN.md: compare a tariffed product from a tariffed origin
against the same product from origins that were not tariffed, in the same month. Two-way
fixed effects, product x month and product x origin, clustered on the cell.

Panel: 2015-01 to 2026-08, 6.09M rows after the inclusion rules, 8,100 HS8 lines,
193 partners, 95.7% of all import value. 21 events have a window of 7 days or more and
are not reversals. Split by mechanism, because the three carry different amounts of noise.

## The headline: the announcement date is not the information date

Every mechanism shows trade already moving before the Federal Register announcement. That
breaks the parallel-trends assumption the design rests on, so **none of these are clean
causal estimates.** What they are is a diagnosis, and a useful one.

Event study, months relative to announcement, baseline k in [-12,-7], in percent:

| k | ENUMERATED (301) | COUNTRY_WIDE (IEEPA) | MATERIAL_CLASS (232) |
| --- | --- | --- | --- |
| -6 | +64.7 | +8.6 | -8.2 |
| -3 | +78.5 | +10.2 | -10.3 |
| -2 | +51.9 | **+18.2** | -11.6 |
| -1 | +55.0 | +7.8 | +0.8 |
| **0** | **+97.0** | -8.5 | +0.7 |
| +1 | +24.9 | -1.4 | -10.1 |
| +3 | -9.9 | -13.5 | -22.7 |
| +6 | +6.0 | -7.0 | -24.0 |
| +12 | - | -26.2 | - |

Three different shapes, one common feature.

**Enumerated Section 301 lists** sit 50 to 78% above baseline for at least six months
before the announcement, spike to +97% in the announcement month, then collapse. The jump
from k=-1 to k=0 is about +27% above the local level, which is the shape a rush predicts.
But the level was already climbing, so the spike cannot be separated from the trend it sits
on. The likely cause of the trend is that these actions target products whose imports are
already surging, which means treatment is not as-good-as-random.

**Country-wide IEEPA actions** peak at **k=-2**, two months *before* the official
announcement, and are already falling by the announcement month. For the 2025 reciprocal
tariffs this is not mysterious: they were promised publicly for months. Importers moved on
the expectation, not the filing. Then a long, deepening decline, -26% a year out.

**Section 232 material actions** show no announcement spike at all and a sustained decline
to about -24%.

## With the trend differenced out, the rush appears

The levels above are contaminated by trend. Differencing to month-over-month growth removes
it and leaves the month-to-month jump, which is what a rush actually is. The pre-periods go
flat, and the picture changes completely.

Growth event study, percent, * = significant:

| k | ENUMERATED (301) | COUNTRY_WIDE (IEEPA) | MATERIAL_CLASS (232) |
| --- | --- | --- | --- |
| -3 | +8.5* | **+9.7*** | +3.1 |
| -2 | -15.9* | **+8.9*** | +0.4 |
| -1 | +0.6 | -9.7* | **+13.2*** |
| **0** | **+26.8*** | -15.0* | -2.8 |
| +1 | **-36.5*** | +7.7* | -9.7* |
| +2 | -7.5* | -7.6* | -14.0* |

In a differenced series a one-month level spike reads as a plus then a minus. So:

- **Section 301 enumerated lists rush in the announcement month.** Growth jumps 26.8% at
  k=0 and reverses to -36.5% at k=1, with a flat pre-period (k=-1 is +0.6%, not
  significant). This is the cleanest rush-then-payback shape in the project.
- **IEEPA country-wide actions rush two to three months early**, +9.7% and +8.9% at k=-3
  and k=-2, and are already contracting by the announcement month.
- **Section 232 material actions rush one month early**, +13.2% at k=-1, then decline.

Each matches its own level series, so the two specifications agree.

**The lead time tracks how much warning the legal mechanism gives.** Section 301 runs a
formal USTR process where the Federal Register notice is the news, so the rush lands on it.
The 2025 reciprocal tariffs were promised publicly for months, so the rush ran ahead of the
filing. Section 232 runs a Commerce investigation that is reported while it is underway,
landing in between.

That is a real answer to Q1, and a better one than the question assumed: the rush is
visible and sizeable, but the date it keys to depends on the authority being used.

## What this changes

Q1 in the problem statement is "predict the rush on the day of announcement." The data says
the announcement day is the right trigger only for Section 301. For IEEPA it is two to three
months late, for Section 232 one month late. A single predictor keyed to the Federal Register
date would miss two of the three mechanisms, so the mechanism has to be a feature.

The sustained post-period declines are the clearest signal in the whole exercise and they
run the right way for Q2, the payback question: -26% at twelve months for country-wide,
-24% at six for Section 232. Whether that is payback or a genuine demand drop still needs
the within-product control to be trustworthy, which it is not yet.

## Q2, the payback question: the cell-level reversal ratio does not work

Two counterfactuals were built and both were placebo-tested. This is the part to not
dress up.

**Extrapolated baseline (decomp.py's method, per cell).** Fit STL on the months before
each announcement, project forward. Placebo-tested at dates with no tariff, it drifts: the
median cell sits **0.115 log points below its own projection** after twelve months, and
only **39.7%** sit above it against 50% if unbiased. Selecting episodes on "excess above
the band" then preferentially picks cells whose baseline drifted low, and that error
carries into the after period. It flagged 18.6% of cell-episodes as surges where 2.5% is
the null. **This baseline manufactures reversal ratios. It should not be used, and it
retires surges.py's rolling geometric mean with it.**

**Control baseline (untreated origins of the same product).** Nothing is projected, so
nothing can drift. Calibration improves a lot: 4.5% of cell-episodes clear the 95% band,
against a 2.5% null.

But it does not survive its own placebo. Shifting every event 24 months earlier:

| | real events | placebo (-24 months) |
| --- | --- | --- |
| episodes clearing the band | 1,113 | 1,438 |
| median reversal | -1.21 | -1.65 |
| band: kept | 70% | 81% |
| band: fully returned or more | **18%** | **9%** |

The placebo produces *more* surges than the real events and a similar reversal
distribution. **At cell-episode level the reversal ratio cannot tell a real tariff from a
fake one.** The only gap that looks real is the top band, 18% against 9%, which is the
band that actually matters for Q2 and is worth pursuing at a level with more signal.

The cause is that the ratio is two noisy sums divided by each other: sd 4.35, range -24 to
+56. label_bands.py already flagged the heavy tail; banding a ratio that is mostly noise
does not create signal, it just hides the variance.

**What this means for Q2.** Payback is not measurable one cell at a time. It is visible in
aggregate: the differenced event studies show the post-period declines clearly, and that is
where the reversal ratio should be computed, per event across cells rather than per cell.
The ordinal bands are not wrong, they are being asked to label a unit of analysis too small
to carry the signal.

## What is still wrong

1. **Pre-trends in levels.** Large in two of three mechanisms, which is why the differenced
   specification is the one to read. The level results are kept above as the diagnosis, not
   as estimates.
2. **Announcement dates measure filing, not news.** Needs an earlier information date:
   first press report, or a public statement of intent.
3. **Month granularity.** 12 of 38 event-partner rows have announcement and effective date
   in the same calendar month, so the rush month also contains post-tariff days.
4. **Thin event count.** 21 usable events, 9 of them enumerated, and 2018-12-19 alone
   carries 5,921 HS8 lines, so the enumerated group is close to one big event.

## Next, in order

1. Done: the differenced specification above.
2. Build an earlier information date, so the three mechanisms can be put on one clock
   instead of three.
3. Recompute the reversal ratio per event across cells, not per cell, and placebo-test it
   the same way before believing it.

## What did work

The machinery is sound and the earlier null is explained. The chapter-level flag used
before was labelling mostly untreated trade as treated: the median action covers 5.4% of
its chapter's value. At HS8 the treatment is exact, controls exist for 89.6% of treated
product-months, and the tests above produce large, precisely estimated, clearly
*structured* coefficients instead of noise around zero. The problem is now identification,
not measurement, which is a better problem to have.
