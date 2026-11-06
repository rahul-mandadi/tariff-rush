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
percent of targeted products did not fall, 18 percent fell and came back, 41 percent fell and
stayed down, and 16 percent stopped trading, against 4 percent on the fake date. A simple model
using only facts public on the day the duty starts ranks later cases slightly better than these
historical rates. We also show that a tariff list typically names about 5 percent of the product
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
monthly trade about five weeks after each month closes, so the answer for a new case arrives too
late to act on. What an importer can use is what happened in past cases.

We set three questions. **Q1: is there a rush to buy before the duty, and when?** **Q2: after the
duty, does the targeted country's trade fall, and does it stay down?** **Q3: how long does
recovery take, and can it be anticipated on the day the duty starts?** The proposal framed these
as forecasting problems. We found that forecasting the level of trade fails because the year a
case happens explains far more than anything about the case (section 4), so the project became a
measurement study with one held-out prediction test, built on a comparison that removes those
year effects.

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
duty, which precedes the investigation's opening for 506 of 507 episodes. Our earlier estimate
pooled every month outside any case window into the reference; that, not a surge before the case,
produced the "42 percent above" level reported in Report 1.

Every estimate is repeated with the cases moved 24 months earlier, when nothing happened: the fake
date. A real effect has to beat it. The fake date needs 42 months of data before each case, so it
covers 286 of the 384 episodes with full follow-up.

### 2.3 Recovery and evaluation

For Q3 we follow each targeted product-country pair. Its position is the targeted country's share
of the product's imports among the panel's countries, smoothed over three months. A pair **fell**
if that share dropped at least a fifth below its pre-case level within six months of the duty, and
**came back** if it was then at or above the pre-case level for three months running by month 18.
A pair **stopped trading** if it fell, never came back, and had no imports at all in months 13 to
18. Coming back means meeting the rule once; 50 pairs that came back later stopped trading and are
counted as having come back. Each pair lands in exactly one category, each case counts once however many products it names, and only pairs with a
full 18 months enter the shares. Time to recovery is estimated by Kaplan-Meier, which also uses
cases still running, with the clock starting at the month of the fall. Intervals are 90 percent
ranges from resampling whole investigation groups.

The historical rates are themselves a forecast: what an importer would assume about a new case. We
test them on later cases, building them only from earlier cases whose 18 months had finished, and
score them with the Brier score (mean squared error of a probability; lower is better; a uniform
guess over four outcomes scores 0.75). We then test one model against them: a regularized logistic
regression for "fell and did not come back", using only facts public on the day the duty starts.
It is validated forward in time, training only on earlier cases whose outcomes were already known
and testing on each later year.

## 3. Results

### 3.1 A tariff list names a small slice of its category

A tariff order names a list of eight-digit products, not a category. Across 1,350 pairings of one
tariff list with one chapter (a broad product category such as copper or pharmaceuticals), the median list names 5.4 percent of the chapter's import
value, and a third name under 1 percent: one dollar in every hundred the chapter imports, with the
other ninety-nine outside the list. Fig. 1 shows copper, our running example. The 2025 Section 232
duty named wire, tubes and sheets, 29 percent of copper imports by value; refined cathodes, 67
percent, were exempt as an input material. Total copper imports rushed in, crashed and recovered,
which looks borrowed. Split by what the duty taxed, among imports reported in kilograms, the
semi-finished products averaged 49 thousand tonnes a month from August 2024 to January 2025 and 27
thousand from March to August 2026, while untaxed cathodes rose from 89 to 154 thousand. Fig. 1's
taxed and untaxed split is assigned from product headings, an approximation of the duty's annex. Studying whole categories
mostly watches trade a tariff never touched, which is why the rest of this report works product by
product.

[[FIG:1|slides/fig/09_sankey.png|Copper in 2025, by heading; widths are import value. The taxed and untaxed split follows Proclamation 10962, paragraph 1 against paragraph 8.]]

