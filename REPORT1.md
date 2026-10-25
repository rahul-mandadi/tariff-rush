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
enough to drive a category-level estimate toward zero. Separately, we find that imports from a
country named in an antidumping case lose roughly a quarter of their standing against other
suppliers of the same product, measured in customs value, and do not regain it within the
eighteen months we observe.

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
and qualifying an alternative supplier, which takes months and carries real cost; a lender holds
the same uncertainty as credit risk. The information that would resolve it arrives far later.
Census publishes monthly trade roughly five weeks after the reference month closes, so by the time
two post-tariff months are observable the duty has been in force for a quarter and the commitments
are made.

The domain problem is therefore to characterise, using only information available at announcement,
what follows a tariff for a given product and origin. It decomposes into three analytic problems.
Whether a surge occurs and how large is a classification problem followed by a regression. What
the post-duty decline represents is a three-way classification: volume borrowed from later
months, demand lost outright, or volume relocated to an untargeted country. How long the
aftermath persists is a duration problem with right-censoring, since some episodes are still
running at the end of our panel.

Existing work measures tariff responses at fine granularity for good reason. Fajgelbaum et al. [1]
study the 2018 tariffs at ten digits, noting the increases were predominantly set at eight. The
International Trade Commission [2] estimates the same elasticity at two, four, six and eight
digits and finds coarser data gives systematically smaller estimates, attributed to heterogeneity
bias; Imbs and Mejean [3] report the same outside the tariff setting, and Flaaen and Pierce [4]
use a continuous exposure measure rather than a binary indicator. Our first result quantifies how
severe this is for United States tariff actions.

## 2. Methods

### 2.1 Data

We use two public sources. Monthly import statistics come from the Census Bureau international
trade API, which reports value in dollars, a quantity in each product's native unit, and shipping
weight by mode. Tariff actions come from the Federal Register API. The product lists behind each
action come from chapter 99 of the Harmonized Tariff Schedule.

Products are classified hierarchically: two digits denote a chapter, a broad category such as
copper or pharmaceuticals, of which 98 appear in our panel; eight digits is where United
States tariff orders name products; ten is the finest level Census publishes. We harvest at ten
and aggregate to eight, because ten nests exactly inside eight, so a tariff matches precisely the
products it names.

### 2.2 Panel construction

The panel covers 140 months from January 2015 to August 2026: 15.9 million observations of one
eight-digit product, one partner country and one month, across 12,253 product lines and 234
partners. Two processing issues were material. The Census response carries an all-countries total alongside
the countries it sums, which doubles every figure if retained; we drop it and reuse it as a
per-month check that all 140 months pass, and our 2017 total is 2.34 trillion dollars against a
published 2.34 trillion. Effective dates were re-extracted after an initial parser took dates
from the rate histories proclamations recite, using the rules that an effective date cannot
precede the announcement and that the operative date is the one most often repeated.

For modelling we apply inclusion rules fixed in advance: at least 36 months of observed data,
a median monthly value of at least 100,000 dollars, and at least one untreated origin supplying the
same product in the same month. This retains 6.09 million observations carrying 95.7 percent of
total import value, but only 8,100 of the 12,253 product lines and 193 of the 234 partners. The
cells that drop are thin, so the value share overstates how much of the product space survives.

### 2.3 Event construction

We searched 2,792 Federal Register documents and classified 134 as actions imposing or modifying a
duty; the remaining 2,658 are proposed rules, administrative notices, exclusion procedures and
trade remedy documents. We separately harvested antidumping and countervailing duty proceedings,
yielding 993 cases across 70 countries and 1,297 named product lines, with case numbers linking
each proceeding's initiation, preliminary, final and order stages. From chapter 99 we resolved
9,083 eight-digit lines named across 162 surcharge codes, giving 1,350 pairings of one surcharge code with one
chapter. We call these actions below, though one Federal Register action may cite several codes.

### 2.4 Identification and evaluation

The outcome throughout is the log of nominal customs value. Quantity is not available on a common
unit across cells, so it is used for the chapter work in section 3.2 and not for the event
studies, which is also the reason to read the value results with the care section 3.2 argues
for. We compare
a product from a targeted country against the same product from untargeted countries in the same
month. A price shock or global demand movement affects every supplier at once and
cancels, whereas a tariff moves one against the rest. The design is available for 89.6 percent of
treated product-months, which have two or more suppliers, median seven.

