# Borrowed or Real: Measuring Import Surges Around U.S. Tariffs

**Authors.** Rahul Reddy Mandadi, Raunaksingh Khalsa

**Sponsor.** No external sponsor. Stakeholders: importers re-sourcing a supplier, lenders exposed
to a single country of origin, and carriers operating an affected service.

**Github.** https://github.com/rahul-mandadi/tariff-rush

## Abstract

A United States tariff is announced with a start date weeks or months later, giving importers a
window to bring goods in before the duty applies. Imports surge, then fall. What matters to anyone
exposed to the targeted country is what the fall means: whether goods merely arrived early, or
whether the business has moved permanently. That decision is made near the announcement, while
official trade data appears about five weeks after each month closes. We built a panel of United States imports covering 140 months at the
eight-digit product level at which tariff orders are written, matched to 134 tariff actions and
993 antidumping cases. We measure how much of a product category a tariff action
actually names: typically about five percent, and under one percent in a third of cases, which is
enough to drive a category-level estimate toward zero. Separately, we find that when an
antidumping or countervailing duty takes effect the named country loses about a quarter of its
position against the other countries supplying the same product, measured in the dollar value
declared at the border, and does not recover it within the eighteen months we observe.

## 1. Introduction

A tariff is a tax on imported goods, announced in the United States by a proclamation or agency
notice naming a future date on which collection begins. That gap creates an incentive to
accelerate shipments and clear customs beforehand. The resulting pattern, a rise before the start
date and a fall after it, is known as front-loading and is well documented [5].

Observing the surge is not difficult. Knowing what the fall means is. If importers merely moved
purchases forward, volumes recover; the volume was borrowed from later months. If buyers switched
to another country and stayed, the fall is permanent. The two are indistinguishable for months and
imply opposite decisions.

Those decisions are expensive and made early. An importer must choose between absorbing the duty
and qualifying an alternative supplier, which takes months; a lender holds the same uncertainty
as credit risk. Census publishes monthly trade roughly five weeks after the reference month
closes, so by the time two post-tariff months are observable the duty has been in force for a
quarter and the commitments are made.

The domain problem is therefore to characterise, using only information available at announcement,
what follows a tariff for a given product and origin. It decomposes into three questions. **Q1:
does a surge happen, and when?** Detecting one is a classification problem, sizing it a
regression. **Q2: what does the fall after the duty mean?** A three-way choice between volume
borrowed from later months, demand lost outright, and volume relocated to an untargeted country.
**Q3: how long does the aftermath last?** A duration problem in which some episodes are still
running when our data ends, so for those the length can only be bounded below.

Existing work measures tariff responses at fine granularity for good reason. Fajgelbaum et al.
[1] study the 2018 tariffs at ten digits, noting the increases were predominantly set at eight.
The International Trade Commission [2] estimates one elasticity at two, four, six and eight
digits and finds coarser data gives systematically smaller estimates; Imbs and Mejean [3] report
the same outside the tariff setting, and Flaaen and Pierce [4] use a continuous exposure measure
rather than a binary indicator. Our first result quantifies how severe this is for United States
tariff actions.

## 2. Methods

### 2.1 Data

We use two public sources. Monthly import statistics come from the Census Bureau international
trade API, which reports value in dollars and a quantity in each product's native unit. Tariff actions come from the Federal Register API. The product lists behind each
action come from chapter 99 of the Harmonized Tariff Schedule.

Products are classified hierarchically: two digits denote a chapter, a broad category such as
copper or pharmaceuticals, of which 98 appear in our panel; eight digits is where United
States tariff orders name products; ten is the finest level Census publishes. We harvest at ten
and aggregate to eight, because ten nests exactly inside eight, so a tariff matches precisely the
products it names.

### 2.2 Panel construction

The panel covers 140 months from January 2015 to August 2026: 15.9 million observations of one
eight-digit product, one partner country and one month, across 12,253 product lines and 234
partners. We call one such product-country-month a cell. Two processing issues were material, an
all-countries total that doubles every figure if retained and effective dates misread from
recited rate histories; the appendix gives both. After the first, the panel reconciles to a 2017
total of 2.34 trillion dollars against a published 2.34 trillion, and all 140 months pass the
same check.

For modelling we apply inclusion rules fixed in advance: at least 36 months of observed data,
a median monthly value of at least 100,000 dollars, and at least one untreated origin supplying the
same product in the same month. This retains 6.09 million observations carrying 95.7 percent of
total import value, but only 8,100 of the 12,253 product lines and 193 of the 234 partners. The
cells that drop are thin, so the value share overstates how much of the product space survives.

### 2.3 Event construction

