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

## Event level: calibration fixed, power gone

Aggregating across the cells an event touches before taking the ratio, one number per event
instead of per cell. Same control baseline, same placebo at -24 months.

Calibration is now right:

| | real | placebo (-24m) |
| --- | --- | --- |
| event-partner groups | 34 | 36 |
| surge rate above the band | **8.8%** | **2.8%** |

The placebo lands on 2.8% against a 2.5% null, and the real events clear the band three
times as often. That is the first clean separation of real from fake in the payback work,
and it says real tariffs do produce detectable surges at the event level.

But only three groups surged, and two of them (2025-02293, 2025-02576) are duplicate notices
of the same China action measured on a single HS8 cell. So the usable n is two. No reversal
ratio can be estimated from that, and no significance test will run on it.

The aggregation also brings dilution back in a new place. The one country-wide group that
surged spans 1,882 cells and shows excess_during of 0.37; the single-cell enumerated group
shows 3.92. Averaging a real rush in a few lines across the whole of a country's trade
shrinks it toward nothing, which is the same problem as the old chapter-level flag, one
level up.

**Verdict: neither cell level nor event level yields a usable reversal estimate.** Cell level
has power but no calibration. Event level has calibration but no power. The binding
constraint is not the method, it is that there are 21 usable events.

## Antidumping and countervailing duty cases: the event sample that works

The 21 Section 232/301/IEEPA events were never going to be enough, and their median
announcement-to-effective window of four days is below what monthly data can resolve. AD/CVD
cases are the same kind of action with none of those problems: one country, an explicit
product scope, and months between the case becoming public and duties being collected.

The original harvest searched five Section 232/301/IEEPA phrases, so these were caught only
by accident: 155 documents in 2018 falling to 14 in 2025, which tracks the search terms
rather than Commerce's caseload. Pulling the whole International Trade Administration index
by year instead gives 10,730 notices, of which 3,399 are duty-starting stages once
administrative reviews are excluded, spread evenly at 163 to 403 a year.

Parsed: 993 cases, 70 countries, 1,297 HS8 lines, and **1,064 preliminary determinations with
a recoverable window**, median 150 days. The initiation date is read out of the preliminary
notice's own background section, because the initiation notice itself often falls outside the
harvest. After requiring a window of at least 60 days and a live panel cell, **508 episodes**
against **473 placebo** episodes.

### The result: a large, durable loss of share, and no rush

| | real | placebo (-24m) |
| --- | --- | --- |
| episodes | 508 | 473 |
| median excess_during | +0.031 | +0.037 |
| **median excess_after** | **-0.316** | **+0.020** |
| surge rate | 6.1% | 3.6% |

`excess_after` separates from its placebo at **p < 0.0001** on both a rank test and a t-test.
This is the strongest and best-identified result in the project. `excess_during` does not
separate at all (Mann-Whitney p = 0.37): there is **no detectable rush** before an AD/CVD
preliminary determination (p = 0.47 against zero).

### Why this answers Q2 rather than dodging it

The baseline is other origins of the same product in the same month. That is what makes the
after-effect interpretable. If U.S. demand for the product had fallen, every origin would fall
together and the gap would not move. The gap moves by -0.32 log points, about 27 percent, so
the targeted origin lost share **to other origins of the same product**.

So for AD/CVD actions the aftermath is mostly not payback and mostly not a demand decline. It
is mostly relocation, with leakage: about four fifths of the displaced volume turns up from
other origins and about one fifth does not. Q2 asked whether the drop is borrowed volume
returning or demand genuinely falling. For this class of events the answer is largely a third
thing the question did not anticipate. See the decomposition below, which is what establishes
the split; the gap on its own cannot.

There is no rush to repay, which is also why the reversal ratio stays noisy here: it divides
by an excess that is not reliably different from zero.

### The month-by-month path, which is what makes it credible

673 events, baseline k in [-18,-13], k = 0 is the month duties start being collected:

| k | effect | | k | effect |
| --- | --- | --- | --- | --- |
| -12 | +36.8%* | | **0** | **+17.7%\*** |
| -9 | +42.1%* | | 1 | +10.3%* |
| **-6** | **+39.9%\*** | | 2 | +2.4% |
| -5 | +45.6%* | | 3 | +0.2% |
| -4 | +40.1%* | | 6 | -7.0%* |
| -3 | +32.8%* | | 9 | -3.1% |
| -1 | +30.4%* | | 12 | -3.3% |

**No rush, and the opposite of one.** With a median window of 150 days, initiation falls around
k=-5 or k=-6. The series is flat from k=-12 to k=-4, then **declines from k=-3 onward**, before
duties are collected. If importers were buying ahead there would be a spike in the months
before k=0. Instead they start pulling back once the case is public.