### 3.2 Where the duty stays, the targeted country loses ground and has not regained it by month 18

Table 1 and Fig. 2 give the aftermath. Pooled over the 384 episodes with a full 18 months, the
targeted country falls 0.19 log points against its rivals after the duty, about 17 percent, with
no movement in the year before: no clear surge to buy ahead, and no early decline. The fall
arrives as a step at the duty, reaching about 0.2 by month 3. The pooled estimate is imprecise once
uncertainty is computed over investigations (90 percent interval about minus 0.37 to minus 0.01),
and the reason is in the split. For cases that became permanent orders, the fall is 0.37 log points,
about 31 percent, deepening to 0.46 in months 13 to 18, and the chance the product is traded at all
falls 9 points. For cases the ITC voted down, there is no sustained fall: the targeted country ends
slightly above its pre-case level.

**Table 1.** The targeted country against rival suppliers of the same product, after the duty
(months 0 to 18) and late (months 13 to 18), relative to months 18 to 13 before. Log points;
standard errors over investigation groups in parentheses.

| cases | episodes (groups) | months 0 to 18 | months 13 to 18 | months 12 to 7 before |
| --- | --- | --- | --- | --- |
| all, full follow-up | 384 (150) | **-0.19** (0.11) | -0.22 (0.13) | +0.02 (0.04) |
| became a permanent order | 329 (128) | **-0.37** (0.07) | -0.46 (0.08) | +0.08 (0.06) |
| ITC found no injury | 45 (18) | +0.06 (0.03) | +0.09 (0.02) | -0.05 (0.02) |
| fake date, 24 months earlier | 286 (110) | +0.06 (0.03) | +0.08 (0.07) | +0.04 (0.04) |

[[FIG:2|slides/fig/12_order_vs_negative.png|Month by month, the targeted country against rivals selling the same product. Shading is the 95 percent interval for cases that became permanent orders.]]

The comparison between the two final outcomes describes them; it does not prove the duty caused
the gap. The ITC's vote rests on the import record itself, and the no-injury group is small and
dominated by the 2024 aluminum extrusions cases. Shared price movements in a product and month,
including general inflation, cancel in the design; a price cut by the targeted exporter alone would
not. Across the 2,492 product-country pairs whose quantity is reported in one unit throughout,
among months with trade, quantity falls 0.31 log points and dollar value 0.30. That is consistent
with a fall in volume rather than price, but both intervals include zero and we did not test
prices directly.

Where Commerce finds critical circumstances, duties can reach back 90 days, which should
discourage buying ahead. An earlier descriptive comparison found the opposite, more buying ahead in
those cases (+0.067 against -0.066, Welch p = 0.012); it uses the older sample of 508 uncollapsed
episodes and does not show whether retroactive liability changes behavior.

### 3.3 What an importer can expect, and how well history predicts it

Table 2 and Fig. 3 give the outcomes for targeted products. Fewer than half are unaffected or come
back: 25 percent never fall and 18 percent fall and recover, while 41 percent fall and stay down and
16 percent stop trading entirely. On the fake date, 4 percent stop trading. The shares barely move
with the definition of a fall: at 10, 20 or 30 percent, 16 percent stop trading. Counting from the
month of the fall, 26 percent of products that fall are back within 18 months of falling, against
58 percent on the fake date.

**Table 2.** Outcome within 18 months of a preliminary duty, each case counted once; 90 percent
intervals from resampling investigation groups.

| outcome | real cases (384) | fake date | became an order | ITC found no injury |
| --- | --- | --- | --- | --- |
| did not fall | 25% [21, 29] | 49% [45, 53] | 24% | 34% |
| fell, came back | 18% [15, 20] | 30% [26, 33] | 16% | 28% |
| fell, still down | 41% [37, 45] | 18% [15, 20] | 42% | 35% |
| stopped trading | 16% [12, 21] | 4% [3, 5] | 18% | 3% |

