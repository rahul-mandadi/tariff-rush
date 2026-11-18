# Borrowed or Real: What Happens to a Supplier Country After a U.S. Trade Duty

**Authors.** Rahul Reddy Mandadi, Raunaksingh Khalsa

**Sponsor.** No external sponsor. Stakeholder: an analyst at a U.S. importer who monitors several
product markets hit by trade duties and decides which declines to investigate first.

**Github.** https://github.com/rahul-mandadi/tariff-rush

## Abstract

When a country loses U.S. market share after a trade duty, how early can public data tell whether it will recover? We matched U.S. import records to 687 duty notices and compared the targeted country with other countries selling the same product. On the day the duty began, case details added nothing we could distinguish from what historical recovery rates already told us. Four months later, we could see which products had lost ground and ask a more specific question: which of those declines would last? We counted a relationship as recovered when its share regained its pre-duty level for three consecutive months by month 18.

We tested the forecast on 936 product–country relationships in later years using only information available at the time. Across 44 monthly lists, an analyst with time to review a fifth of each list had about 187 review slots. Filling them in the forecast's order found about 22 more relationships that had not recovered by month 18 than filling them with the largest visible drops: 82.3 percent of reviewed relationships had not recovered, against 70.3 percent (difference 12.0 points, 90 percent interval 3.9 to 15.7). The forecast's reviews reached 26.4 percent of all relationships that had not recovered by month 18.

## 1. Introduction

Once a supplier country loses U.S. market share after a trade duty, how early can public data tell whether it will recover? This report answers that question for duties that name one product from one country. The project began with copper: when a copper tariff was announced in July 2025, imports had already been climbing for months, and we wanted to know whether buyers were borrowing shipments from later months, the idea behind our title, *Borrowed or Real*. Anyone outside the importing companies had to wait to find out, because Census publishes each month's trade about five weeks after the month ends (Appendix A shows copper).

Fig. 1 shows the question for one relationship: epoxy resins from Taiwan (product 3907.30.00), which came under a new duty in September 2024. In January 2025, Census had published trade through November. Taiwan's share of the product's U.S. imports from the countries compared had fallen to 4.4 percent, against 10.3 percent before the case. That is 42 percent of its earlier share, not 42 percent of U.S. imports. That month, 36 product–country relationships hit by duties had visibly fallen and not yet recovered. Ordered by the latest share, lowest first, Taiwan came 20th; ordered by our model, it came 2nd. An analyst with time to review a fifth of the list, about seven relationships, would have reached Taiwan only in the model's order. What happened next was not known then: by month 18 (March 2026), Taiwan's share was 26 percent of its earlier level, and it had not recovered.

The example shows only that the two orderings send an analyst to different relationships; one case cannot show which order is better. Across all 44 monthly lists from 2020 to 2025, an analyst reviewing a fifth of each list had about 187 review slots. In the model's order, 82.3 percent of them went to relationships that had not recovered by month 18, against 70.3 percent in the latest-share order: about 22 more lasting declines found with the same slots (section 3.4).

We started with three questions. Could we see a rush coming, and how big would it be? What happened to trade once the duty started? How long did the change last? Even the first question was harder than it looked, because tariff lists name narrow products: across the lists we examined, the median list covered just 5.4 percent of the import value in its broader product category, and earlier studies find that grouping products together can hide changes visible in the individual goods [1–4].

[[FIG:1|slides/fig/26_taiwan_example.png|Taiwan epoxy resins (3907.30.00), as an analyst could see it in January 2025. Left: Taiwan's share of the product's U.S. imports from the 43 countries compared, as a percent of its average share 18 to 13 months before the duty (3-month averages); solid, published by January 2025; dashed, published later. Right: the same January 2025 list of 36 relationships ordered by the latest share and by the model; the shaded band is what a review of 20 percent of the list covers.|92]]

Buying ahead of an announced tariff has been documented elsewhere [5]. Could we recognize it with the information available at the time? Late in the project we went back to that first question with three Trump tariff proposals on Chinese goods in 2018. We used the product lists buyers saw on announcement day and only the trade months Census had published by then. A simple rule flagged products whose imports were already growing quickly. It picked out later jumps about as well in 2017, a year before any proposal, as it did in 2018. So published data could flag growing imports, but it could not separate a rush from ordinary momentum or say how much trade buyers pulled forward (draft Appendix J). That is why the rest of this report studies what happens after the duty starts.

