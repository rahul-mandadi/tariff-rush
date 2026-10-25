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
country named in an antidumping case fall to their pre-case baseline and stay there, with no
recovery over the eighteen months we observe and no surge beforehand.

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
what follows a tariff for a given product and country of origin. This decomposes into three
analytic problems: whether a surge occurs and how large, a classification problem followed by a
regression; what the post-duty decline represents, a three-way classification between volume
borrowed from later months, demand lost outright, and volume relocated to an untargeted country;
and how long the aftermath persists, a duration problem with right-censoring, since some episodes
are still in progress at the end of our panel.

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
partners. Two processing issues were material. The Census response carries a row denoting the total
across all countries alongside the countries it sums; retaining it doubles every figure, and
January 2015 initially reported 362.4 billion dollars against a true 181.2 billion. We drop it and
reuse it as a per-month reconciliation check, which all 140 months pass, and our 2017 total is 2.34
trillion dollars against a published 2.34 trillion. Separately, our initial parser took the first
date near an effective-date phrase, which fails because proclamations recite earlier rate changes
in identical wording; dates were re-extracted on the rules that an effective date cannot precede
the announcement and that the operative date is the one most often repeated.

For modelling we apply inclusion rules fixed in advance: at least 36 months of observed data,
a median monthly value of at least 100,000 dollars, and at least one untreated origin supplying the
same product in the same month. This retains 6.09 million observations carrying 95.7 percent of
total import value.

### 2.3 Event construction

We searched 2,792 Federal Register documents and classified 134 as actions imposing or modifying a
duty; the remaining 2,658 are proposed rules, administrative notices, exclusion procedures and
trade remedy documents. We separately harvested antidumping and countervailing duty proceedings,
yielding 993 cases across 70 countries and 1,297 named product lines, with case numbers linking
each proceeding's initiation, preliminary, final and order stages. From chapter 99 we resolved
9,083 eight-digit lines named across 162 surcharge codes, giving 1,350 pairings of one surcharge code with one
chapter. We call these actions below, though one Federal Register action may cite several codes.

### 2.4 Identification and evaluation

We compare a product from a targeted country against the same product from untargeted countries
in the same month. A price shock or global demand movement affects every supplier at once and
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
published as an annex to a separate legal notice. How much of a category that list covers is an
empirical question, and to our knowledge it has not been measured for United States tariff
actions. Across all 1,350 pairings of one surcharge code with one chapter, the median pairing
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

Granularity alone does not then deliver an answer. Re-estimating the same tariff actions at eight
digits, where treatment is exact, Table 1 shows no common pattern in the months after a duty
begins and significant movement before it in all three legal mechanisms.

**Table 1.** The same tariff actions estimated at eight digits, by legal mechanism. Each figure is
the differenced estimate at month k relative to the duty start, against untargeted origins of the
same product; k is months. Asterisks mark significance at 5 percent.

| mechanism | k = 0 | k = 1 | k = 2 | k = 3 | pre-period months significant |
| --- | --- | --- | --- | --- | --- |
| enumerated, Section 301 lists | +27%* | -37%* | -7%* | -22%* | 4 of 6 |
| country-wide, IEEPA | -15%* | +8%* | -8%* | -6%* | 5 of 6 |
| material class, Section 232 | -3% | -10%* | -14%* | 0% | 2 of 6 |

Exact treatment removes the dilution, and the estimates remain unstable. Two constraints are
therefore separable: how a tariff order is written, which this section measures, and when it
becomes known, which section 4 takes up and which the 8.5-day median window makes acute. The
antidumping cases in section 3.3 are not subject to the second constraint, which is why they
carry the identification that these events cannot.

### 3.2 Neither dollars nor quantity is a safe measure at category level

A second measurement problem comes from the same source: dollars cannot distinguish a price
increase from a volume increase. Our anomaly detector scores each chapter by how far its furthest
2025 month ran from a counterfactual fitted on its own prior years, in units of that series'
residual standard deviation, so a score of 1.0 means the chapter just reached the edge of its
normal range. On dollars it ranked cocoa among the most unusual categories of 2025; cocoa prices
roughly tripled after poor West African harvests, so a price movement read as a surge in volume.

Switching to quantity is not a straightforward correction. Quantity is reported in each product's
native unit, and at chapter level those units are mixed: 56 of 98 chapters report kilograms for
under seventy percent of their value, with apparel in dozens, footwear in pairs and vessels in
units. Restricting to chapters whose dominant unit carries at least eighty percent of value leaves
65 of them, of which 63 are rankable on both measures, and the two rankings disagree substantially.

Pharmaceuticals is the extreme case, 2.86 on dollars against negative 0.33 on quantity. Its
tonnage in 2025 tracked trend while dollar value rose 57 percent above trend in March on flat
tonnage, concentrated in two lines and in high-value origins: within line 30049092, Switzerland
shipped 4.31 billion dollars in 832 tonnes that month, roughly 5,200 dollars per kilogram, against
India at 183. That is a shift in product mix, which tonnage cannot see. Copper runs the other way,
1.77 on dollars against 2.68 on quantity. In dollars cocoa is a false positive; in quantity
pharmaceuticals is a false negative. Both scores move with the counterfactual's anchoring, which
shifts pharmaceutical tonnage from negative 6 to positive 8 percent, but the gap between the two
measures does not.