That fits the law. AD/CVD duties can be applied retroactively, reaching back 90 days before
suspension of liquidation or to the initiation notice, whichever is later. Goods imported
during the window are therefore at risk of being taxed anyway, so the incentive runs the other
way: buy less once a case is filed, not more. This is the mechanism that makes AD/CVD different
from Section 301, where the rush is large and lands on the announcement month.

**The decline completes by k=2 and does not reverse.** From +30.4 percent at k=-1 to +2.4
percent at k=2 and roughly zero to slightly negative through k=12, a fall of about 0.30 log
points, matching the episode estimate of -0.32 independently.

The elevated pre-level is the selection that creates these cases: Commerce acts where one
origin has unusually high import penetration in a product. It is flat from k=-12 to k=-4, so it
shifts the intercept rather than the estimate.

### Robustness

The headline does not depend on where the thresholds were put. Varying the horizon H and the
minimum window, median excess_after against its placebo:

| H | min window | real | placebo | p |
| --- | --- | --- | --- | --- |
| 6 | 90d | -0.266 | +0.050 | <0.0001 |
| 6 | 120d | -0.264 | +0.050 | <0.0001 |
| 9 | 60d | -0.319 | +0.045 | <0.0001 |
| 12 | 90d | -0.343 | +0.052 | <0.0001 |
| 12 | 120d | -0.343 | +0.052 | <0.0001 |

The decline deepens with the horizon, -0.27 at six months against -0.34 at twelve, which is
what a sustained loss of share looks like and not what a temporary dip would look like. The
surge rate sits at 5.9 to 6.0 percent for real events against 5.1 to 5.2 percent for placebos
in every configuration, so the absence of a rush is not a threshold artefact either.

### An accidental validation

Commerce can find "critical circumstances", which section 733(e)(1)(B) defines as imports
having "been massive over a relatively short period" - a legal determination that a surge
happened, made independently of anything in this project.

Episodes where Commerce made an affirmative finding show a rush, +0.263 mean excess_during,
against -0.106 for episodes where the question was never raised (Mann-Whitney p = 0.033,
Welch p = 0.041). Our measure agrees with Commerce's own statutory finding. On the full data
the broader flag, any mention of critical circumstances, splits the same way: +0.063 against
-0.065 (Welch p = 0.015, n = 187 against 321).

**Exploratory, not a result.** n = 10 affirmative against 28 not-raised, and it is one of
several tests run on this data. It is reported because it points the right way, not because
it is established.

### Decomposing the gap: mostly substitution, with real leakage

The episode test measures a gap, the named origin against other origins of the same product.
A falling gap is consistent with the origin falling or with the others rising, and those mean
opposite things to anyone committing capacity. substitution_test.py splits it into the three
absolute series, 583 episodes against 521 placebo.

| | real | placebo (-24m) | separates? |
| --- | --- | --- | --- |
| tariffed origin | **-21.7%** | +13.8% | yes, p < 0.0001 |
| other origins | +4.2% | +6.4% | **no, p = 0.28** |
| product total | **-1.6%** | +6.7% | yes, p < 0.0001 |

**The "other origins rise" leg does not survive its placebo.** Other origins do grow, by about
4 percent, but they grow slightly more than that in the placebo, so none of it can be credited
to the tariff. Reporting substitution from that leg alone would have been wrong.

What does survive is the comparison of totals. The named origin ends about 36 points below its
placebo trend while the product total ends about 8 points below, so **roughly 79 percent of the
displaced volume is absorbed elsewhere and roughly 21 percent genuinely disappears.**

Per episode: the origin falls in 69 percent of cases; the total roughly holds in 29 percent and
falls in 39 percent. So the average hides two regimes, and which regime a case lands in is
itself worth predicting.

**This corrects an earlier reading in this file that described the aftermath as substitution
full stop.** It is mostly substitution. It is not only substitution.

### The port test: the displaced volume arrives through the same districts

A stakeholder review objected that everything here is denominated in dollars at HS8 by country,
while capacity is committed at a facility. If replacement volume arrives through different
districts there is a lane story and a terminal operator cares. If it arrives through the same
ones, the cargo changes flag and nobody downstream sees anything.

Census publishes DISTRICT on the same endpoint and it supports HS10, so this is testable. Seven
large cases were pulled at district level, 1.45M rows across 42 districts and 140 months,
$713B. Four where the volume was absorbed elsewhere and three where it was largely lost. The
metric is total variation distance between the district share vectors before and after, which
reads directly as "this fraction of the volume changed district", each paired with the same
24 month placebo.

