# Borrowed or Real: What Happens to a Supplier Country After a U.S. Trade Duty

**Authors.** Rahul Reddy Mandadi, Raunaksingh Khalsa

**Sponsor.** No external sponsor. Stakeholder: the sourcing team at a U.S. importer that buys a
product from a country just named in a trade duty; secondarily, lenders exposed to that supplier.

**Github.** https://github.com/rahul-mandadi/tariff-rush

## Abstract

When the United States puts a duty on one product from one country, an importer buying that
product has to decide whether to start qualifying another supplier or wait for the business to
come back. We answer that question with history. From U.S. import records at the eight-digit
product level, 2015 to 2026, matched to 694 antidumping and countervailing duty notices (704 notice-country decisions) read from
their Federal Register notices, we compare each targeted country with the other countries selling
the same product in the same month, counting months with no trade as zero and checking every
estimate against the same cases moved two years earlier. Where the duty became permanent, the
targeted country's imports fell about 31 percent against its rivals, kept falling for the 18 months
we observe; where the trade commission found no injury and the duty was lifted, there was no
lasting fall. A separate check on physical quantity is consistent with a fall in volume rather than
price, but is imprecise. Across 380 past cases, 26
percent of targeted products did not fall, 17 percent fell and came back, 42 percent fell and
stayed down, and 16 percent fell, never came back and had no imports at all 13 to 18 months later,
against 3 percent on the
fake date. On the day the duty starts, case facts add little over these historical rates.
Among products whose fall is already visible, a monthly model does better on later years: by month
5 it ranks a product that comes back above one that does not in 80 percent of pairs. Its added
decision value is narrower: tested jointly over all assumed cost ratios, the forecast at the
trade commission's vote beats always or never qualifying and the historical rates at most ratios
from 0.45 to 0.80 of the avoidable loss, but not a simple rule built on the latest published share. Public records show switching around
these cases is common and slow, though few purchasers tie it to the duty. The model carries over to China's 2018 Section 301 tariffs,
where a fall that follows a rush before the tariff is often borrowed. We also show that a tariff list typically names about 5 percent of the product
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

For an importer, the preliminary determination opens the decision. If the business with the
targeted country is merely interrupted, waiting is cheap, and deposits are refunded if the duty is
lifted. If it will not come back, the months spent waiting are months not spent qualifying a new
supplier. Switching is common and slow: in the ITC's final reports, 27 of 54 responding purchasers
of aluminum extrusions and 23 of 45 of steel nails changed suppliers during the investigation
period, mostly for reasons such as shortages, with only a few per report tying it to the case; and
qualifying a new supplier took from days to 18 months, about seven on average for tin mill products
[6, 7]. Some firms act at the preliminary: Floor & Decor's annual report describes moving its
sourcing of Chinese ceramic tile after the 2019 preliminary duties [8]. This shows the decision and
its timing exist; it does not validate the forecasts here. This is the question in our title: after a
duty, is the fall in trade borrowed, coming back once the shock passes, or real? Census publishes
monthly trade about five weeks after each month closes, so on the day the duty starts an importer
has only past cases to go on; a few months in, the new case's own data begin to arrive.

We set three questions. **Q1: is there a rush to buy before the duty, and when?** **Q2: after the
duty, does the targeted country's trade fall, and does it stay down?** **Q3: how long does
recovery take, and how early can it be anticipated?** The proposal framed these
as forecasting problems. Forecasting the level of trade failed, because the year a case happens
explains more than anything about the case (section 4), so the project became a measurement study
with held-out prediction tests, built on a comparison that removes those year effects.

Existing work measures tariff responses at fine product detail [1, 4] because coarser data gives
smaller estimates [2, 3], and documents buying ahead of announced tariffs [5]. Our first result
quantifies how much of a category a U.S. tariff actually names.

## 2. Data and methods

### 2.1 Data

