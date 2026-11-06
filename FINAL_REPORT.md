# Borrowed or Real: What Happens to a Supplier Country After a U.S. Trade Duty

**Authors.** Rahul Reddy Mandadi, Raunaksingh Khalsa

**Sponsor.** No external sponsor. Stakeholder: the sourcing team at a U.S. importer that buys a
product from a country just named in a trade duty; secondarily, lenders exposed to that supplier.

**Github.** https://github.com/rahul-mandadi/tariff-rush

## Abstract

When the United States puts a duty on one product from one country, an importer buying that
product has to decide whether to start qualifying another supplier or wait for the business to
come back. We answer that question with history. From U.S. import records at the eight-digit
product level, 2015 to 2026, matched to 707 antidumping and countervailing duty decisions read from
their Federal Register notices, we compare each targeted country with the other countries selling
the same product in the same month, counting months with no trade as zero and checking every
estimate against the same cases moved two years earlier. Where the duty became permanent, the
targeted country's imports fell about 31 percent against its rivals, kept falling for the 18 months
we observe; where the trade commission found no injury and the duty was lifted, there was no
lasting fall. A separate check on physical quantity is consistent with a fall in volume rather than
price, but is imprecise. Across 384 past cases, 25
percent of targeted products did not fall, 17 percent fell and came back, 42 percent fell and
stayed down, and 16 percent fell, never came back and had no imports at all 13 to 18 months later,
against 3 percent on the
fake date. Built only from earlier cases, these historical rates beat a uniform guess on later
cases. On the day the duty starts, case facts add no reliable gain over them; once the fall shows in
published trade data, a model does, and by the trade commission's final vote it ranks a product that
will come back above one that will not 81 percent of the time. The model carries over to China's
2018 Section 301 tariffs, where a fall that follows a rush before the tariff is often
borrowed. We also show that a tariff list typically names about 5 percent of the product
category it touches, which is why this work has to be done product by product.

## 1. Introduction

A trade duty is a tax on imports of a product. Most U.S. duties that name one product from one
country are antidumping duties, which answer a complaint that a foreign producer sells below its
home price, or countervailing duties, which answer a complaint that it is subsidised. They follow a
fixed sequence: a domestic producer files a petition, the Commerce Department opens an
investigation, and about six months later its preliminary determination starts the duty. Importers
pay cash deposits from that day. A few months after that, the U.S. International Trade Commission
(ITC) votes on whether the imports injure U.S. producers: yes, and the duty becomes a permanent
order; no, and it is lifted and the deposits are refunded.

For an importer, the preliminary determination is the moment of decision. If the business with the
targeted country is merely interrupted, waiting is cheap. If it will not come back, the months spent
waiting are months not spent qualifying a new supplier. This is the question in our title: after a
duty, is the fall in trade borrowed, coming back once the shock passes, or real? Census publishes
monthly trade about five weeks after each month closes, so on the day the duty starts an importer
has only past cases to go on; a few months in, the new case's own data begin to arrive.

We set three questions. **Q1: is there a rush to buy before the duty, and when?** **Q2: after the
duty, does the targeted country's trade fall, and does it stay down?** **Q3: how long does
recovery take, and can it be anticipated on the day the duty starts?** The proposal framed these
as forecasting problems. Forecasting the level of trade failed, because the year a case happens
explains more than anything about the case (section 4), so the project became a measurement study
with held-out prediction tests, built on a comparison that removes those year effects.

Existing work measures tariff responses at fine product detail for good reason. Fajgelbaum et al.
[1] study the 2018 tariffs at ten digits; the ITC [2] and Imbs and Mejean [3] show that coarser
data gives systematically smaller estimates; Flaaen and Pierce [4] use continuous exposure rather
than a yes-or-no flag. Front-loading before announced tariffs is documented by Khan and
Khederlarian [5]. Our first result quantifies how much of a category a U.S. tariff actually names.

## 2. Data and methods

### 2.1 Data

Monthly U.S. imports come from the Census Bureau's international trade API, harvested at ten digits
and summed to eight, the level at which U.S. duties name products: 15.9 million rows of one
product, one partner country and one month, January 2015 to August 2026, covering 12,253 products
and 234 partners. The panel reconciles to published totals in every month (2.34 trillion dollars in
2017). Values are customs value in nominal dollars; quantity is in each product's own unit.