We searched 2,792 Federal Register documents and classified 134 as actions imposing or modifying a
duty; the rest are proposed rules, notices, exclusion procedures and trade remedy documents. We separately harvested antidumping and countervailing duty proceedings,
yielding 993 cases across 70 countries and 1,297 named product lines, with case numbers linking
each proceeding's initiation, preliminary, final and order stages. From chapter 99 we resolved
9,083 eight-digit lines named across 162 surcharge codes, giving 1,350 pairings of one surcharge code with one
chapter. We call these actions below, though one Federal Register action may cite several codes.

### 2.4 Identification and evaluation

The outcome throughout is the logarithm of customs value, the dollar amount declared at the
border and not adjusted for inflation; in logs a coefficient reads as a percentage change.
Quantity is not available on a common unit across cells, so it is used for the chapter work in
section 3.2 and not for the event studies. We compare
a product from a targeted country against the same product from untargeted countries in the same
month. A price shock or global demand movement affects every supplier at once and
cancels, whereas a tariff moves one against the rest. The design is available for 89.6 percent of
treated product-months, which have two or more suppliers, median seven.

Estimates we report as results are paired with a placebo: the identical calculation on the same
events shifted 24 months earlier, where no action occurred. An estimate that does not separate
from its own placebo is not reported as a result. Table 1 is the exception and is labelled as
such. This discipline has retired three candidate estimators
over the course of the project, including one of our own earlier conclusions, described in section
3.3.

## 3. Results

### 3.1 How much of a category a tariff action actually names

A tariff order does not name a product category. It names a list of eight-digit lines, usually
published as an annex to a separate notice. How much of a category that list covers is an
empirical question we have not seen answered for United States tariff actions. Across all 1,350
pairings of one surcharge code with one chapter, the median pairing
names 5.4 percent of that chapter's import value, and 32.4 percent of pairings name under one
percent. Collapsing to one figure per surcharge code gives a median of 1.3 percent.

Fig. 1 shows what that looks like for copper, the running example of this project. Chapter 74
comprised 24.7 billion dollars of imports across 89 eight-digit lines in 2025. The Section 232
proclamation of 30 July 2025 imposed a 50 percent duty on semi-finished copper products and
intensive derivatives, 29 percent of the chapter by value. Refined copper and cathodes, 67
percent of the chapter on their own, were treated as input materials and not subject to the duty.

[[FIG:1|slides/fig/09_sankey.png|Copper in 2025, by heading; widths are import value. The taxed/untaxed split follows Proclamation 10962, paragraph 1 against paragraph 8. The annex table is not in the Federal Register text, so headings are assigned by standard meaning.]]

This has a direct consequence for measurement. A category-level treatment flag assigns treatment
to mostly untreated trade, so any genuine response is averaged against a much larger unaffected
remainder. Tested directly, chapter-months touched by an action sit slightly higher than
untouched ones rather than further from normal: medians of negative 7.1 against negative 7.6
percent across 1,815 and 7,977 chapter-months, one-sided p = 0.0075. A gap of 0.6 percentage
points is detectable and economically negligible, which is what heavy dilution predicts. This is the quantified form of the attenuation that [2] and [3] describe in
general terms.

Re-estimating the same tariff actions on the eight-digit panel then shows what the
category-level view could not. Treatment is exact for the two mechanisms that name products,
Section 301 and IEEPA. It is not for Section 232, whose proclamations name a material class, so
that row still assigns treatment by chapter and carries the dilution this section describes. Table 1 reports a first-differenced specification, so each
figure is the month-over-month change in log import value against the same change in the baseline
months; a one-month jump in the level appears as a positive followed by a negative.

**Table 1.** The same tariff actions at eight digits, by legal mechanism, first-differenced. k
counts months from the announcement, so k = 0 is the announcement month, not the duty start.
Asterisks mark significance at 5 percent; event counts are nine, four and eight documents.

| mechanism | k = -2 | k = -1 | k = 0 | k = 1 |
| --- | --- | --- | --- | --- |
| enumerated, Section 301 lists | -16%* | +1% | **+27%*** | -37%* |
| country-wide, IEEPA | **+9%*** | -10%* | -15%* | +8%* |
| material class, Section 232 | +0% | **+13%*** | -3% | -10%* |

The jump arrives at a different month in each mechanism, and the ordering is suggestive: Section
301 lists are published with the action and the jump is in the announcement month; IEEPA measures
were trailed publicly and the jump comes two to three months early; Section 232 follows an
investigation and the jump comes one month early. That is the shape front-loading would take if
the rush began when the duty became knowable.

We do not report it as an answer to Q1, for three reasons. It has no placebo, unlike every other
estimate here. The rows rest on nine, four and eight documents, with standard errors clustered on
cells rather than on events, so the asterisks overstate the evidence. And the largest Section 301
event, a December 2018 notice covering 5,921 lines, postponed its own scheduled increase, which
was then deferred indefinitely; whatever moved around it was not a duty taking effect. The
pattern is worth recording and is not yet identified.