| case | country | regime | absorbed | tvd real | tvd placebo |
| --- | --- | --- | --- | --- | --- |
| 2019-21998 | China | substituted | 0.87 | 0.054 | 0.043 |
| 2019-17198 | China | substituted | 0.82 | 0.050 | 0.041 |
| 2016-15837 | China | substituted | 0.81 | 0.058 | 0.068 |
| 2019-16327 | China | substituted | 0.72 | 0.057 | 0.048 |
| 2024-22994 | Vietnam | lost | 0.37 | 0.237 | 0.215 |
| 2025-11383 | China | lost | 0.32 | 0.106 | 0.073 |
| 2025-15781 | China | lost | 0.27 | 0.098 | 0.077 |

**The answer is no.** Median tvd is 0.058 for real events against 0.068 for placebos, so the
district mix is if anything marginally *more* stable after a tariff than in a random window.
For the four absorbed cases it is 0.056 against 0.046. In the most absorbed case, 87 percent of
displaced volume replaced, the largest single district move is Savannah at +1.6 points and
everything else is under 1.3.

**This kills the terminal as the primary stakeholder**, which is the framing in the proposal and
in STORY.md. Volume leaves one origin, arrives from another, and comes through the same gates in
nearly the same proportions. An operator committing crew and yard space would see almost nothing
worth acting on.

Who it does matter to: whoever carries origin risk rather than throughput risk. The importer
doing the re-sourcing, the supplier losing the market, a lender financing either. That is a
different stakeholder with a different decision and the project should say so plainly instead of
keeping a terminal framing the data does not support.

One hint of a lane story survives and is worth a look: Laredo gains 1.2 points in the most
absorbed China case, which is a land crossing rather than a berth and would be consistent with
sourcing moving to Mexico. It is small and it is one case.

**Two limits on this test.** Districts are groups of ports, 42 of them, so a shift between two
ports inside one district is invisible here. And it is measured in customs value, not containers
or lifts, so a change in value mix is not necessarily a change in box count. Both would need
port-level data in TEU to settle, which Census does not publish at HS10.

### Q3: the volume moves, but the destination is not predictable from the tariff

If a few named origins absorbed the displaced volume there would be a lane story worth selling.
311 real episodes against 141 placebo, measuring how concentrated the share gains are:

| metric | real | placebo | p |
| --- | --- | --- | --- |
| top absorber's share of all gains | 0.375 | 0.416 | 0.067 |
| top three share | 0.719 | 0.775 | 0.018 |
| **effective number of absorbers (1/HHI)** | **4.4** | **3.7** | 0.019 |
| origins gaining share | 13 | 11 | 0.32 |

**Absorption after a real tariff is more diffuse than in a random window, not less**, and
significantly so. That is the opposite of what a lane story requires.

It is also not predictable from the identity of the target. Conditional on China being tariffed
(n = 113) the most frequent absorber is Mexico, in 24 percent of cases, with 5.5 effective
absorbers. Every other treated country behaves the same way, with the best conditional absorber
landing between 20 and 33 percent, usually on small samples. Top-gainer counts are flat across
Canada 36, Mexico 36, Vietnam 31, Korea 30, Thailand 20, India 20.

One nuance runs the other way and should not be lost. Per case, the single largest absorber
picks up share roughly equal to the entire loss, median 1.01 times it. So a lane does shift in
each individual case. It is a different lane each time and nothing about the tariff says which.

**Consequence for the stakeholder.** Combined with the port test, this settles it. The US gate
does not move and the destination origin is not predictable from the tariff, so a terminal has
no decision. What remains is origin risk: suppliers losing the market, lenders exposed to them,
and importers wanting to move before the crowd. A carrier is still in scope, which the port
test did not rule out: the US district is unchanged but the origin port and ocean leg are not.

**Both prediction framings were tried and both fail.** Forward-chaining validation by year,
grouped by case, so no case is in both folds and the model is always tested on later cases.
307 cases, 6,572 case-candidate rows.

*Which origin absorbs most* (classification, 1 of about 13):

| | mean AUC | top-1 accuracy |
| --- | --- | --- |
| naive: biggest incumbent | **0.808** | **0.22** |
| logistic regression | 0.803 | - |
| gradient boosting | 0.757 | 0.20 |

The sort wins. Feature importance says why: share_pre at 0.32 and log_value_pre at 0.26
dominate, so the models spend their capacity rediscovering "big suppliers absorb". Top-1 of
0.22 against a 4.6 percent random baseline is about five times chance and wrong three times in
four.