Duty decisions come from the Federal Register. We harvested every antidumping and countervailing
notice and kept preliminary determinations, the notices that start collection. We then read each
one's own summary and removed 21 that start no duty: 4 negative findings, 9 side notices about
retroactive duties issued separately from the case's preliminary, and 8 reviews of orders that
already existed. The 707 that remain collapse to 507 episodes, one targeted country in one
investigation, with companion antidumping and countervailing notices merged; they fall into 208
investigation groups, because one petition often names several countries. Each case's final outcome
comes from the order notices in our harvest and, where none links, from the ITC's own determination
notice for that country. Preliminary duty rates are read from each notice's rate table (the "all
others" or country-wide rate) for 511 of 718 notices.

### 2.2 Measuring the aftermath

For each episode we build a small panel: its products, the targeted country, and the rival
countries that sold those products before the case, over the 18 months before and the 18 months
after the duty starts. Who is in the panel is fixed from before the case, and a month with no trade
stays in as zero, so a supplier that stops selling is counted rather than silently dropped. Rivals
that were themselves named on the product by another case within 36 months before to 18 months
after are left out, so the comparison group is not itself under a new duty.

We then compare the targeted country with its rivals in the same product and month, with a Poisson
regression (suited to trade values that include zeros) holding fixed each product's month-to-month
swings and each country's usual level in it. Anything that moves the whole product at once,
including general inflation and demand, cancels. The coefficient reads as a proportional change
against rivals; we report it in log points, where minus 0.37 is about minus 31 percent. Uncertainty
is computed over investigation groups, not individual product rows, because one petition's
countries and products are not independent. The reference period is months 18 to 13 before the
duty, which precedes the investigation's opening for 506 of 507 episodes.

Every estimate is repeated with the cases moved 24 months earlier, when nothing happened: the fake
date. A real effect has to beat it. The fake date needs 42 months of data before each case, so it
covers 286 of the 384 episodes with full follow-up.

### 2.3 Recovery and evaluation

For Q3 we follow each targeted product-country pair. Its position is the targeted country's share
of the product's imports among the panel's countries, smoothed over three months. A pair **fell**
if that share dropped at least a fifth below its pre-case level within six months of the duty, and
**came back** if it was then at or above the pre-case level for three months running by month 18.
A pair **stopped trading** if it fell, never came back, and had no imports at all in months 13 to
18. Each pair lands in exactly one category, each case counts once however many products it names, and only pairs with a
full 18 months enter the shares. Time to recovery is estimated by Kaplan-Meier, which also uses
cases still running, with the clock starting at the month of the fall. Intervals are 90 percent
ranges from resampling whole investigation groups.

The historical rates are themselves a forecast: what an importer would assume about a new case. We
test them on later cases, building them only from earlier cases whose month 18 had been published
(Census releases a month's trade about five weeks after it ends), and
score them with the Brier score (mean squared error of a probability; lower is better; a uniform
guess over four outcomes scores 0.75). We then test models against them at three points a sourcing
team could act: the day the duty starts (target: fell and did not come back), the month a fall first
shows in published data, and the ITC's final vote (target at both: back by month 18, among products
that have visibly fallen and are not yet back). Models see only trade data published by then (a
two-month lag), notices published by that date, and comparison panels that leave out only rivals
named by cases already started: regularized logistic regression throughout, plus
shallow gradient boosting and a penalized Cox model at the later points. All are validated forward
in time, training only on earlier cases whose outcomes were already published.

## 3. Results

### 3.1 A tariff list names a small slice of its category

A tariff order names a list of eight-digit products, not a category. Across 1,350 pairings of one
tariff list with one chapter (a broad product category such as copper or pharmaceuticals), the median list names 5.4 percent of the chapter's import
value, and a third name under 1 percent: one dollar in every hundred the chapter imports, with the
other ninety-nine outside the list. Copper, our running example, is in appendix Fig. A1. The 2025 Section 232
duty named wire, tubes and sheets, 29 percent of copper imports by value; refined cathodes, 67
percent, were exempt as an input material. Total copper imports rushed in, crashed and recovered,
which looks borrowed. Split by what the duty taxed, among imports reported in kilograms, the
semi-finished products averaged 49 thousand tonnes a month from August 2024 to January 2025 and 27
thousand from March to August 2026, while untaxed cathodes rose from 89 to 154 thousand. Studying whole categories
mostly watches trade a tariff never touched, which is why the rest of this report works product by
product.