Monthly U.S. imports come from the Census Bureau's international trade API, harvested at ten digits
and summed to eight, the level at which U.S. duties name products: 15.9 million rows of one
product, one partner country and one month, January 2015 to August 2026, covering 12,253 products
and 234 partners. The panel reconciles to published totals in every month (2.34 trillion dollars in
2017). Values are customs value in nominal dollars; quantity is in each product's own unit.

Duty decisions come from the Federal Register. We harvested every antidumping and countervailing
notice and kept preliminary determinations, the notices that start collection. We then read each
one's own summary and removed 24 that do not start a new duty: 4 negative findings, 9 side notices about
retroactive duties issued separately from the case's preliminary, 8 reviews of orders that
already existed, and 3 circumvention findings on existing orders. The 704 notice-country decisions
that remain (694 notices) collapse to 504 episodes, one targeted country in one
investigation, with companion antidumping and countervailing notices merged; they fall into 205
investigation groups, because one petition often names several countries. Each case's final outcome
comes from the order notices in our harvest and, where none links, from the ITC's own determination
notice for that country. Preliminary duty rates are read from each notice's rate table (the "all
others" or country-wide rate) for 507 of the 694 notices.

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
duty, which precedes the investigation's opening for 503 of 504 episodes.

Every estimate is repeated with the cases moved 24 months earlier, when nothing happened: the fake
date, which a real effect has to beat (283 of the 381 episodes have the 42 months of data it needs).

### 2.3 Recovery and evaluation

For Q3 we follow each targeted product-country pair. Its position is the targeted country's share
of the product's imports among the panel's countries, smoothed over three months. A pair **fell**
if that share dropped at least a fifth below its pre-case level within six months of the duty, and
**came back** if it was then at or above the pre-case level for three months running by month 18.
A pair **stopped trading** if it fell, never came back, and had no imports at all in months 13 to
18. A month in which none of the panel's countries trades the product has no share and is left out,
and a pair with no such share in months 0 to 6 is not classified. Each pair lands in exactly one category, each case counts once however many products it names, and only pairs with a
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
that have visibly fallen and are not yet back). Models see only trade data Census had released by then (by its actual release dates, usually about
five weeks after the month), notices published by that date, the products named by the first preliminary, and
comparison panels that leave out only rivals whose own case was published by then (exact dates):
regularized logistic regression throughout, plus
shallow gradient boosting and a penalized Cox model at the later points. A monthly version
re-scores every fallen, not-yet-back product at each month 3 to 14 from what is published by then;
the eligible products change from month to month, so months are not compared on the same products.
All are validated forward in time, training only on earlier cases whose outcomes were already
published. Decision value is potential net benefit under assumed costs (decision-curve analysis
[9]): bad outcomes prepared for, less unneeded qualifications weighted by their cost relative to the
avoidable loss. It assumes the country-level outcome stands in for an importer's loss and that
qualifying at the decision date can still avoid it. All 17 thresholds (0.10 to 0.90) and all
baselines are tested together with simultaneous 90 percent bounds, holding fitted models fixed.

## 3. Results

### 3.1 A tariff list names a small slice of its category

A tariff order names a list of eight-digit products, not a category. Across 1,350 pairings of one
tariff list with one chapter (a broad category such as copper), the median list names 5.4 percent of
the chapter's import value, and a third name under 1 percent. Copper shows why it matters (Fig. A1):
total imports rushed in, crashed and recovered, which looks borrowed, but the taxed semi-finished
products fell from 49 to 27 thousand tonnes a month while untaxed cathodes rose from 89 to 154
thousand. Studying whole categories mostly watches trade a tariff never touched.

### 3.2 Where the duty stays, the targeted country loses ground and has not regained it by month 18