The second question gave us a more direct comparison. Take mattresses from Vietnam. When the United States imposes a duty on Vietnamese mattresses, other countries still sell mattresses to U.S. buyers. We can follow Vietnam's share of those purchases month by month. If that share falls, does it return to its earlier level within 18 months? We studied duties that name particular products and countries: antidumping duties address goods sold below fair value, and countervailing duties address government subsidies. Importers begin paying deposits after an affirmative preliminary decision. The U.S. International Trade Commission (ITC) later decides whether the imports injure U.S. producers.

Consider an analyst at a U.S. importer who monitors several product markets hit by duties. The analyst knows whether the company's own mattress orders are arriving. What those orders cannot show is whether buyers across the U.S. are continuing to source mattresses from Vietnam. That distinction matters. Floor & Decor, for example, had already begun moving its Chinese tile sourcing when preliminary duties came in [6]. In other industries, purchasers told the ITC that qualifying a supplier could take anywhere from days to 18 months [7, 8]. Buyers face different timelines. The narrower question an analyst might bring to our data is: of the declines I am seeing across the products we buy, which deserve a closer look?

We therefore tested what that analyst could have learned as the case unfolded. On the day the duty began, the case details added nothing we could distinguish from what had happened in earlier cases. Four months later, Census had usually published about two months of trade after the duty, and some declines were visible. Month 4 is a checkpoint we studied, not a deadline buyers work to (section 2.4).

## 2. Data and methods

### 2.1 Data

We linked Federal Register duty notices to monthly U.S. Census import records from January 2015 through August 2026. Each of the 15.9 million trade records describes one product imported from one country in one month (Table 1). It gives the customs value in dollars and the quantity in the unit Census uses for that product. We grouped the ten-digit Census codes into the eight-digit codes used in the duty notices. The resulting records cover 12,253 products and 234 trading partners. Their monthly totals match the published figures.

**Table 1.** Five Census records: the largest by value for two copper products in March 2025. Each row is one product from one country in one month.

| product | country | month | value, USD | quantity, kg |
| --- | --- | --- | --- | --- |
| 7403.11.00 (refined copper cathodes) | Chile | March 2025 | 715,897,592 | 73,977,447 |
| 7403.11.00 | Canada | March 2025 | 118,144,886 | 11,854,813 |
| 7403.11.00 | Germany | March 2025 | 93,060,459 | 10,000,049 |
| 7403.11.00 | Dem. Rep. of the Congo | March 2025 | 82,079,537 | 8,723,661 |
| 7408.11.60 (refined copper wire) | Canada | March 2025 | 78,104,444 | 7,467,535 |

Duty decisions come from the Federal Register. We harvested every antidumping and countervailing
notice and kept preliminary determinations, the notices that start collection. We then read each
one's own summary and removed 31 that do not start a new duty: 4 negative findings, 16 side notices
about retroactive duties (critical circumstances) issued separately from the case's preliminary, 8
reviews of orders that already existed, and 3 circumvention findings on existing orders. Side
notices never date an episode; they are kept as dated facts about the case and enter a forecast
only once published. The 697 notice-country decisions that remain (687 notices) collapse to 502
episodes, one targeted country in one investigation, with companion antidumping and countervailing
notices merged; they fall into 204
investigation groups, because one petition often names several countries. Each case's final outcome
comes from the order notices in our harvest and, where none links, from the ITC's own determination
notice for that country. Preliminary duty rates are read from each notice's rate table (the "all
others" or country-wide rate) for 507 of the 687 notices.

Of the 935 product codes named in the retained notices, 919 appeared in the Census records. Of the 502 cases, 457 had enough earlier trade data and a rival selling the same product to support a comparison. For 381 of those cases, we could also observe the full 18 months after the duty began. These 381 cases form the main comparison. Fig. 2 traces each step.

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
duty, which precedes the investigation's opening for 501 of 502 episodes.

Every estimate is repeated with the cases moved 24 months earlier, when nothing happened: the fake
date (283 of the 381 episodes have the 42 months of data it needs). It is a falsification check: a
pattern that also appears on the fake date is not specific to the duty. Passing it does not rule
out selection (which suppliers face a petition) or other changes at the same time, so the results
describe what followed these duties; they do not isolate the duty's effect.

[[FIG:2|slides/fig/25_matching_funnel.png|From 10,730 Federal Register notices to the 381 cases in the main comparison. Each step gives what was dropped and why; 919 of the 935 product codes the kept notices name appear in the Census records.|94]]

### 2.3 Recovery and evaluation