### 3.2 Where the duty stays, the targeted country loses ground and has not regained it by month 18

Table 1 and Fig. 1 give the aftermath. Pooled over the 384 episodes with a full 18 months, the
targeted country falls 0.19 log points against its rivals after the duty, about 17 percent, with
no movement in the year before: no clear surge to buy ahead, and no early decline. The fall
arrives as a step at the duty, reaching about 0.2 by month 3. The pooled estimate is imprecise once
uncertainty is computed over investigations (90 percent interval about minus 0.37 to minus 0.01),
and the reason is in the split. For cases that became permanent orders, the fall is 0.37 log points,
about 31 percent, deepening to 0.46 in months 13 to 18, and the chance the product is traded at all
falls 9 points. For cases the ITC voted down, there is no sustained fall: the targeted country ends
slightly above its pre-case level.

The comparison between the two final outcomes describes them; it does not prove the duty caused
the gap. The ITC's vote rests on the import record itself, and the no-injury group is small and
dominated by the 2024 aluminum extrusions cases. Shared price movements, including inflation, cancel
in the design; a price cut by the targeted exporter alone would not. On the 2,492 pairs whose
quantity is reported in one unit, among months with trade, quantity falls 0.31 log points and
value 0.30: consistent with lower volume rather than price, though both intervals include zero.

**Table 1.** The targeted country against rival suppliers of the same product, after the duty
(months 0 to 18) and late (months 13 to 18), relative to months 18 to 13 before. Log points;
standard errors over investigation groups in parentheses.

| cases | episodes (groups) | months 0 to 18 | months 13 to 18 | months 12 to 7 before |
| --- | --- | --- | --- | --- |
| all, full follow-up | 384 (150) | **-0.19** (0.11) | -0.22 (0.13) | +0.02 (0.04) |
| became a permanent order | 329 (128) | **-0.37** (0.07) | -0.46 (0.08) | +0.08 (0.06) |
| ITC found no injury | 45 (18) | +0.06 (0.03) | +0.09 (0.02) | -0.05 (0.02) |
| fake date, 24 months earlier | 286 (110) | +0.06 (0.03) | +0.08 (0.07) | +0.04 (0.04) |

[[FIG:1|slides/fig/12_order_vs_negative.png|Month by month, the targeted country against rivals selling the same product. Shading is the 95 percent interval for cases that became permanent orders.]]

### 3.3 What an importer can expect, and how well history predicts it

Table 2 and Fig. 2 give the outcomes for targeted products. Fewer than half are unaffected or come
back: 25 percent never fall and 17 percent fall and recover, while 42 percent fall and stay down and
16 percent fall, never come back and have no imports at all in months 13 to 18 (counting every
product, including a few that came back first, 19 percent have none then). On the fake date, 3
percent fall and stop. On the 282
cases the fake date covers, the real shares are 27, 18, 42 and 13 percent. At 10, 20 or 30 percent
definitions of a fall, 16 percent have no late imports. Counting from the
month of the fall, 26 percent of products that fall are back within 18 months of falling, against
58 percent on the fake date.

[[FIG:2|slides/fig/14_outcomes.png|What happened to each targeted product-country pair within 18 months of the duty, real cases against the fake date.]]

**Table 2.** Outcome within 18 months of a preliminary duty; 90 percent intervals as in Table 3.

| outcome | real cases (384) | fake date | became an order | ITC found no injury |
| --- | --- | --- | --- | --- |
| did not fall | 25% [21, 29] | 49% [45, 54] | 24% | 34% |
| fell, came back | 17% [15, 20] | 30% [26, 33] | 16% | 27% |
| fell, still down | 42% [37, 46] | 18% [15, 20] | 42% | 35% |
| fell, then no imports in months 13 to 18 | 16% [12, 20] | 3% [2, 5] | 18% | 3% |

