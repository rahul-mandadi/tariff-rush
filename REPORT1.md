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
993 antidumping cases. Our first attempt returned nothing, and the central result is why: the
typical action covers about five percent of the category it touches, so category-level analysis
averages any real response away. At product level we find that imports from a country named in an antidumping
case fall to their pre-case baseline and stay there, with no recovery over eighteen months and no
surge beforehand.

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
copper or pharmaceuticals, of which there are roughly ninety-seven; eight digits is where United
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

### 3.1 Category-level treatment averages the effect away

Our first attempt assigned treatment at chapter level, marking a chapter tariffed whenever any
action touched any product within it, and found no detectable effect. We measured why. Across all 1,350 pairings of one
surcharge code with one chapter, the median pairing names 5.4 percent of that chapter's import
value, and 32.4 percent of
pairings name under one percent. Collapsing to one figure per action gives a median of 1.3
percent.

The consequence is arithmetic. If a chapter is labelled treated when roughly ninety-five percent of
its value was never named, any genuine response in the treated five percent is averaged against the
untreated remainder, and the estimate is driven toward zero. The null result was a property of the
measurement, not of the world. This is the specific, quantified form of the attenuation that [2]
and [3] describe in general terms.

Fig. 1 makes the same point concretely for copper, the running example of this project. Chapter 74
comprised 24.7 billion dollars of imports across 89 eight-digit lines in 2025. The Section 232
proclamation of 30 July 2025 imposed a 50 percent duty on semi-finished copper products and
intensive copper derivatives, which account for 29 percent of the chapter by value. Refined copper
and cathodes, which alone are 67 percent of the chapter, were treated as input materials and were
not subject to the duty. A category-level analysis of copper in 2025 would therefore have assigned
a 50 percent tariff to more than two thirds of trade that never paid it.

[[FIG:1|slides/fig/09_sankey.png|Copper in 2025, by heading; widths are import value. The split between taxed and untaxed follows Proclamation 10962, paragraph 1 against paragraph 8. The annex table is not in the Federal Register text, so headings are assigned by standard meaning.]]

The split also shows what happened to the part that was named. In tonnes, the semi-finished
products covered by the duty ran at 49 thousand tonnes a month beforehand, peaked at 68, and have
settled at 27, a fall of 45 percent that has persisted. The untaxed cathodes ran at 89, peaked at
218, and settled at 154, above where they started. One product and one action with no placebo, so
we offer it as illustration rather than result; but the two halves of one chapter moved in
opposite directions, which is exactly what a category-level view cannot see.

### 3.2 Neither dollars nor quantity is a safe measure at category level

A second measurement problem comes from the same source: dollars cannot distinguish a price
increase from a volume increase. Our anomaly detector, which compares each chapter against a
baseline built from its own prior years, ranked cocoa among the most unusual categories of 2025;
cocoa prices roughly tripled after poor West African harvests, so a price movement read as a
surge in volume.

Switching to quantity is not a straightforward correction. Quantity is reported in each product's
native unit, and at chapter level those units are mixed: 56 of 98 chapters report kilograms for
under seventy percent of their value, with apparel in dozens, footwear in pairs and vessels in
units. Because the measure asks how far a chapter moved relative to its own history it is
scale-free, so units need only be stable within a chapter, not comparable across them. Restricting
to chapters whose dominant unit carries at least eighty percent of value leaves 65 of 97, of which
63 are rankable on both measures.

Fig. 2 compares them, and they disagree substantially. Pharmaceuticals is the extreme case, 2.86 on
dollars against negative 0.33 on quantity. Its tonnage in 2025 tracked trend while dollar value rose 57
percent above trend in March on flat tonnage. The increase sat in two product lines and in
high-value origins: within one line, 30049092, Switzerland shipped 4.31 billion dollars in 832
tonnes that month, roughly 5,200 dollars per kilogram, against India at 183. That is a shift in
product mix, which tonnage cannot see. In dollars cocoa is a false positive; in quantity
pharmaceuticals is a false negative. Whether pharmaceutical tonnage sat just below or just above
trend depends on anchoring the counterfactual on the last observed month or on the fitted line,
which moves the peak from negative 6 to positive 8 percent; the gap between the two measures does
not depend on that choice.