Table 1 and Fig. 1 give the aftermath. Pooled over the 381 episodes with a full 18 months, the
targeted country falls 0.19 log points against its rivals after the duty, about 17 percent, with
no movement in the year before: no clear surge to buy ahead, and no early decline. The fall
arrives as a step at the duty, reaching about 0.2 by month 3. The pooled estimate is imprecise once
uncertainty is computed over investigations (90 percent interval about minus 0.37 to minus 0.01),
and the reason is in the split. For cases that became permanent orders, the fall is 0.37 log points,
about 31 percent, deepening to 0.46 in months 13 to 18, and the chance the product is traded at all
falls 9 points. For cases the ITC voted down, there is no sustained fall: the targeted country ends
slightly above its pre-case level.

The comparison between the two final outcomes is descriptive: the ITC's vote rests on the import
record itself, and the no-injury group is small and dominated by the 2024 aluminum extrusions cases.
Shared price movements, including inflation, cancel in the design. On the 2,486 pairs reported in
one unit, months with trade show quantity falling 0.31 log points and value 0.30 (both 95 percent
intervals include zero); with no-trade months kept as zeros, quantity falls 0.54 (SE 0.17) and value 0.19
(SE 0.12). Either way volume fell at least as much as value.

**Table 1.** Targeted country against rivals in the same product, relative to months 18 to 13 before;
log points, standard errors over investigation groups.

| cases | episodes (groups) | months 0-18 | months 13-18 | 12-7 before |
| --- | --- | --- | --- | --- |
| all, full follow-up | 381 (147) | **-0.19** (0.11) | -0.22 (0.13) | +0.02 (0.04) |
| became an order | 326 (125) | **-0.37** (0.06) | -0.46 (0.08) | +0.08 (0.06) |
| ITC found no injury | 45 (18) | +0.06 (0.03) | +0.09 (0.02) | -0.05 (0.02) |
| fake date | 283 (107) | +0.06 (0.03) | +0.08 (0.07) | +0.04 (0.03) |

[[FIG:1|slides/fig/12_order_vs_negative.png|Month by month, the targeted country against rivals selling the same product. Shading is the 95 percent interval for cases that became permanent orders.|48]]

### 3.3 What an importer can expect, and how well history predicts it

Table 2 gives the outcomes for targeted products. Fewer than half are unaffected or come
back: 26 percent never fall and 17 percent fall and recover, while 42 percent fall and stay down and
16 percent fall, never come back and have no imports at all in months 13 to 18 (counting every
product, including a few that came back first, 18 percent have none then). On the fake date, 3
percent fall and stop; on the 277 cases the fake date covers, the real shares are 27, 18, 42 and
13. For the 2020 mattress cases our panel matches published import figures within 3 million dollars,
and the outcomes match the reported shift [10]: Vietnam, Thailand and Cambodia (rates 250 to 990
percent) fell and stayed down or stopped; Indonesia (2.6 percent) did not stay down. Counting from the
month of the fall, 25 percent of products that fall are back within 18 months of falling, against
58 percent on the fake date.

**Table 2.** Outcome within 18 months of a preliminary duty; 90 percent intervals as in Table 3.

| outcome | real (380) | fake date | order | no injury |
| --- | --- | --- | --- | --- |
| did not fall | 26% [22, 30] | 50% [45, 55] | 24% | 35% |
| fell, came back | 17% [15, 19] | 29% [26, 33] | 16% | 26% |
| fell, still down | 42% [38, 46] | 18% [15, 21] | 42% | 36% |
| fell, no imports 13-18 | 16% [11, 20] | 3% [2, 4] | 18% | 3% |

Built only from earlier cases, these rates beat a uniform guess in five of six test years.