Built only from earlier cases, these rates beat a uniform guess in five of six test years (Brier
0.65 to 0.72 against 0.75; 2024, dominated by cases the ITC later voted down, scores 0.752).

On the day the duty starts, case facts add no reliable gain over the historical rate (Table 3).
Later looks do better. When the fall first shows, gradient boosting beats the historical recovery
rate by 0.018, but only 0.009 (-0.000 to 0.019) beyond a model of day-one facts alone, so most of what
can be told then was known on day one. At the ITC's final vote, a logistic model ranks a product that
will come back above one that will not 81 percent of the time and cuts the Brier score by a quarter.
The latest published share alone gives 0.027; the other features add 0.018 (0.009 to 0.029), the
vote alone 0.005 (-0.001 to 0.012). It beats the rates split by vote in all six test years (2023 by
0.001); its top third runs 11 points high. Large pre-case
suppliers and high duty rates go with lower odds of coming back. Recalibrating on earlier years
makes later years worse, so we do not. Appendix
Table A1 turns both models into a lookup: where the duty was confirmed and the share is under half
its pre-case level, 13 of 100 products came back (the model expected 12); where it was lifted and the
share is back to four-fifths, 82 (expected 76).

**Table 3.** Held-out Brier scores (lower is better). Cases: eligible, and in parentheses those in
scored test years. Intervals resample investigation groups of scored cases, models held fixed.

| decision point | cases (scored) | history | best model | improvement | AUC |
| --- | --- | --- | --- | --- | --- |
| duty starts | 384 (242) | 0.249 | logistic, 0.243 | 0.005 [-0.004, 0.014] | 0.60 |
| fall first visible | 354 (222) | 0.205 | boosting, 0.187 | 0.018 [0.008, 0.029] | 0.69 |
| ITC final vote | 333 (210) | 0.180 | logistic, 0.134 | 0.045 [0.032, 0.060] | 0.81 |

### 3.4 The same model on China's Section 301 tariffs

The 2018 Section 301 tariffs taxed China alone, product by product: 6,844 products on Lists 1 to 3
at 10 to 25 percent, read from the tariff schedule's notes, compared with untaxed rivals in the same
product. Windows stop at January 2020, before China's COVID shutdown, so outcomes run 16 months.
China's share of these products' imports fell from 14.9 to 10.4 percent (fake date: up 6 percent).
Of the products, 37 percent did not fall, 23 fell and came back, 35 stayed down and 5 had no late
imports, against 25, 17, 42 and 16 for antidumping cases at the same horizon (Table A2). The
at-the-fall model trained on antidumping cases, minus the China and case-type flags, ranks Section
301 products correctly 70 percent of the time (a model trained on Section 301 itself: 76) and beats
even Section 301's own recovery rate by 0.026 (0.022 to 0.031); trained on Section 301, it beats
antidumping cases from 2020 on by 0.011 (0.001 to 0.020). Most antidumping training cases come after
2018; trained only on the 26 published before September 2018, it ranks as well (0.71) but expects
too few recoveries. One pattern stands out: products whose
China share ran more than a quarter above its usual level just before the tariff came back 60
percent of the time, against about 30 for the rest. That part of the fall was borrowed. Each list
is one date, so these describe products; they do not estimate a list's effect.

## 4. Discussion

For the importer, the answer to the title is closer to real than borrowed. After an antidumping or
countervailing duty, six products in ten fall without coming back within 18 months, and one in six
falls and has no imports a year on; there is no clear average surge before collection to pay back.
Where the ITC confirms the duty, nearly one in five falls and has none a year on; where it lifts it,
the aftermath looks like the fake date. These are base rates, not guarantees for any one supplier,
and they are untested with importers.

The methodological lesson is that unit, comparison and decision point all matter. A category is the
wrong unit, because the typical list names a twentieth of it. Level forecasts failed because the
year of a case explained more than any case feature; comparing a country with its rivals in the
same product and month removes that. On day one the best forecast is the historical rates; by the
ITC vote a model does better, mostly by reading how far the published share has come back, and it
carries over to a different tariff law.