[[FIG:3|slides/fig/14_outcomes.png|What happened to each targeted product-country pair within 18 months of the duty, real cases against the fake date.]]

These rates hold up on later cases. Built only from cases whose 18 months had finished before each
year, they beat a uniform guess in five of six test years (Brier 0.65 to 0.72 against 0.75) and
are marginally worse in 2024 (0.754), a year dominated by cases the ITC later voted down.

Facts known on the day of the duty add a weak but measurable signal. The model of "fell and did not
come back" scores a pooled held-out Brier of 0.241 against 0.250 for the historical rate, an
improvement of 0.009 with a 90 percent interval of 0.0003 to 0.017, and ranks a bad outcome above a
good one 63 percent of the time (0.57 to 0.68). It is better in three of six test years, equal in
one, and worse in two. In the fitted model, more rival suppliers, a more concentrated market and a
supplier that was gaining share before the case go with lower predicted risk, and a higher
preliminary duty rate with higher risk. These features are correlated with each other, and none of
this shows cause. Its probabilities rank correctly but run 4 to 12 points too high in later years, so they
need recalibrating before use.

## 4. Discussion

For the importer, the answer to the title is closer to real than borrowed. When an antidumping or
countervailing duty starts, the historical odds are that the targeted country's position in the
product falls and stays down: in six cases out of ten it falls without coming back within 18
months, and in one in six the trade stops. We find no clear average surge before collection that
would later be paid back. The ITC's vote
a few months later is a second, public point to update: where the duty is confirmed, nearly one
product in five stops trading; where it is lifted, the aftermath looks like the fake date. These are
the base rates a sourcing team would want at the preliminary determination. They describe what
usually happens, not a guarantee for any supplier, and we have not tested with importers how such
teams decide.

The methodological lesson is that both the unit and the comparison matter. A product category is
the wrong unit for tariff work, because the typical list names a twentieth of it. And level
forecasts of trade fail: in our earlier attempts, the year a case happened explained 0.366 of the
variance in how much of a product's imports survived, against 0.142 for every case feature together,
and three prediction targets failed to beat simple baselines out of sample. Comparing a country with
its rivals in the same product and month removes shocks they share, including the year. The new
prediction test also changes the outcome and adds the duty rate, so we cannot credit its
improvement to the comparison alone.

Against the three questions: Q2 is answered for antidumping and countervailing duties, as a
persistent relative decline over the 18 months we observe; where the lost trade goes is not
estimable from totals, since gains spread across many rivals. Q3 is answered descriptively by the
recovery rates, with a modest predictive improvement on top. Q1 is answered only for these duties,
where there is no clear surge before collection; for the broad 2018 to 2026 tariff actions it
remains open (appendix).

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
plus 17 other non-duty notices.

### Limitations

The no-injury group is small (45 episodes in 18 groups) and dominated by one 2024 case, so the
contrast between final outcomes is descriptive. Duty rates are missing for 29 percent of notices,
and the model carries a missing-rate indicator. Copper, the running example, is one product with no
comparison country, so it illustrates rather than tests. The importer use case is plausible and
grounded in the duty timeline, but not validated with importers.

All code is in the repository. The panel: `harvest_hs10.py`, `build_panel_hs8.py`. Duty notices:
`events/harvest_adcvd.py`, `events/parse_adcvd.py`, `events/parse_margins.py`. Final outcomes:
`events/itc_check.py`, `events/itc_audit.py`. Section 3.2: `adcvd_stacked.py`, `itc_compare.py`,
`adcvd_stacked_qty.py`, `adcvd_analysis.py`. Section 3.3: `recovery_benchmark.py`,
`recovery_by_final_stage.py`, `prediction_test.py`. Section 3.1: `coverage_share.py`,
`copper_split.py`. Figures: `slides/fig_sankey.py`, `slides/fig_stacked.py`. Each script writes
the CSV its numbers come from.