### 3.2 Neither dollars nor quantity is a safe measure at category level

A second measurement problem comes from the same source. Our anomaly detector scores each
chapter by how far its most extreme 2025 month ran from a counterfactual fitted on its own prior
years, scaled by that series' own variability. On dollars it ranked cocoa among the most unusual
categories of 2025, but cocoa prices roughly tripled after poor West African harvests, so a price
movement read as a surge in volume.

Quantity is not a clean substitute. It comes in each product's native unit, and at chapter level
those are mixed: 56 of 98 chapters report kilograms for under seventy percent of their value,
with apparel in dozens and footwear in pairs. Restricting to chapters whose dominant unit carries
eighty percent of value leaves 65, of which 63 are rankable on both measures, and the two
rankings disagree sharply. Pharmaceuticals scores 2.86 on dollars and negative 0.33 on quantity:
its tonnage tracked trend while dollar value rose 57 percent above trend in March, concentrated
in high-value origins, which is a shift in product mix that tonnage cannot see. Copper runs the
other way, 1.77 against 2.68. In dollars cocoa is a false positive; in quantity pharmaceuticals
is a false negative.

Both failures share a cause with section 3.1: a chapter mixes products with different treatment
status and different units. An eight-digit line usually has one of each, though 145,423 cells
carrying 4.6 percent of value still span more than one.

### 3.3 The aftermath of an antidumping or countervailing duty is a durable loss, with no
preceding surge we can detect

When the United States imposes an antidumping or countervailing duty, the named country loses
ground against the other countries supplying the same product. It runs 42 percent above its own
pre-case baseline before collection and 6 percent above it after, a fall of about 26 percent that
has not reversed eighteen months later. This is the one estimate here that clears its placebo by
a wide margin, and it is the opposite of what front-loading predicts: we detect no rush before
the duty starts.

Antidumping and countervailing proceedings give the event sample with adequate power: the cases
are numerous, name products explicitly, and target individual countries. Of the 508 episodes in
Table 2, 338 are antidumping and 169 countervailing. We date each from the publication of the
preliminary determination and treat that as the onset of collection, which is wrong for 8 of
them; the appendix gives the detail. Fig. 2 traces the named country against
other suppliers of the same product across 673 events, from a baseline eighteen to thirteen months
before collection begins. Product-month and product-origin fixed effects hold constant the
product's own monthly swings and each country's usual level in it, so a point is a position
against rival suppliers, not a dollar amount. Cell-months claimed by more than one case are
dropped, 27,255 of the 65,488 falling in any window.

The elevated run through the year before collection starts to decline roughly four months out.
In the model's own units the drop is 0.30 log points. It is not a complete displacement: eight of
the nineteen post-period months are individually significant and all eight remain above
baseline.

[[FIG:2|slides/fig/10_event.png|The named country against other suppliers of the same product, 673 events. Shading is the 95 percent interval on the real path; the placebo repeats the estimation on the same events shifted back 24 months.]]

The same estimation on events shifted back 24 months rises rather than falls over the same event
time. That placebo is a contrast rather than a zero, because shifting back two years puts its
post window inside the real pre-period.

**Table 2.** Episode-level excess imports for the named country, real events against the same
events shifted back 24 months, a log deviation from each cell's own pre-event level.

| measure | real events | placebo at minus 24 months |
| --- | --- | --- |
| episodes | 508 | 473 |
| median excess during the window | +0.031 | +0.037 |
| median excess after | **-0.316** | +0.020 |

The post-period difference separates from its placebo at p < 0.0001 on both a rank test and a
t-test, at horizons of six, nine and twelve months. The during-window difference is no evidence
of a rush: a rank test gives p = 0.37, and a Welch test separates at p = 0.023 but in the wrong
direction. We tested whether retroactive liability explains the absence, since
provisional measures can reach back 90 days where critical circumstances are found affirmatively,
and our own data does not support it: splitting on that affirmative finding, the exposed cases
show more buying ahead rather than less, at +0.067 against -0.066, Welch p = 0.012 and rank test
p = 0.0002. We report the absence without a mechanism.

Two things this does not establish. The elevation before collection is consistent with an import
surge being the reason a petition is filed, so some of the later decline may be reversion rather
than the duty. And we cannot say what share of the lost value is replaced: dividing the change in
a product's total by the change in the named country is confounded with market share, since a
supplier holding a fifth of a product can stop entirely with nobody replacing it and that
arithmetic still reports four fifths absorbed. Redone in levels, per-episode median absorption is
near zero, other suppliers fall alongside the named country in half of episodes, and their growth
does not separate from its own placebo (p = 0.28). The loss is established; its destination is
not.