We followed the targeted country’s share of U.S. imports of each product among the countries in the comparison. We averaged the share over three months to smooth out short swings. We recorded a **fall** if that share dropped below 80 percent of its pre-case level in months 0 through 6, counting the month the duty began as month 0. We recorded a **recovery** if the share then reached its pre-case level and stayed at or above it for three consecutive months by month 18.
A pair **stopped trading** if it fell, never came back, and had no imports at all in months 13 to
18. A month in which none of the panel's countries trades the product has no share and is left out,
and a pair with no such share in months 0 to 6 is not classified. Each pair lands in exactly one category, each case counts once however many products it names, and only pairs with a
full 18 months enter the shares. Time to recovery is estimated by Kaplan-Meier, which also uses
cases still running, with the clock starting at the month of the fall. Intervals are 90 percent
ranges from resampling whole investigation groups.

The historical rates are themselves a forecast: what an analyst would assume about a new case. We
test them on later cases, building them only from earlier cases whose month 18 had been published, and
score them with the Brier score (mean squared error of a probability; lower is better; a uniform
guess over four outcomes scores 0.75). We then test models against them at three points an analyst
could check: the day the duty starts (target: fell and did not come back), the month a fall first
shows in published data, and the ITC's final vote (target at both: back by month 18, among products
that have visibly fallen and are not yet back). Models see only trade data Census had released by then (by its actual release dates), notices
published by that date, the products named by the first preliminary, and
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

### 2.4 A review list for a market analyst

At the end of month 4, what could the analyst have seen? We used the trade figures Census had published by that date. Month 4 is a studied checkpoint, not a business deadline. By then Census has usually published trade through month 2 (the month the duty began and two more). We chose it with the held-out results in view: the monthly model's accuracy rises from an AUC of 0.730 at month 3 to 0.795 at month 4 and stays between 0.787 and 0.806 through month 8. Months 6 and 8 are reported as checks. A product entered the review list if those figures already showed a fall and had yet to show a recovery. We chose the review rules before examining the review-list results (`forecast/review_queue.py`). Each calendar month is its own
list, so a relationship is ranked only against others at their month-4 checkpoint in the same
month, never against later cases. The predictions are the held-out ones above. Three orderings are compared: the forecast (boosting, the month-4 model
of Table 4), the latest published share relative to its pre-case level (lowest first), and the
historical rate, which is one number for every relationship in a month and so amounts to a random
order. The analyst reviews an assumed 20 percent of each month's list (10 and 30 percent as
checks); these are assumptions, not documented budgets. Tied scores share the remaining reviews
equally. Each relationship counts once, as the unit reviewed; a version weighting each case once is
a check. We report the share of reviewed relationships that had not recovered by month 18 and the share
of all relationships that had not recovered by month 18 that were reviewed, with 90 percent intervals as above. The forecast was to replace the latest share as the ordering only if it beat
it at 20 percent with an interval above zero.

## 3. Results

### 3.1 A tariff list names a small slice of its category

A tariff order names a list of eight-digit products, not a category. Across 1,350 pairings of one
tariff list with one chapter (the first two digits of the product code, a broad category such as
copper), the median list names 5.4 percent of
the chapter's import value, and a third name under 1 percent. Copper shows why it matters (Fig. A1, Appendix A):
total imports rushed in, crashed and recovered, which looks borrowed, but the taxed semi-finished
products fell from 49 to 27 thousand tonnes a month while untaxed cathodes rose from 89 to 154
thousand. Studying whole categories mostly watches trade a tariff never touched.

### 3.2 Where the duty stays, the targeted country loses ground and has not regained it by month 18

Table 2 and Fig. 3 give the aftermath. Pooled over the 381 episodes with a full 18 months, the
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

**Table 2.** Targeted country against rivals in the same product, relative to months 18 to 13 before;
log points, standard errors over investigation groups.

| cases | episodes (groups) | months 0-18 | months 13-18 | 12-7 before |
| --- | --- | --- | --- | --- |
| all, full follow-up | 381 (147) | **-0.19** (0.11) | -0.22 (0.13) | +0.02 (0.04) |
| became an order | 326 (125) | **-0.37** (0.06) | -0.46 (0.08) | +0.07 (0.06) |
| ITC found no injury | 45 (18) | +0.06 (0.03) | +0.09 (0.02) | -0.05 (0.02) |
| fake date | 283 (107) | +0.06 (0.03) | +0.08 (0.07) | +0.04 (0.03) |

[[FIG:3|slides/fig/12_order_vs_negative.png|Month by month, the targeted country against rivals selling the same product. Shading is the 95 percent interval for cases that became permanent orders.|76]]

### 3.3 What follows a duty, and how well history predicts it