Both failures share a cause with section 3.1. A chapter mixes products with different treatment
status and different units of measure. An eight-digit line usually has one of each, which is why
we work there, though 145,423 cells carrying 4.6 percent of value still span more than one unit.

### 3.3 The aftermath of an antidumping duty is a durable loss with no preceding surge

Antidumping and countervailing duty proceedings give the event sample with adequate power: the
cases are numerous, name products explicitly, and target individual countries. Fig. 2 traces imports from the named country around the month duties begin to be
collected, across 673 events, measured against a baseline eighteen to thirteen months prior.

The path is not the one the front-loading literature predicts. Imports from the named country are
already 37 percent above baseline a year before duties begin, rising to 46 percent at five months
out. They then decline steadily, stand 17.7 percent above baseline in the month collection starts,
cross baseline within four months, and stay flat through eighteen months. There is no surge before
the duty and no recovery after it.

[[FIG:2|slides/fig/10_event.png|Imports from the country named in an antidumping case, 673 events, against a baseline eighteen to thirteen months before duties begin. Shading is the 95 percent interval.]]

Table 2 sets the episode-level comparison against its placebo.

**Table 2.** Episode-level excess imports for the named country, real events against the same
events shifted back 24 months, a log deviation from each cell's own pre-event level.

| measure | real events | placebo at minus 24 months |
| --- | --- | --- |
| episodes | 508 | 473 |
| median excess during the window | +0.031 | +0.037 |
| median excess after | **-0.316** | +0.020 |

The post-period difference separates from its placebo at p < 0.0001 on both a rank test and a
t-test, and is robust across horizons of six, nine and twelve months. The during-window difference is not evidence of a
rush: a rank test gives p = 0.37, and a Welch test separates at p = 0.023 but in the wrong
direction, real mean negative 0.018 against positive 0.063 in placebo. The absence is
explicable rather than anomalous: antidumping duties can be applied retroactively to the initiation
notice, so accelerating purchases offers no protection. This contrast is itself a finding, because
it suggests that whether a tariff produces a surge depends on whether the duty can be escaped by
buying early.

We cannot say what share of the lost volume is replaced. Dividing the median change in a
product's total by the median change in the named country, as we first did, is confounded with
market share: a supplier holding a fifth of a product can stop entirely with nobody replacing it
and that arithmetic still reports four fifths absorbed. Redone in levels, where treated and other
suppliers sum to the total by construction, the per-episode median absorption is near zero, other
suppliers fall alongside the named country in half of episodes, and the dispersion is far too
large to estimate from. The component measuring whether other suppliers grow also fails its
placebo, 4.2 against 6.6 percent at p = 0.28. The loss to the named country is established; its
destination is not.

## 4. Discussion

For a stakeholder exposed to one country of origin, the practical conclusion is that for
antidumping cases the decline does not reverse within the eighteen months we observe, which
argues against waiting it out. We cannot yet say whether that volume reappears elsewhere.

One stakeholder assumption did not survive the data. An earlier version named port and terminal
operators as the primary user, reasoning that a surge and collapse would disrupt throughput.
Across seven cases, the median total variation distance between a product's district mix before
and after an episode is 0.058, against 0.068 in placebo: displaced volume arrives from another
country through much the same districts. That statistic is invariant to proportional contraction,
so it shows the mix is stable rather than the throughput, and customs value in those cases fell
by 9 to 53 percent. Seven cases is thin, and this is our reason for dropping the assumption, not
an established null.

The methodological conclusion is the one we would most want carried forward: a product category
is the wrong unit for tariff work. The typical action names five percent of the category it
touches, and the same aggregation mixes incompatible units of measure. Working at eight digits
removes both, though section 3.1 shows it is not on its own sufficient to identify an effect.

The goals are partly met. The second question is answered for antidumping cases and survives
placebo testing; the third has a partial answer in the absence of recovery over eighteen months,
but no fitted duration model. The first remains open, and section 3.1 locates why: the median
interval between the announcement date we hold and the start of collection is 8.5 days, too short
for any meaningful acceleration of shipments, because most of our documents are implementing
notices rather than first announcements. Copper illustrates it. The proclamation was signed on 30
July 2025, but imports had climbed since February, following the executive order of 25 February
directing a Section 232 investigation. The informative date is when a tariff becomes likely, not
when it becomes official.

The next step is to reconstruct earlier information dates. Roughly two hundred of the documents
we set aside are initiation notices or requests for comment, and the antidumping data already
carries initiation dates for 2,177 records.

## 5. Statement of contributions

Both authors contributed equally. Rahul Reddy Mandadi led data collection and panel construction,
including the Census harvest, the eight-digit panel and its reconciliation, and the tariff and
antidumping event tables. Raunaksingh Khalsa led exploratory analysis, the anomaly detection work,
and the first presentation. Both developed the research questions, chose the identification
strategy, interpreted the results, and wrote this report.

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