Every estimate is paired with a placebo: the identical calculation applied to the same events
shifted 24 months earlier, where no action occurred. An estimate that does not separate from its
own placebo is not reported as a result. This discipline has retired three candidate estimators
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
intensive copper derivatives, 29 percent of the chapter by value. Refined copper and cathodes,
which alone are 67 percent of the chapter, were treated as input materials and were not subject to
the duty.

[[FIG:1|slides/fig/09_sankey.png|Copper in 2025, by heading; widths are import value. The split between taxed and untaxed follows Proclamation 10962, paragraph 1 against paragraph 8. The annex table is not in the Federal Register text, so headings are assigned by standard meaning.]]

This has a direct consequence for measurement. A category-level treatment flag assigns treatment
to mostly untreated trade, so any genuine response is averaged against a much larger unaffected
remainder. Testing it directly, chapter-months touched by an action are more anomalous than
untouched ones, but barely: medians of negative 7.1 against negative 7.6 percent across 1,815 and
7,977 chapter-months, one-sided p = 0.0075. The difference is detectable and economically
negligible, which is what heavy dilution predicts. This is the specific, quantified form of the
attenuation that [2] and [3] describe in general terms.

Re-estimating the same tariff actions at eight digits, where treatment is exact, then shows what
the category-level view could not. Table 1 reports a first-differenced specification, so each
figure is the month-over-month change in log import value against the same change in the baseline
months; a one-month jump in the level appears as a positive followed by a negative.

**Table 1.** The same tariff actions at eight digits, by legal mechanism, first-differenced.
Month 0 is the announcement month, not the duty start. Each figure is the month-over-month change
in log import value for the targeted origin against untargeted origins of the same product.
Asterisks mark significance at 5 percent; event counts are nine, four and eight documents.

| mechanism | k = -2 | k = -1 | k = 0 | k = 1 |
| --- | --- | --- | --- | --- |
| enumerated, Section 301 lists | -16%* | +1% | **+27%*** | -37%* |
| country-wide, IEEPA | **+9%*** | -10%* | -15%* | +8%* |
| material class, Section 232 | +0% | **+13%*** | -3% | -10%* |

The jump arrives at a different month in each mechanism, and the ordering tracks how much warning
each one gives. Section 301 lists are published with the action, and the jump is in the
announcement month itself. IEEPA measures were trailed publicly, and the jump comes two to three
months before the announcement. Section 232 duties follow an investigation, and the jump comes one
month before. That is front-loading whose timing moves with how early the duty became knowable,
which is the same point section 4 makes about announcement dates.

Two caveats belong with it. The pre-periods are not flat, with four, five and two of six months
individually significant, so this is a pattern consistent with front-loading rather than a clean
identified effect. And the three rows rest on nine, four and eight documents, with standard errors
clustered on product-origin cells rather than on events, so the asterisks are optimistic.

### 3.2 Neither dollars nor quantity is a safe measure at category level

A second measurement problem comes from the same source. Our anomaly detector scores each chapter
by how far its furthest 2025 month ran from a counterfactual fitted on its own prior years, in
units of that series' residual standard deviation, so 1.0 is the edge of the normal range. On
dollars it ranked cocoa among the most unusual categories of 2025, but cocoa prices roughly
tripled after poor West African harvests, so a price movement read as a surge in volume.

Quantity is not a clean substitute. It comes in each product's native unit, and at chapter level
those are mixed: 56 of 98 chapters report kilograms for under seventy percent of their value,
with apparel in dozens and footwear in pairs. Restricting to chapters whose dominant unit carries
eighty percent of value leaves 65, of which 63 are rankable on both measures, and the two
rankings disagree sharply. Pharmaceuticals scores 2.86 on dollars and negative 0.33 on quantity:
its tonnage tracked trend while dollar value rose 57 percent above trend in March, concentrated
in high-value origins, which is a shift in product mix that tonnage cannot see. Copper runs the
other way, 1.77 against 2.68. In dollars cocoa is a false positive; in quantity pharmaceuticals
is a false negative.

Both failures share a cause with section 3.1. A chapter mixes products with different treatment
status and different units. An eight-digit line usually has one of each, though 145,423 cells
carrying 4.6 percent of value still span more than one unit.

### 3.3 The aftermath of an antidumping duty is a durable loss with no preceding surge