Table 3 gives the outcomes for targeted products. Fewer than half are unaffected or come
back: 26 percent never fall and 17 percent fall and recover, while 42 percent fall and stay down and
16 percent fall, never come back and have no imports at all in months 13 to 18 (counting every
product, including a few that came back first, 18 percent have none then). On the fake date, 3
percent fall and stop; on the 277 cases the fake date covers, the real shares are 27, 18, 42 and
13. For the 2020 mattress cases our panel matches published import figures within 3 million dollars,
and the outcomes match the reported shift [10]: Vietnam, Thailand and Cambodia (rates 250 to 990
percent) fell and stayed down or stopped; Indonesia (2.6 percent) did not stay down. Counting from the
month of the fall, 25 percent of products that fall are back within 18 months of falling, against
58 percent on the fake date.

**Table 3.** Outcome within 18 months of a preliminary duty; 90 percent intervals as in Table 4.

| outcome | real (380) | fake date | order | no injury |
| --- | --- | --- | --- | --- |
| did not fall | 26% [22, 30] | 50% [45, 54] | 24% | 35% |
| fell, came back | 17% [15, 19] | 29% [26, 33] | 16% | 26% |
| fell, still down | 42% [38, 46] | 17% [15, 20] | 42% | 36% |
| fell, no imports 13-18 | 16% [11, 20] | 3% [2, 4] | 18% | 3% |

Built only from earlier cases, these rates beat a uniform guess in five of six test years.

On the day the duty starts, case facts add nothing we can distinguish from the historical rate
(Table 4): a gain of 0.007 whose 90 percent interval includes zero (-0.001 to 0.013). Before any
trade after the duty is published, the model has only the case's facts (duty rate, one duty or
both, China or not, retroactive duties) and the market before the case (the country's share and
its trend, its size, how concentrated the market is), and these say little beyond how past cases
went.
Among products whose fall is visible and that are not yet back, monthly forecasts do better (Fig.
4). At month 4, gradient boosting ranks a product that came back above one that did not in 79.5
percent of pairs (AUC 0.795; logistic, 0.753), 0.039 (0.026 to 0.052) better than that month's historical rate;
at month 5, 0.797. Much of that improvement comes from the latest published share alone:
a model of the latest share reaches a Brier score of 0.165 against 0.192 for the historical rate and
0.154 for boosting, about 70 percent of the gain. Boosting was ahead of that latest-share model in
every month from 3 to 12, by 0.003 to 0.013 (pointwise intervals above zero in months 4 to 6 and
11), but no month clears a test of all months together. At the ITC vote a logistic model reaches
80 percent, 0.012 (0.003 to 0.021) beyond the share model, which again supplies about 70 percent of
the gain over history; the vote itself adds 0.004 (-0.002 to 0.011). These are gains in probability
accuracy. Decision value is a separate question (Fig. B1, Appendix B): with logistic as the common model (a
consistency choice, not preregistered), the vote-time forecast leads always or never qualifying, the historical rate and the rate by vote
at cost ratios 0.45, 0.50 and 0.60 to 0.80, but additional decision value over the latest-share model was
not established under the simultaneous test at any ratio (pointwise, it leads the share model at
0.70, 0.75, 0.85 and 0.90); at the fall and on day one, at none.
Recalibrating on earlier years made the vote-time forecasts worse on held-out years (Brier 0.155
against 0.145) and the fall-time ones slightly better (0.204 against 0.205); we report the raw model
at both, a choice made after seeing those years. Table C1 (Appendix C) turns the models into a lookup.

[[FIG:4|slides/fig/19_monthly_forecast.png|Pairwise ranking accuracy (AUC), held-out products already fallen and not yet back; eligible products differ by month. Boosting against a latest-share model. 16,781 product-months from 1,712 products, 349 cases, 136 groups; held out 1,157 products, 219 cases.|82]]

**Table 4.** Held-out Brier scores (lower is better), best pre-specified model; cases eligible (scored); intervals over groups.

| decision point | cases (scored) | history | best model | improvement | AUC |
| --- | --- | --- | --- | --- | --- |
| duty starts | 381 (241) | 0.248 | logistic, 0.242 | 0.007 [-0.001, 0.013] | 0.633 |
| month 4 | 315 (198) | 0.192 | boosting, 0.154 | 0.039 [0.026, 0.052] | 0.795 |
| ITC final vote | 329 (207) | 0.174 | logistic, 0.134 | 0.039 [0.027, 0.052] | 0.796 |

### 3.4 Which relationships to review first