On the day the duty starts, case facts add little over the historical rate (Table 3); the gain's
interval includes zero.
Among products whose fall is visible and that are not yet back, monthly forecasts do better (Fig.
2). At month 4, gradient boosting ranks a product that came back above one that did not in 79
percent of pairs (logistic, 75), 0.040 (0.028 to 0.054) better than that month's historical rate;
at month 5, 80 percent. Boosting was ahead of the tested latest-share model in every month from 3
to 12, by 0.004 to 0.015 (pointwise intervals above zero in months 4 to 6 and 10 to 12), but no
month clears a test of all months together. At the ITC vote
a logistic model reaches 80 percent, 0.012 (0.003 to 0.021) beyond the share model; the vote itself
adds 0.004 (-0.002 to 0.011). Decision value is narrower (Fig. A2): with logistic as the common model
(a consistency choice, not preregistered), tested against every baseline at all thresholds
together, the vote-time forecast leads always or never qualifying, the historical rate and the rate
by vote at cost ratios 0.45 and 0.55 to 0.80, but at no ratio does it also lead the share model (pointwise,
it leads the share model from 0.70 to 0.90); at the fall it leads every baseline at 0.70; on day
one, at none. Recalibrating on earlier years made the vote-time forecasts worse on held-out years (Brier 0.155 against 0.146) and the fall-time ones slightly better (0.204 against 0.207); we report the raw model at both, a choice made after seeing those years. Table
A1 turns the models into a lookup.

[[FIG:2|slides/fig/19_monthly_forecast.png|Pairwise ranking accuracy (AUC), held-out products already fallen and not yet back; eligible products differ by month. Boosting against a latest-share model. 16,781 product-months from 1,712 products, 349 cases, 136 groups; held out 1,157 products, 219 cases.|48]]

**Table 3.** Held-out Brier scores (lower is better), best pre-specified model; cases eligible (scored); intervals over groups.

| decision point | cases (scored) | history | best model | improvement | AUC |
| --- | --- | --- | --- | --- | --- |
| duty starts | 381 (241) | 0.248 | logistic, 0.241 | 0.008 [-0.002, 0.016] | 0.62 |
| month 4 | 315 (198) | 0.192 | boosting, 0.152 | 0.040 [0.028, 0.054] | 0.79 |
| ITC final vote | 329 (207) | 0.174 | logistic, 0.134 | 0.040 [0.028, 0.052] | 0.80 |

### 3.4 The same model on China's Section 301 tariffs

The 2018 Section 301 tariffs taxed China alone, product by product: 6,844 products on Lists 1 to 3,
compared with untaxed rivals in the same product, with windows stopped at January 2020 before
China's COVID shutdown (16-month outcomes, Table A2). China's share of these products' imports fell
from 14.9 to 10.4 percent (fake date: up 6 percent). The at-the-fall model trained on antidumping
cases (logistic) ranks Section 301 products correctly in 66 percent of pairs (a Section 301 model:
73) and beats even Section 301's own recovery rate by 0.017 (0.011 to 0.023); trained on Section 301 it beats later
antidumping cases by 0.011 (0.001 to 0.020), and pooled with them it improves their forecasts
slightly (0.005, 0.001 to 0.010). Products whose China share ran more than a quarter above normal
just before the tariff came back 60 percent of the time, against about 30: that part of the fall
was borrowed. Each list is one date, so these describe products, not a list's effect.

## 4. Discussion

For the importer, the answer to the title is closer to real than borrowed: after an antidumping or
countervailing duty, more than half of targeted products (57 percent) fall without coming back
within 18 months, and 16 percent fall and have no imports a year on, and there is no average surge before collection to pay back.
Where the ITC lifts the duty, the aftermath looks like the fake date. The public record suggests
the decision is staged: some importers start qualifying at or before the preliminary, and
finishing can take months, so a forecast that sharpens by month 4 or 5 could inform the later step
of committing volume. These are odds for a supplier country, not for one importer's own supplier,
and their value depends on assumed costs we did not measure.

Unit, comparison and decision point all matter: a category is the wrong unit, and comparing a
country with its rivals in the same product and month removes the year effects that sank level
forecasts. Against the questions: Q2 is answered for these duties, a persistent relative decline;
Q3 by the recovery rates and a monthly forecast that sharpens them for products already falling; Q1
for these duties (no clear surge) and in part for Section 301, where a rush predicts recovery, but
not for the broad 2018 to 2026 actions (appendix). Where the lost trade goes is not estimable.

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