Against the three questions: Q2 is answered for these duties, as a persistent relative decline over
the 18 months we observe; where the lost trade goes is not estimable from totals. Q3 is answered by
the recovery rates and by a model that sharpens them by the ITC vote. Q1 is answered for these
duties (no clear surge before collection) and in part for Section 301, where a rush predicts a
recovery; for the broad 2018 to 2026 tariff actions it remains open (appendix).

## 5. Statement of contributions

Both authors contributed equally. Rahul Reddy Mandadi led data collection, the eight-digit panel
and the event tables. Raunaksingh Khalsa led exploratory analysis, anomaly detection and the first
presentation. Both set the research questions, chose the identification strategy, and wrote this
report.

## 6. References

[1] Fajgelbaum, P., Goldberg, P., Kennedy, P. and Khandelwal, A. (2020). The Return to
Protectionism. *Quarterly Journal of Economics* 135(1), 1-55.

[2] Schrammel, M. and Schreiber, S. (2023). How Does Data Aggregation Impact Elasticity of
Substitution Estimation? *USITC Economics Working Paper* 2023-10-B.

[3] Imbs, J. and Mejean, I. (2015). Elasticity Optimism. *American Economic Journal:
Macroeconomics* 7(3), 43-83.

[4] Flaaen, A. and Pierce, J. (2019). Disentangling the Effects of the 2018-2019 Tariffs on a
Globally Connected U.S. Manufacturing Sector. *Federal Reserve FEDS* 2019-086.

[5] Khan, S. Y. and Khederlarian, A. (2021). How does trade respond to anticipated tariff changes?
Evidence from NAFTA. *Journal of International Economics* 133, 103538.

**Data sources.** United States Census Bureau international trade API; Federal Register API;
United States International Trade Commission Harmonized Tariff Schedule, chapter 99; United States
International Trade Administration antidumping and countervailing duty case index; ITC final
determination notices in the Federal Register.

## 7. Appendix