## 4. Discussion

For a stakeholder exposed to one country of origin, the practical conclusion is that for
antidumping and countervailing cases the decline does not reverse within eighteen months, which argues
against waiting it out.

The methodological conclusion is the one we would most want carried forward: a product category
is the wrong unit for tariff work. The typical action names five percent of the category it
touches, and the same aggregation mixes incompatible units of measure. Both resolve at eight
digits wherever the action names a product list, which is what makes Table 1 possible. Section
232, which names a material class instead, does not resolve.

The goals are partly met. Q2 is partly answered: the fall is established and survives its
placebo, but we cannot separate volume lost outright from volume relocated, which is the
distinction Q2 asks for. Q3 has only the absence of recovery over eighteen months, with no fitted
duration model. Q1 is not answered: Table 1 has the right shape but too few events, and they are
not independent, for the reasons section 3.1 gives.

What limits all three is the same thing: our announcement dates are mostly implementing notices,
and the informative date is when a tariff becomes likely, not when it becomes official. Copper
shows it: the proclamation was signed on 30 July 2025, but imports had climbed since the 25
February order directing the investigation. The next step is to reconstruct those earlier dates,
from the two hundred initiation notices we set aside and the 2,177 case records that already
carry one.

## 5. Statement of contributions

Both authors contributed equally. Rahul Reddy Mandadi led data collection, the eight-digit
panel and its reconciliation, and the event tables.
Raunaksingh Khalsa led exploratory analysis, the anomaly detection work and the first
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
International Trade Administration antidumping and countervailing duty case index.

## 7. Appendix

### The stakeholder assumption we dropped

One stakeholder assumption did not survive the data. An earlier version named port and terminal
operators as the primary user, reasoning that a surge and collapse would disrupt throughput.
Across seven cases, the median total variation distance between a product's district mix before
and after an episode, a zero to one measure of how far two distributions sit apart, is 0.058,
against 0.068 in placebo: displaced volume arrives from another
country through much the same districts. That statistic is invariant to proportional contraction,
so it shows the mix is stable rather than the throughput, and customs value in those cases fell
by 9 to 53 percent. Seven cases is thin, and this is our reason for dropping the assumption, not
an established null.


### The copper split either side of the duty

The two halves of chapter 74 moved in opposite directions after the Section 232 action. In tonnes,
the semi-finished products the duty names ran at 49 thousand tonnes a month beforehand, peaked at
68, and have settled at 27; the untaxed cathodes ran at 89, peaked at 218, and settled at 154.
This is one product and one action with no placebo, and the figures move with the chosen windows,
so we record it as illustration rather than result. Produced by `copper_split.py`, which states
the windows explicitly.

### Two processing issues in the panel

The Census response carries an all-countries total alongside the countries it sums, which doubles
every figure if retained. We drop it and reuse it as a per-month reconciliation check. Effective
dates were re-extracted after an initial parser took dates from the rate histories that
proclamations recite, using the rules that an effective date cannot precede the announcement and
that the operative date is the one most often repeated.

### Events that did not start collection

We select events by stage rather than by an affirmative determination, so eight of the 508
episodes rest on notices that made no affirmative preliminary finding and say so, two of them
stating outright that liquidation will not be suspended (`2016-19867`, Indian off-road tires, and
`2019-10283`, Austrian strontium chromate). Those episodes carry no duty. They add noise and
should pull the estimate toward zero rather than inflate it, but we have not re-estimated without
them. This is a property of the selection rule, not of those two documents.

### Limitations

Three limitations should be stated. The tariff action sample is thin: 21 usable events, with a
single December 2018 action carrying 5,921 named product lines, so that group approximates one
large event. Pre-trends in levels are substantial for two of three legal mechanisms, which is why
we report the differenced specification. And three attempts to predict episode-level outcomes gave
negative out-of-sample R-squared; year alone explains 0.366 of the variance in retention against
0.142 for structural features in-sample, so period effects dominate. That is consistent with the
within-product design working precisely because it differences them out.


All code is in the repository linked above. The panel is built by `harvest_hs10.py` and
`build_panel_hs8.py` and filtered by `analysis_panel.py`. Events are built by
`events/harvest_fr.py`, `events/fix_effective_dates.py`, `events/harvest_adcvd.py` and
`events/parse_adcvd.py`. The coverage map is produced by `coverage/explode_products.py` and
`coverage_share.py`. The results in section 3.3 are produced by `adcvd_analysis.py`,
`adcvd_event_study.py` and `substitution_test.py`. The unit analysis in section 3.2 is produced by
`chapter_quantity.py` and `pharma_mix.py`. Negative results, including the three retired
estimators and the failed prediction models, are recorded in `PHASE2_RESULTS.md`.