[6] U.S. International Trade Commission (2024). *Aluminum Extrusions from China, Colombia, ... and
Vietnam* (Final). Publication 5560, pp. II-32 to II-33.

[7] U.S. International Trade Commission (2024). *Tin Mill Products from Canada, China, Germany, and
South Korea* (Final). Publication 5492, p. II-47; and *Steel Nails from India, Oman, Sri Lanka,
and Turkey* (Final), Publication 5370 (2022), p. II-22.

[8] Floor & Decor Holdings, Inc. (2020). Annual Report on Form 10-K for fiscal 2019, filed with the
SEC February 20, 2020 (antidumping and countervailing duties on ceramic tile from China).

[9] Vickers, A. and Elkin, E. (2006). Decision curve analysis: a novel method for evaluating
prediction models. *Medical Decision Making* 26(6), 565-574.

[10] Furniture Today (November 23, 2020), "Report: mattress importers moving to Taiwan, Bangladesh
and India"; Home News Now (August 16, 2022), import data on global mattress sourcing.

**Data sources.** United States Census Bureau international trade API; Federal Register API;
United States International Trade Commission Harmonized Tariff Schedule, chapter 99; United States
International Trade Administration antidumping and countervailing duty case index; ITC final
determination notices in the Federal Register.

## 7. Appendix

[[FIG:A2|slides/fig/18_decision_value.png|Potential net benefit per product of acting on the logistic forecast, against the historical rate, always qualifying and (at the vote) the latest-share model, by assumed cost of qualifying as a share of the avoidable loss. Shaded: thresholds where the model leads every baseline at once (simultaneous 90 percent bound above zero; none at the vote, where the share model is never beaten jointly, max-t over all baselines and thresholds, fitted models held fixed).]]

[[FIG:A3|slides/fig/14_outcomes.png|What happened to each targeted product-country pair within 18 months of the duty, real cases against the fake date.]]