[[FIG:A1|slides/fig/09_sankey.png|Copper in 2025, by heading; widths are import value. The taxed and untaxed split follows Proclamation 10962, paragraph 1 against paragraph 8, assigned from product headings, an approximation of the duty's annex.]]

### A lookup for a sourcing team

**Table A1.** Lookup: of 100 held-out products in each cell, the model's expected number back by month 18 / the number that came back (cases in the cell).

| when the fall shows: supplier's pre-case imports | rate up to 25% | rate over 25% | rate not published |
| --- | --- | --- | --- |
| under USD 1M | 35 / 56 (51) | 30 / 30 (38) | 35 / 43 (27) |
| USD 1M to USD 10M | 23 / 36 (52) | 18 / 16 (51) | 26 / 25 (28) |
| over USD 10M | 20 / 25 (78) | 16 / 15 (72) | 19 / 28 (36) |

| at the ITC vote: latest share against pre-case | duty confirmed | duty lifted |
| --- | --- | --- |
| under half | 12 / 13 (144) | 38 / 32 (24) |
| half to 4/5 | 21 / 22 (68) | 55 / 40 (20) |
| 4/5 or more | 45 / 52 (50) | 76 / 82 (18) |

### Section 301 details

**Table A2.** Section 301 Lists 1 to 3 (6,844 listed products, 4,908 with a pre-case share) against antidumping cases, 16-month horizon; 90 percent intervals from resampling 2-digit chapters (Section 301) or investigation groups (antidumping), holding fitted models fixed. Transfer tests use comparison panels that leave out only rivals named by cases already started.

| outcome | Section 301 | fake date | antidumping |
| --- | --- | --- | --- |
| did not fall | 37% [34, 39] | 44% [41, 47] | 25% [22, 29] |
| fell, came back | 23% [22, 25] | 30% [28, 32] | 17% [15, 19] |
| fell, still down | 35% [32, 37] | 23% [22, 24] | 42% [38, 46] |
| fell, then no imports in months 11 to 16 | 5% [4, 7] | 3% [3, 4] | 16% [12, 20] |

| trained on, scored on | products | AUC | Brier | gain over the target's own rate |
| --- | --- | --- | --- | --- |
| antidumping, all cases, to Section 301 (boosting) | 3,128 | 0.70 | 0.207 | 0.026 [0.022, 0.031] |
| antidumping published by Sep 2018, to Section 301 (logistic) | 3,128 | 0.71 | 0.237 | -0.004 [-0.012, 0.004] |
| Section 301, to antidumping from 2020 (logistic) | 1,252 | 0.67 | 0.185 | 0.011 [0.001, 0.020] |
| Section 301 on itself, by chapter (reference) (boosting) | 3,128 | 0.76 | 0.188 | 0.045 [0.039, 0.050] |

### Dollars and quantity at the category level

Our unusual-month score measures how far a chapter's largest 2025 month sat above a line drawn
from its own recent trend and seasonal pattern, as a share of its usual range. On dollars,
pharmaceuticals rank first of 63 comparable chapters (2.26); on quantity, 62nd (minus 0.34). Its
March jump is a shift toward Swiss medicines at about 5,185 dollars a kilogram, which lifts dollars
far more than tonnes. Cocoa scores 1.00 on dollars and 0.69 on quantity; its import value per unit
roughly doubled from 2022 to 2025. A category's dollar total alone misleads in both directions.
Deflating by the BLS import price index keeps 8 of the top 10 chapters; by the non-fuel index,
9 of 10.

### The tariff-action rush (Q1 for broad tariffs)

Report 1 described month-by-month jumps around Section 301, IEEPA and Section 232 actions. A
document-by-document audit found 13 of the 19 study documents wrong in date, countries, direction
or product list, and the analysis has no fake-date check, so we do not report it. Correcting those
documents is the first step for anyone extending this work.

### Changes from Report 1

Report 1 put the antidumping aftermath at minus 0.30 log points, "about 26 percent", against a
placebo at p < 0.0001. Rebuilt on a fixed set of products with zero months kept, with the 21
non-duty notices removed, companion notices merged and uncertainty computed over investigation
groups, the pooled estimate is minus 0.19 (SE 0.11), and minus 0.37 (SE 0.07) for cases that became
orders. Report 1 counted 8 notices without an affirmative finding; reading every summary gives 4,
plus 17 other non-duty notices. Report 1's "42 percent above its level before the case" came from
pooling every month outside any case window into the reference, not from a surge before the case.
Where Commerce finds critical circumstances, duties can reach back 90 days. An earlier descriptive
comparison found more buying ahead in those cases, not less (+0.067 against -0.066, Welch p = 0.012,
on the older 508-episode sample); it does not show that retroactive liability changes behavior.

### Limitations

The no-injury group is small (45 episodes in 18 groups) and dominated by one 2024 case, so the
contrast between final outcomes is descriptive. Duty rates are missing for 29 percent of notices,
and the model carries a missing-rate indicator. Copper, the running example, is one product with no
comparison country, so it illustrates rather than tests. The importer use case is plausible and
grounded in the duty timeline, but not validated with importers. For Section 301, the product
lists come from the 2026 tariff schedule, so about a tenth of lines renumbered since 2018 are
missing; roughly 2,000 product exclusions, some retroactive, are not removed, so some taxed
products were not taxed; Chinese goods shipped through third countries can inflate rivals' shares;
and each list is one date, so the intervals cover products, not the list's common shock.

All code is in the repository. The panel: `harvest_hs10.py`, `build_panel_hs8.py`. Duty notices:
`events/harvest_adcvd.py`, `events/parse_adcvd.py`, `events/parse_margins.py`. Final outcomes:
`events/itc_check.py`, `events/itc_audit.py`. Section 3.2: `adcvd_stacked.py`, `itc_compare.py`,
`adcvd_stacked_qty.py`, `adcvd_analysis.py`. Section 3.3: `recovery_benchmark.py`,
`recovery_by_final_stage.py`, `prediction_test.py`, `prediction_stage2.py`, `calibrated_lookup.py`.
Section 3.4: `events/build_301_lists.py`, `sec301_benchmark.py`, `sec301_transfer_test.py`,
`recovery_lib.py`. Section 3.1: `coverage_share.py`,
`copper_split.py`. Figures: `slides/fig_sankey.py`, `slides/fig_stacked.py`. Each script writes
the CSV its numbers come from.