Antidumping proceedings give the event sample with adequate power: the cases are numerous, name
products explicitly, and target individual countries. Fig. 2 traces the named country against
other suppliers of the same product across 673 events, from a baseline eighteen to thirteen months
before collection begins; product-month and product-origin fixed effects make each point relative
rather than a level. Cell-months claimed by more than one case are dropped, 27,255 of the 65,488
falling in any window.

The path is not the one the front-loading literature predicts. The named country runs about 42
percent above its baseline position through the year before collection, declines from roughly four
months out, and averages 6 percent across the eighteen months after. In the model's own units that is a fall of 0.30 log points,
about 26 percent against other suppliers of the same product, and it does not reverse. It is also not a complete
displacement: eight of the nineteen post-period months are individually significant and all eight
remain above baseline.

[[FIG:2|slides/fig/10_event.png|The named country against other suppliers of the same product, 673 events, from a baseline eighteen to thirteen months before collection begins. Shading is the 95 percent interval on the real path. The placebo repeats the estimation on the same events shifted back 24 months.]]

The same estimation on events shifted back 24 months gives a path that rises rather than falls
over the same event time. That placebo is not a clean null, because shifting back two years puts
its post window inside the real pre-period, so it is a contrast rather than a zero. The elevation
before collection is in any case consistent with an import surge being why a petition is filed,
so part of the later decline may be reversion rather than the duty.

Table 2 sets the episode-level comparison against its placebo.

**Table 2.** Episode-level excess imports for the named country, real events against the same
events shifted back 24 months, a log deviation from each cell's own pre-event level.

| measure | real events | placebo at minus 24 months |
| --- | --- | --- |
| episodes | 508 | 473 |
| median excess during the window | +0.031 | +0.037 |
| median excess after | **-0.316** | +0.020 |

The post-period difference separates from its placebo at p < 0.0001 on both a rank test and a
t-test, robust across horizons of six, nine and twelve months. The during-window difference is not evidence of a
rush: a rank test gives p = 0.37, and a Welch test separates at p = 0.023 but in the wrong
direction, real mean negative 0.018 against positive 0.063 in placebo. We considered whether
retroactive liability explains the absence, since provisional measures can reach back 90 days
where critical circumstances are found. Our own data does not support it: splitting the episodes
on that finding, the cases carrying critical circumstances show more buying ahead rather than
less, at +0.063 against -0.065, Welch p = 0.015. We report the absence without a mechanism for
it.

We cannot say what share of the lost value is replaced. Dividing the median change in a product's
total by the median change in the named country is confounded with market share: a supplier
holding a fifth of a product can stop entirely with nobody replacing it and that arithmetic still
reports four fifths absorbed. Redone in levels, where the series are additive, per-episode median
absorption is near zero, other suppliers fall alongside the named country in half of episodes,
and the dispersion is too large to estimate from. The component measuring whether other suppliers
grow also fails its placebo at p = 0.28. The loss is established; its destination is not.

## 4. Discussion

For a stakeholder exposed to one country of origin, the practical conclusion is that for
antidumping cases the decline does not reverse within the eighteen months we observe, which
argues against waiting it out. We cannot yet say whether that volume reappears elsewhere.

The methodological conclusion is the one we would most want carried forward: a product category
is the wrong unit for tariff work. The typical action names five percent of the category it
touches, and the same aggregation mixes incompatible units of measure. Both resolve at eight
digits, which is where the rush in Table 1 becomes visible at all.

The goals are partly met. The first question has a partial answer in Table 1: a rush exists and
its timing moves with how early the duty became knowable, though on four to nine events per
mechanism and with pre-periods that are not flat. The second is answered for antidumping cases
and survives placebo testing. The third has only the absence of recovery over eighteen months,
with no fitted duration model.

What limits all three is the same thing: our announcement dates are mostly implementing notices,
and the informative date is when a tariff becomes likely, not when it becomes official. Copper
shows it. The proclamation was signed on 30 July 2025, but imports had climbed since February,
after the 25 February order directing a Section 232 investigation.

The next step is to reconstruct earlier information dates: roughly two hundred of the documents
we set aside are initiation notices, and the antidumping data already carries initiation dates
for 2,177 records.

## 5. Statement of contributions

Both authors contributed equally. Rahul Reddy Mandadi led data collection and panel construction,
the Census harvest, the eight-digit panel and its reconciliation, and the event tables.
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
and after an episode is 0.058, against 0.068 in placebo: displaced volume arrives from another
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