[[FIG:2|slides/fig/08_units.png|Twelve chapters ranked on dollars and on quantity, 2025. A value of 1.0 means the chapter just reached the edge of its own normal range. Pharmaceuticals runs from 2.86 on dollars to negative 0.33 on quantity; copper runs the other way, 1.77 to 2.68.]]

Both failures share a cause with section 3.1. A chapter mixes products with different treatment
status and different units of measure. An eight-digit line usually has one of each, which is why
we work there, though it is not a complete escape: 145,423 cells in the panel still span more than
one unit and carry 4.6 percent of total value.

### 3.3 The aftermath of an antidumping duty is a durable loss with no preceding surge

Antidumping and countervailing duty proceedings give the event sample with adequate power: the
cases are numerous, name products explicitly, and target individual countries. Fig. 3 traces imports from the named country around the month duties begin to be
collected, across 673 events, measured against a baseline eighteen to thirteen months prior.

The path is not the one the front-loading literature predicts. Imports from the named country are
already 37 percent above baseline a year before duties begin, rising to 46 percent at five months
out. They then decline steadily, stand 17.7 percent above baseline in the month collection starts,
cross baseline within four months, and stay flat through eighteen months. There is no surge before
the duty and no recovery after it.

[[FIG:3|slides/fig/10_event.png|Imports from the country named in an antidumping case, 673 events, against a baseline eighteen to thirteen months before duties begin. Shading is the 95 percent interval.]]

**Table 1.** Episode-level excess imports for the named country, real events against the same
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
antidumping cases the decline is not temporary. Volumes from the named country do not recover
within eighteen months, which argues for treating the loss as permanent rather than waiting it
out. We cannot yet say whether that volume reappears elsewhere, so a stakeholder should not assume the
product stays equally available.

One stakeholder assumption did not survive the data. An earlier version named port and terminal
operators as the primary user, reasoning that a surge and collapse would disrupt throughput.
Across seven cases, the median total variation distance between a product's district mix before
and after an episode is 0.058, against 0.068 in placebo: displaced volume arrives from another
country through much the same districts. That statistic is invariant to proportional contraction,
so it shows the mix is stable rather than the throughput, and customs value in those cases fell
by 9 to 53 percent. Seven cases is thin, and this is our reason for dropping the assumption, not
an established null.

The methodological conclusion is the one we would most want carried forward: tariff effects should
not be measured at product-category level. The typical action names about five percent of the
category it touches, and the same aggregation mixes incompatible units of measure. Both largely
resolve at the eight-digit level, where tariff orders are written.

The goals are partly met. The second question is answered for antidumping cases and survives
placebo testing; the third has a partial answer in the absence of recovery over eighteen months,
but no fitted duration model. The first remains open, blocked by a limitation we have diagnosed
but not resolved: the median interval between the announcement date we hold and the start of
collection is 8.5 days, far too short for any meaningful acceleration of shipments. Most of our
documents are implementing notices rather than first announcements. Copper illustrates this. The
proclamation was signed on 30 July 2025, but imports had climbed since February, following the
executive order of 25 February directing a Section 232 investigation and the request for comment
of 13 March. The informative date is when a tariff becomes likely, not when it becomes official.

The next step is to reconstruct earlier information dates. Roughly two hundred of the documents
we set aside are initiation notices or requests for comment, and the antidumping data already
carries initiation dates for 2,177 records.

## 5. Statement of contributions

Both authors contributed equally to this project. Rahul Reddy Mandadi led data collection and panel
construction, including the Census ten-digit harvest, the eight-digit product-by-partner-by-month
panel and its reconciliation against published totals, and the tariff and antidumping event tables.
Raunaksingh Khalsa led exploratory data analysis, the anomaly detection work, and the design and
delivery of the first presentation. Both authors jointly developed the research questions, selected
the identification strategy, interpreted the results, and wrote this report.

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

[6] Cleveland, R., Cleveland, W., McRae, J. and Terpenning, I. (1990). STL: A seasonal-trend
decomposition procedure based on LOESS. *Journal of Official Statistics* 6(1), 3-73.

**Data sources.** United States Census Bureau international trade API; Federal Register API;
United States International Trade Commission Harmonized Tariff Schedule, chapter 99; United States
International Trade Administration antidumping and countervailing duty case index.

## 7. Appendix

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