*How much of the loss each origin takes* (regression on frac = share gain / treated loss):

| | mean R2 | within-case rank correlation |
| --- | --- | --- |
| proportional reallocation (the economic null) | **-0.058** | -0.013 |
| ridge | -0.046 | - |
| gradient boosting | -0.250 | +0.056 |

Every R2 is at or below zero, so worse than predicting the mean. Proportional reallocation,
which is what trade theory would hand you for free, also fails. The target has sd 0.68 around a
median of 0.008.

**So the volume moves and the destination is not predictable.** You can weakly rank who is
likely to take the most, and that ranking is just supplier size. You cannot predict how much
anyone takes by any method tried, including the null. Q3 is answered, in the negative, and the
negative is well evidenced rather than a failure to try.

**Consequence for the project.** The strength here is measurement and identification: the
coverage fix that explained the original null, the within-product design that separates a tariff
from a price shock, and placebo discipline that retired three estimators. There is no model that
beats a heuristic. If a modelling contribution is wanted, the untried candidate is Q1: predict
whether an announcement produces a rush and how large, from announcement-day features including
the legal authority. That is what the proposal actually promised and it has not been attempted.

See q3_absorbers.py, absorber_model.py, absorber_regression.py.

### Q2 as a prediction problem: it fails too, and now we know why

The aftermath is measurable in aggregate. The obvious next step is to predict it per case: when
duties land on one origin, does the product's total import volume hold up or fall? 583 episodes,
which is 28 times the 21 events the rush analysis rests on, and the drivers should be
structural: how many alternative suppliers exist, how concentrated the market is, how large the
targeted origin was, whether the alternatives are themselves under duty.

Forward-chaining validation by year, grouped by case. Two deliberately hard benchmarks:
predicting the training mean, and predicting that the basket simply continues its own recent
growth.

| | mean R2 | rank correlation |
| --- | --- | --- |
| predict the training mean | -0.898 | - |
| predict the pre-period trend | -1.914 | - |
| ridge | -1.123 | -0.191 |
| gradient boosting | -0.967 | +0.013 |

Everything is negative, including predicting the training mean, which is the tell. If the mean
of the training years does not transfer to the next year, the outcome is not a stable function
of anything measured at case level.

**The cause: period effects dominate.** Variance in the target explained by the year of the case
alone is **0.366**. Variance explained by all eleven structural features together, in sample and
therefore optimistically, is **0.142**, and out of sample it is negative. Year means run from
+0.544 in 2021 to -0.313 in 2024, a swing far larger than anything market structure contributes.
Post-covid restocking lifted everything; the 2024-25 tariff era pulled everything down.

So the retention outcome is mostly about *when* a case happened, not *what* the affected market
looked like. That also explains the two earlier prediction failures rather than leaving them as
unrelated nulls.

The ridge coefficients are directionally sensible even though the model is useless: a larger
targeted origin, a more concentrated market, and a higher share of alternatives themselves under
duty all push the total down. The economics is right. The predictive power is not there.

### What this means for the project

Three prediction targets have now failed, and the reason is consistent: **the level of trade
after a duty is dominated by the macro period, which is not knowable in advance.**

This is not a wasted finding, because it is exactly why the measurement works. The
within-product across-origin design compares a tariffed origin against other origins of the
same product *in the same month*, which differences out the period effect entirely. That is why
the -27% aftermath estimate survives at p < 0.0001 while every level prediction collapses.

The honest framing of the project is therefore: **the effect is identifiable but not
forecastable.** We can say what a duty does to a targeted origin's trade, with placebo
discipline behind it. We cannot say in advance how much volume a given product will keep,
because that depends mostly on what the following year looks like for trade as a whole.

That is a defensible result with evidence behind it, and it is a more useful thing to report
than a model nobody should trust.

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
3. Done, and it does not work on the Section 232/301/IEEPA events: see the event-level
   section. It does work on AD/CVD cases, where the answer turns out to be substitution
   rather than payback.
4. Finish the AD/CVD harvest and reparse; roughly 500 documents were still downloading
   when these numbers were produced, so every count here is a floor.
5. Extend the panel back to 2010, which the Census HS10 series supports, to widen the
   window AD/CVD cases fall into.

## What did work

The machinery is sound and the earlier null is explained. The chapter-level flag used
before was labelling mostly untreated trade as treated: the median action covers 5.4% of
its chapter's value. At HS8 the treatment is exact, controls exist for 89.6% of treated
product-months, and the tests above produce large, precisely estimated, clearly
*structured* coefficients instead of noise around zero. The problem is now identification,
not measurement, which is a better problem to have.