The month-4 lists hold 936 held-out relationships (198 cases, 66 investigation groups, 44 monthly
lists, 2020 to 2025); 62 percent of them had not recovered by month 18. Reviewing 20 percent of
each month's list gives about 187 review slots in all. Filled in the forecast's order, 82.3 percent
of the slots went to relationships that had not recovered by month 18, against 70.3 percent in the
latest-share order and 62 percent in a random order (Table 5): 12.0 points more than the latest
share (90 percent interval 3.9 to 15.7). With the same slots, that is about 154 such relationships
against 132, some 22 more. The forecast's reviews reached 26.4 percent of all relationships that had
not recovered by month 18, where the most any order could reach at that capacity is 32.1 percent
(Table 5). The result holds at 10 and 30 percent,
weighting each case once (90 against 81 percent), without the largest investigation group (2024
aluminum extrusions, 14 countries and nearly half the relationships; 89 against 77 percent, a check
added after the first results), and at the month-6 and month-8 checkpoints (88.2 against 75.7
percent and 89.2 against 81.1; differences 12.5 points [7.1, 17.3] and 8.1 [4.6, 12.5]). The
forecast is therefore the ranking (Table D1, Appendix D, shows one month's list).

**Table 5.** Month-4 review lists, held out 2020 to 2025: share of reviewed relationships that had
not recovered by month 18 (share of all such relationships reviewed); last column, forecast minus
latest share in points, with a 90 percent interval.

| review capacity | forecast | latest share | historical rate (random) | forecast minus latest share |
| --- | --- | --- | --- | --- |
| 10% | 85% (14%) | 69% (11%) | 62% (10%) | +16.0 [7.6, 20.4] |
| 20% | 82% (26%) | 70% (23%) | 62% (20%) | +12.0 [3.9, 15.7] |
| 30% | 81% (39%) | 71% (34%) | 62% (30%) | +10.3 [3.4, 12.8] |

### 3.5 The same model on China's Section 301 tariffs

Section 301 of the Trade Act of 1974 lets the U.S. Trade Representative tax imports from a country
whose trade practices it finds unfair. The 2018 Section 301 tariffs taxed China alone, product by
product: 6,844 products on Lists 1 to 3,
compared with untaxed rivals in the same product, with windows stopped at January 2020 before
China's COVID shutdown (16-month outcomes, Table E1, Appendix E). China's share of these products' imports fell
from 14.9 to 10.4 percent (fake date: up 6 percent). The at-the-fall model trained on antidumping
cases (logistic) ranks Section 301 products correctly in 67 percent of pairs (Table E2; a Section 301 model:
73) and beats even Section 301's own recovery rate by 0.017 (0.011 to 0.023); trained on Section 301 it beats later
antidumping cases by 0.011 (0.001 to 0.020), and pooled with them it improves their forecasts
slightly (0.005, 0.001 to 0.010). Among the 3,128 products scored once their fall showed, those whose
China share in the six months before the tariff ran more than a quarter above its earlier level
came back 60 percent of the time, against about 30 for the rest. That is an observed association,
not a measured payback: a temporary spike can reverse on its own, these products were smaller
before the case, so their shares swing more, and the split has no fake-date check. Each list is one date, so these describe products, not a
list's effect.

## 4. Discussion

For an analyst watching these markets, the answer to the title is closer to real than borrowed: after an
antidumping or countervailing duty, more than half of targeted products (57 percent) fall without
coming back within 18 months, 16 percent fall and have no imports a year on, and there is no average
surge before collection to pay back. Where the ITC lifts the duty, the aftermath looks like the fake
date. What we demonstrated is a better order for reviewing declines at month 4 (section 3.4). In probability accuracy the latest share does
most of the work, and under assumed costs at the vote the forecast's added decision value over it
was not established; the gain we can show is in ordering, at assumed review capacities. These are
odds for a supplier country in a product, not for one importer's supplier, and whether to act on a
reviewed relationship also depends on the importer's exposure, its alternatives, how long
qualification takes and what it costs. We did not test whether the list changes an importer's
orders or costs; that would need a study with users.

Unit, comparison and decision point all matter: a category is the wrong unit, and comparing a
country with its rivals in the same product and month removes the year effects that sank level
forecasts. Against our three questions: what happens after the duty starts is answered for these duties, a
persistent relative decline; how long it lasts, by the recovery rates, which are the benchmark, and
a monthly forecast that orders review of products already falling. Whether there is a rush is
answered for these duties (no clear surge before collection) and in part for Section 301, where
products with a rush before the tariff more often came back (an association: a spike can reverse
on its own). For the 2018 Section 301 proposals, published data flagged growing imports
but did not separate a rush from ordinary momentum (draft Appendix J); Report 1's analysis of the
broader 2018 to 2026 actions is withdrawn (Appendix F). Where the lost trade goes is not estimable. Limitations are listed in Appendix I.

## 5. Statement of contributions

Both authors contributed equally. Rahul Reddy Mandadi led data collection, the eight-digit panel,
the duty-notice tables, the stacked event study, the recovery and forecasting tests, the Section 301
test and the code repository. Raunaksingh Khalsa led exploratory analysis, anomaly detection (the
dollars and quantity comparison in Appendix G) and the first presentation. Both set the research
questions, chose the identification strategy, and wrote this report.

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

[6] Floor & Decor Holdings, Inc. (2020). Annual Report on Form 10-K for fiscal 2019, filed with the
SEC February 20, 2020 (antidumping and countervailing duties on ceramic tile from China).

[7] U.S. International Trade Commission (2024). *Aluminum Extrusions from China, Colombia, ... and
Vietnam* (Final). Publication 5560, pp. II-32 to II-33.

[8] U.S. International Trade Commission (2024). *Tin Mill Products from Canada, China, Germany, and
South Korea* (Final). Publication 5492, p. II-47; and *Steel Nails from India, Oman, Sri Lanka,
and Turkey* (Final), Publication 5370 (2022), p. II-22.

[9] Vickers, A. and Elkin, E. (2006). Decision curve analysis: a novel method for evaluating
prediction models. *Medical Decision Making* 26(6), 565-574.

[10] Furniture Today (November 23, 2020), "Report: mattress importers moving to Taiwan, Bangladesh
and India"; Home News Now (August 16, 2022), import data on global mattress sourcing.

**Data sources.** United States Census Bureau international trade API; Federal Register API;
United States International Trade Commission Harmonized Tariff Schedule, chapter 99; United States
International Trade Administration antidumping and countervailing duty case index; ITC final
determination notices in the Federal Register.

## 7. Appendices

### Appendix A. Copper in 2025

[[FIG:A1|slides/fig/09_sankey.png|Copper in 2025, by heading; widths are import value. The taxed and untaxed split follows Proclamation 10962, paragraph 1 against paragraph 8, assigned from product headings, an approximation of the duty's annex.|80]]

### Appendix B. Decision value under assumed costs

[[FIG:B1|slides/fig/18_decision_value.png|Potential net benefit per product of acting on the logistic forecast, against the historical rate, always qualifying and (at the vote) the latest-share model, by assumed cost of qualifying as a share of the avoidable loss. At no threshold and no decision point is the model ahead of every baseline at once (simultaneous 90 percent bound, section 2.3).|100]]

### Appendix C. A lookup for an analyst

**Table C1.** Lookup: of 100 held-out products in each cell, the model's expected number back by month 18 / the number that came back (cases in the cell).

| when the fall shows: supplier's pre-case imports | rate up to 25% | rate over 25% | rate not published |
| --- | --- | --- | --- |
| under USD 1M | 35 / 52 (49) | 30 / 30 (38) | 35 / 44 (26) |
| USD 1M to USD 10M | 24 / 35 (50) | 16 / 16 (51) | 26 / 21 (27) |
| over USD 10M | 21 / 24 (78) | 15 / 15 (71) | 19 / 28 (36) |

| at the ITC vote: latest share against pre-case | duty confirmed | duty lifted |
| --- | --- | --- |
| under half | 12 / 13 (143) | 38 / 32 (24) |
| half to 4/5 | 22 / 20 (66) | 52 / 27 (19) |
| 4/5 or more | 46 / 54 (49) | 78 / 81 (17) |

### Appendix D. A review list, one month

**Table D1.** The month-4 list for January 2025 (36 relationships from ten cases in five investigation
groups, all held out), first nine rows,
ranked by the forecast; at 20 percent capacity the analyst reviews the first 7.2. Columns are what
the analyst sees on the decision date, plus the outcome, known only later. Of the reviewed
relationships, 83 percent had not recovered by month 18, against 80 percent in the latest-share
order and 56 percent in a random order; the historical rate (79 percent not recovered, from earlier
years) is the same for every row and overstated this month's 56 percent. One month is an
illustration, not evidence.

| rank | product | HS code | country | chance not recovered by month 18 | latest share / pre-case | historical rate not recovered | had not recovered by month 18 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ferrosilicon | 7202.21.10 | Brazil | 0.93 | 0.00 | 0.79 | yes |
| 2 | Epoxy resins | 3907.30.00 | Taiwan | 0.92 | 0.42 | 0.79 | yes |
| 3 | Ferrosilicon | 7202.21.50 | Kazakhstan | 0.91 | 0.43 | 0.79 | yes |
| 4 | Epoxy resins | 2910.90.91 | India | 0.90 | 0.58 | 0.79 | yes |
| 5 | 2,4-D acid | 3808.93.15 | India | 0.89 | 0.59 | 0.79 | no |
| 6 | Ferrosilicon | 7202.21.50 | Brazil | 0.89 | 0.48 | 0.79 | yes |
| 7 | Ceramic tile | 6914.10.80 | India | 0.88 | 0.03 | 0.79 | yes |
| 8 | Ceramic tile | 6907.40.90 | India | 0.87 | 0.17 | 0.79 | no |
| 9 | Ceramic tile | 6907.30.40 | India | 0.87 | 0.00 | 0.79 | yes |

### Appendix E. Section 301 details

**Table E1.** Section 301 Lists 1 to 3 (6,844 listed products, 4,746 with a pre-case share and a measurable fall window) against antidumping cases, 16-month horizon; 90 percent intervals from resampling 2-digit chapters (Section 301) or investigation groups (antidumping), holding fitted models fixed. Transfer tests compare only with rivals whose own case was published by the decision (exact dates); antidumping test cases in C to E are decided from April 2020, after every training label is public.

| outcome | Section 301 | fake date | antidumping |
| --- | --- | --- | --- |
| did not fall | 35% [32, 37] | 42% [38, 45] | 26% [22, 30] |
| fell, came back | 24% [22, 26] | 31% [29, 34] | 16% [14, 19] |
| fell, still down | 36% [33, 38] | 24% [23, 25] | 42% [39, 46] |
| fell, then no imports in months 11 to 16 | 6% [4, 7] | 3% [3, 4] | 15% [11, 20] |

**Table E2.** Transfer tests, logistic model, the common model across tests (boosting in `sec301_transfer_test.csv`). Pooling (E against D, same test products): Brier better by 0.005 [0.001, 0.010].

| trained on, scored on | products | AUC | Brier | gain over the target's own rate |
| --- | --- | --- | --- | --- |
| antidumping, all cases, to Section 301 | 3,128 | 0.67 | 0.216 | 0.017 [0.011, 0.023] |
| antidumping published by Sep 2018, to Section 301 | 3,128 | 0.70 | 0.240 | -0.007 [-0.015, 0.001] |
| Section 301, to antidumping from April 2020 | 1,229 | 0.67 | 0.181 | 0.011 [0.001, 0.020] |
| antidumping published by Mar 2020, to antidumping from April 2020 | 1,229 | 0.68 | 0.180 | 0.011 [0.005, 0.016] |
| the same plus Section 301 (pooled) | 1,229 | 0.68 | 0.175 | 0.017 [0.008, 0.024] |
| Section 301 on itself, by chapter (reference) | 3,128 | 0.73 | 0.199 | 0.034 [0.027, 0.041] |


### Appendix F. Report 1's broad-tariff rush analysis (withdrawn)

Report 1 described month-by-month jumps around Section 301 actions, Section 232 actions (tariffs set
on national-security grounds, such as those on steel, aluminum and copper) and IEEPA actions (tariffs
set under the International Emergency Economic Powers Act, such as the 2025 country-wide tariffs). A
document-by-document audit found 13 of the 19 study documents wrong in date, countries, direction
or product list, and the analysis has no fake-date check, so we do not report it. Correcting those
documents is the first step for anyone extending this work.

### Appendix G. Dollars and quantity at the category level

Our unusual-month score measures how far a chapter's largest 2025 month sat above a line drawn
from its own recent trend and seasonal pattern, as a share of its usual range. On dollars,
pharmaceuticals rank first of 63 comparable chapters (2.26); on quantity, 62nd (minus 0.34). Its
March jump is a shift toward Swiss medicines at about 5,185 dollars a kilogram, which lifts dollars
far more than tonnes. Cocoa scores 1.00 on dollars and 0.69 on quantity; its import value per unit
roughly doubled from 2022 to 2025. A category's dollar total alone misleads in both directions.
Deflating the dollar ranking over all 96 product chapters by the BLS import price index keeps 8 of
its top 10 chapters; by the nonfuel index, 9 of 10 (on the 63 chapters with quantity data, 7 and 8).

### Appendix H. Changes from Report 1

Report 1 put the antidumping aftermath at minus 0.30 log points, "about 26 percent", against a
placebo at p < 0.0001. Rebuilt on a fixed set of products with zero months kept, with the 24
non-duty notices removed, companion notices merged and uncertainty computed over investigation
groups, the pooled estimate is minus 0.19 (SE 0.11), and minus 0.37 (SE 0.065) for cases that became
orders. Report 1 counted 8 notices without an affirmative finding; reading every summary gives 4,
plus 20 other non-duty notices. Report 1's "42 percent above its level before the case" came from
pooling every month outside any case window into the reference, not from a surge before the case.

### Appendix I. Limitations

The no-injury group has 45 episodes in 18 groups (section 3.2). Duty rates are missing for 26 percent of notices,
and the model carries a missing-rate indicator. Copper, the running example, is one product with no
comparison country, so it illustrates rather than tests. The analyst's use is plausible and
grounded in the duty timeline, but not tested with users, and we measured no changed orders or
savings. The review capacities are assumptions,
and the lists are small (median 8 relationships, 6 of 44 months with one). For Section 301, the product
lists come from the 2026 tariff schedule, so about a tenth of lines renumbered since 2018 are
missing; roughly 2,000 product exclusions, some retroactive, are not removed, so some taxed
products were not taxed; Chinese goods shipped through third countries can inflate rivals' shares;
and each list is one date, so the intervals cover products, not the list's common shock.

Trade data are Census's current revised values, not the figures first published, so "data
available at the decision" means the months released by then, at today's values. Simultaneous
bounds for decision value control error within each decision point, not across the three.

All code is in the repository. The panel: `data/harvest_hs10.py`, `data/build_panel_hs8.py`. Duty notices:
`events/harvest_adcvd.py`, `events/parse_adcvd.py`, `events/parse_margins.py`. Final outcomes:
`events/itc_check.py`, `events/itc_audit.py`. Section 3.2: `measure/adcvd_stacked.py`, `measure/itc_compare.py`,
`measure/adcvd_stacked_qty.py`, `report1/adcvd_analysis.py`. Section 3.3: `measure/recovery_benchmark.py`,
`measure/recovery_by_final_stage.py`, `events/build_release_calendar.py`, `measure/build_decision_stacks.py`, `forecast/prediction_test.py`, `forecast/prediction_stage2.py`,
`forecast/prediction_landmark.py`, `forecast/decision_value.py`, `forecast/calibrated_lookup.py`, `forecast/review_queue.py` (section 3.4).
Section 3.5: `events/build_301_lists.py`, `section301/sec301_benchmark.py`, `section301/sec301_transfer_test.py`,
`recovery_lib.py`. Appendix G, dollars and quantity: `data/eda_summary.py`, `data/chapter_quantity.py`,
`slides/fig_units.py`, `data/pharma_mix.py`, `data/deflation_check.py`. Section 3.1: `measure/coverage_share.py`,
`data/copper_split.py`. Figures: `slides/fig_sankey.py`, `slides/fig_stacked.py`. Each script writes
the CSV its numbers come from.

### Appendix J (draft). The rush, revisited with the 2018 proposals

*Draft, pending the scope amendment in `docs/SCOPE_AMENDMENT_DRAFT.md`. Code and the recorded run
are in `research/rush_2018/`.*

We replayed the April 3, June 15 and July 10, 2018 Section 301 proposals on Chinese goods. Each
replay used that proposal's own product list (1,333, 284 and 6,031 lines) and only the trade months
Census had published by the proposal date (through January, April and May). For each proposed
product with imports in both comparison periods, we compared its last three published months with
the same months a year earlier and flagged the fastest-growing fifth. A product jumped if a target
month before the duty was more than 25 percent above the same month a year earlier.

The year-earlier comparison comes first, because it decides how to read the rest. One year before
any proposal, the same rule on the same lists picked out jumps about as well:

| target month (proposal) | eligible products, 2018 | flagged minus whole list, 2017 | flagged minus whole list, 2018 | 2018 minus 2017 |
| --- | --- | --- | --- | --- |
| May (April) | 905 | +8.3 | +8.5 | +0.2 |
| June (April) | 933 | +5.9 | +4.9 | -1.0 |
| July (June) | 234 | +23.2 | +27.5 | +4.3 |
| August (July) | 3,707 | +16.2 | +13.3 | -2.9 |

Percentage points of products that jumped. Flagged products jump more often because import growth
persists, not because a tariff was coming. July's 81 percent among flagged products, against 53
percent across the list, rests on 47 flagged products; the same rule gave 62 against 39 percent in
2017.

The only tariff-specific sign is in August. Matched to the closest unproposed Chinese product in
the same four-digit group by earlier size and growth, proposed products jumped 23.2 points more often
(95 percent interval 10.8 to 34.4), against 0.0 (-17.0 to 15.4) a year earlier. Those 125 matches
cover 3.4 percent of the eligible lines, the quantity version includes zero (14.8 points, -2.6 to
28.4), and one matched comparison a year earlier came out clearly negative (July 2017, -26.3, -47.1
to -9.5), so the matching is noisy. Forecasting the size of the jump from recent growth beat a
same-month-last-year forecast in only one of the four 2018 target months.

Published trade can flag products whose imports are growing between a proposal and its duty. It
cannot tell a tariff rush from ordinary momentum, or say how much trade was pulled forward. That
would need more independent policy episodes, broader comparison groups, or shipment data from
inside the reporting gap. Trade values are Census's current revised figures, not those first
published.