[[FIG:A1|slides/fig/09_sankey.png|Copper in 2025, by heading; widths are import value. The taxed and untaxed split follows Proclamation 10962, paragraph 1 against paragraph 8, assigned from product headings, an approximation of the duty's annex.]]

### A lookup for a sourcing team

**Table A1.** Lookup: of 100 held-out products in each cell, the model's expected number back by month 18 / the number that came back (cases in the cell).

| when the fall shows: supplier's pre-case imports | rate up to 25% | rate over 25% | rate not published |
| --- | --- | --- | --- |
| under USD 1M | 36 / 52 (49) | 29 / 30 (38) | 37 / 44 (26) |
| USD 1M to USD 10M | 24 / 35 (50) | 17 / 16 (51) | 27 / 21 (27) |
| over USD 10M | 21 / 24 (78) | 15 / 15 (71) | 20 / 28 (36) |

| at the ITC vote: latest share against pre-case | duty confirmed | duty lifted |
| --- | --- | --- |
| under half | 11 / 13 (143) | 38 / 32 (24) |
| half to 4/5 | 22 / 20 (66) | 52 / 27 (19) |
| 4/5 or more | 46 / 54 (49) | 79 / 81 (17) |

### Section 301 details

**Table A2.** Section 301 Lists 1 to 3 (6,844 listed products, 4,746 with a pre-case share and a measurable fall window) against antidumping cases, 16-month horizon; 90 percent intervals from resampling 2-digit chapters (Section 301) or investigation groups (antidumping), holding fitted models fixed. Transfer tests compare only with rivals whose own case was published by the decision (exact dates); antidumping test cases in C to E are decided from April 2020, after every training label is public.

| outcome | Section 301 | fake date | antidumping |
| --- | --- | --- | --- |
| did not fall | 35% [32, 37] | 42% [38, 45] | 26% [22, 30] |
| fell, came back | 24% [22, 26] | 31% [29, 34] | 16% [14, 19] |
| fell, still down | 36% [33, 38] | 24% [23, 25] | 42% [39, 46] |
| fell, then no imports in months 11 to 16 | 6% [4, 7] | 3% [3, 4] | 15% [11, 20] |

| trained on, scored on | products | AUC | Brier | gain over the target's own rate |
| --- | --- | --- | --- | --- |
| antidumping, all cases, to Section 301 | 3,128 | 0.66 | 0.216 | 0.017 [0.011, 0.023] |
| antidumping published by Sep 2018, to Section 301 | 3,128 | 0.70 | 0.240 | -0.007 [-0.015, 0.001] |
| Section 301, to antidumping from April 2020 | 1,229 | 0.67 | 0.181 | 0.011 [0.001, 0.020] |
| antidumping published by Mar 2020, to antidumping from April 2020 | 1,229 | 0.68 | 0.180 | 0.011 [0.005, 0.016] |
| the same plus Section 301 (pooled) | 1,229 | 0.68 | 0.175 | 0.017 [0.008, 0.024] |
| Section 301 on itself, by chapter (reference) | 3,128 | 0.73 | 0.199 | 0.034 [0.027, 0.041] |

All transfer rows are the logistic model, the common model across tests (boosting in `sec301_transfer_test.csv`). Pooling (E against D, same test products): Brier better by 0.005 [0.001, 0.010].

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
placebo at p < 0.0001. Rebuilt on a fixed set of products with zero months kept, with the 24
non-duty notices removed, companion notices merged and uncertainty computed over investigation
groups, the pooled estimate is minus 0.19 (SE 0.11), and minus 0.37 (SE 0.065) for cases that became
orders. Report 1 counted 8 notices without an affirmative finding; reading every summary gives 4,
plus 20 other non-duty notices. Report 1's "42 percent above its level before the case" came from
pooling every month outside any case window into the reference, not from a surge before the case.
Where Commerce finds critical circumstances, duties can reach back 90 days. An earlier descriptive
comparison found more buying ahead in those cases, not less (+0.067 against -0.066, Welch p = 0.012,
on the older 508-episode sample); it does not show that retroactive liability changes behavior.

### Limitations

The no-injury group is small (45 episodes in 18 groups) and dominated by one 2024 case, so the
contrast between final outcomes is descriptive. Duty rates are missing for 27 percent of notices,
and the model carries a missing-rate indicator. Copper, the running example, is one product with no
comparison country, so it illustrates rather than tests. The importer use case is plausible and
grounded in the duty timeline, but not validated with importers. For Section 301, the product
lists come from the 2026 tariff schedule, so about a tenth of lines renumbered since 2018 are
missing; roughly 2,000 product exclusions, some retroactive, are not removed, so some taxed
products were not taxed; Chinese goods shipped through third countries can inflate rivals' shares;
and each list is one date, so the intervals cover products, not the list's common shock.

Trade data are Census's current revised values, not the figures first published, so "data
available at the decision" means the months released by then, at today's values. Simultaneous
bounds for decision value control error within each decision point, not across the three.

All code is in the repository. The panel: `harvest_hs10.py`, `build_panel_hs8.py`. Duty notices:
`events/harvest_adcvd.py`, `events/parse_adcvd.py`, `events/parse_margins.py`. Final outcomes:
`events/itc_check.py`, `events/itc_audit.py`. Section 3.2: `adcvd_stacked.py`, `itc_compare.py`,
`adcvd_stacked_qty.py`, `adcvd_analysis.py`. Section 3.3: `recovery_benchmark.py`,
`recovery_by_final_stage.py`, `events/build_release_calendar.py`, `build_decision_stacks.py`, `prediction_test.py`, `prediction_stage2.py`,
`prediction_landmark.py`, `decision_value.py`, `calibrated_lookup.py`.
Section 3.4: `events/build_301_lists.py`, `sec301_benchmark.py`, `sec301_transfer_test.py`,
`recovery_lib.py`. Section 3.1: `coverage_share.py`,
`copper_split.py`. Figures: `slides/fig_sankey.py`, `slides/fig_stacked.py`. Each script writes
the CSV its numbers come from.
