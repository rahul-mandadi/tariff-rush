# Design notes from the script headers

Each script used to open with a long header explaining its design. On 2026-11-15 those headers
were shortened to what the script does, reads, writes and how to run it, and the full text was
moved here unchanged, one section per script. These are source notes to be rewritten in plain
words; they are not edited.

## adcvd_analysis.py

```text
Rush and repayment around antidumping and countervailing duty cases.

Why these events and not the Section 232/301/IEEPA set: there are far more of them, each
names one country and an explicit product scope, and the window between a case becoming
public and duties being collected is months rather than days. Monthly import data cannot
resolve a four day window, which is the median in the other event set. It can resolve six.

The clock runs from the initiation date, which is when the case becomes public and importers
can begin buying ahead, to the preliminary determination, which is when duties start being
collected. Both come out of the preliminary notice itself.

Baseline is the same product from origins not named by the case, in the same month. Nothing
is extrapolated, because placebo tests showed a fitted baseline drifts far enough to
manufacture a result (see docs/history/PHASE2_RESULTS.md).

Every number is produced twice, once for the real events and once with every event shifted
back 24 months. A result that does not separate from its own placebo is not reported as a
result.

Usage:  python3 adcvd_analysis.py [--h 9] [--min-window 60]
```

## adcvd_event_study.py

```text
Month-by-month path of imports around an AD/CVD preliminary determination.

The episode test says imports from a targeted origin fall about 27 percent against other
origins of the same product, and that there is no rush beforehand. Two summary numbers cannot
show whether that drop is a step at the determination or a trend that was already running, and
the difference decides whether it can be read as caused by the duty.

k = 0 is the month duties start being collected. Fixed effects are product-month and
product-origin, so what is left is one origin moving against the others supplying the same
product that month. Baseline is k in [-18,-13].

A cell-month that falls inside more than one case's event window is dropped, since China and
Korea cells in particular are named by many cases and a contaminated observation cannot be
attributed to one of them. An earlier version assigned such a month to whichever case it met
first and dropped nothing, which left overlapping treatments pooled.

The same estimation is run on events shifted back 24 months, where no determination occurred, so
the path can be read against a placebo rather than against zero.

Usage:  python3 adcvd_event_study.py [--min-window 60]
```

## adcvd_stacked.py

```text
AD/CVD aftermath on a fixed cohort that keeps zero-trade months: a stacked event study.

adcvd_event_study.py pools every cell-month into one regression. Its treated cohort changes with
event time (975 cells at k = 0, 1,437 at k = 18), product-country pairs that stop trading leave
the panel, months outside any window act as reference alongside the baseline, and companion
notices for one case claim the same months and get dropped. archive/adcvd_cohort_check.py showed the
headline fall is sensitive to all of that. This script rebuilds the estimate so none of it
applies.

Design
  episode     notices for one targeted country, initiated in the same month, with overlapping
              products (companion AD and CVD notices) collapse to one episode, dated at the
              first preliminary determination, k = 0.
  notices     only affirmative preliminary determinations. EXCLUDE lists 31 notices that are
              negative, critical-circumstances-only, administrative-review / no-shipment, or
              circumvention notices on existing orders, each read from its own summary (review of
              2026-11-06; the three circumvention preliminaries added 2026-11-07; the last seven
              critical-circumstances-only notices added 2026-11-09).
  side        critical-circumstances-only notices (CC_ONLY) never define k = 0 or an episode. They
              are kept as dated information: events/cc_side_notices.csv holds one row per notice
              and country (affirmative or not, read from each summary), attached to the episode of
              the same country whose own notices name the same product in their titles, share
              one of its product codes and were initiated on or before it (if several, the one
              whose notices cite its case number). The forecasts read critical circumstances from the
              episode's own notices and these side notices, each only once it was published.
  stack       one per episode: the episode's products, the targeted country, and every rival
              country trading those products before the case, over k = -18 to +18.
  cohort      fixed from pre-case information only. A product-country pair is in the stack if
              it traded at least once in k = -18 to -7 and before the case's initiation month.
              It stays in for every later month whether or not it trades.
  zeros       a month with no reported trade is zero. A product-month with no imports from any
              country is dropped (the code was not in use). Months past the data end are not
              observed and are not filled.
  controls    rivals that are themselves named on that product by an episode with k = 0 within
              36 months before to 18 months after are dropped from the stack.
  estimators  PPML on value (zeros included; the coefficient is a proportional change in the
              targeted country's expected imports against rivals of the same product and month),
              a linear probability model on whether the pair trades at all, and OLS on log value
              among positive months (the original outcome, for comparison only).
              Fixed effects: stack x product x month and stack x product x country.
              Event-time indicators for the targeted country, k = -12 to 18; k = -18 to -13 is
              the reference. Standard errors clustered on investigation groups (episodes sharing
              an initiation month and products, i.e. one petition across countries).
  placebo     the same stacks with k = 0 moved 24 months earlier.

Usage:  python3 adcvd_stacked.py
```

## adcvd_stacked_qty.py

```text
The stacked AD/CVD aftermath, on physical quantity instead of dollar value.

Kylie asked whether the data are inflation-adjusted. In the within-product design a price change
shared by every supplier cancels, but a price change specific to the targeted country does not:
if the duty makes the targeted exporter cut its price, value falls even when tonnage holds. This
reruns adcvd_stacked.py's estimator on quantity, and on value for exactly the same rows, so the two
can be compared on one sample.

A stack's product is kept only if every trading row in its window reports quantity in one unit,
the same unit for every country and month (qty_ok in the panel, one unit across the product's
ten-digit lines). A month with no trade is zero quantity, as for value.

Reads panel/adcvd_stacks_real.parquet and panel/adcvd_stacks_placebo.parquet, written by
adcvd_stacked.py.

Usage:  python3 adcvd_stacked_qty.py
```

## analysis_panel.py

```text
Apply the inclusion rules from docs/history/DESIGN.md and write the panel the tests run on.

Rules, fixed before any model was fit:
  - at least 36 months of history in the cell (an STL baseline needs three cycles)
  - median monthly value at least $100,000 (drops cells that are noise)
The third rule, that an untreated origin must exist for the same product and month,
is applied inside the test because it depends on which event is being looked at.

Output: panel/analysis.parquet

Usage:  python3 analysis_panel.py
```

## build_decision_stacks.py

```text
Comparison panels for the prediction tests, built only from what was known at the decision.

adcvd_stacked.py drops rival countries that another case names on the same product from 36 months
before to 18 months after the duty. That is right for measuring the aftermath, but a forecaster at
the fall or at the ITC vote could not know about cases filed later. Here a rival is left out only
if its own first preliminary was published on or before this episode's first preliminary (exact
dates, not months), and the products are only those named in notices published by that date, not
ones a later companion notice adds. Both are known at every later decision point and both rules are
asserted below. Everything a prediction test uses (the visible share path,
whether a product has fallen, the trade features and the outcome labels) is computed on these
panels; the descriptive results keep adcvd_stacked.py's panels.

Writes panel/adcvd_stacks_decision.parquet (ignored by git, rebuilt here) and the outcome files
recovery_pairs_decision_fall20.csv (H = 18) and s301_adcvd_pairs_h16_decision.csv (H = 16), with
recovery_lib.categorize, the rule recovery_benchmark.py uses.

Usage:  python3 build_decision_stacks.py      # from the repo root
```

## build_panel_hs8.py

```text
Roll the HS10 month checkpoints up to the analysis grid: HS8 x partner x month.

HS10 is the pull level because it nests exactly under the HS8 lines the tariff
orders name. HS8 is the analysis level because that is what the orders name.

Quantity needs care. UNIT_QY1 is the unit native to each HS10 line, so two lines
under the same HS8 can be measured in different units (KG and NO, say) and
summing them would be meaningless. Where that happens the quantity is set to
null and the cell is flagged, so those cells fall back to value rather than
silently carrying a nonsense number.

CTY_CODE "-" is a TOTAL FOR ALL COUNTRIES row sitting in the same response as
the countries it sums. Left in, it doubles every total. Dropped and kept aside,
it is a free reconciliation check: the 226 real partners must add back to it.

Writes one parquet per month so memory stays flat and a rerun is cheap.

Usage:  python3 build_panel_hs8.py
```

## build_treatment.py

```text
Resolve each tariff event to the panel cells it actually treats.

Three mechanisms, because the orders are written three different ways, and they do not
carry the same amount of dilution:

  ENUMERATED     the order lists HS8 subheadings. Exact match, no dilution.
  COUNTRY_WIDE   IEEPA hits everything from a partner. Also exact: every product from
                 that origin is treated, so there is no product dilution either.
  MATERIAL_CLASS Section 232 names a material, not a list. Resolved to chapters, so this
                 is the one group that still carries dilution and is reported separately.

Dates come from events/tariff_events_dates.csv, which corrected 17 impossible effective
dates. The announcement-to-effective window is the period a rush could happen in.

Outputs
  events_resolved.csv   one row per event x partner, with mechanism and dates
  event_products.csv    one row per enumerated event x HS8 line

Usage:  python3 build_treatment.py
```

## calibrated_lookup.py

```text
Calibrated lookup: the second-decision-point models (prediction_stage2.py) as a table a sourcing
team can read, "of 100 products like yours, about N came back".

Calibration: the held-out predictions run high in places. For each test year Y, a Platt scaling
(logistic regression on the logit of the model's probability) is fitted only on held-out predictions
of earlier years whose month 18 had been published before January of Y (at least 50 products), and
applied to year Y. Earlier test years have too little published history and stay uncalibrated. Compared on the years
that can be calibrated: Brier score and calibration by predicted tercile, raw against calibrated.

Lookup cells, using facts visible at each decision:
  at the fall      the targeted supplier's pre-case imports (12 months, k -18..-7) under $1M, $1M to
                   $10M, over $10M; and the preliminary duty rate missing, up to 25 percent, over 25
  at the ITC vote  the latest published share against the pre-case level (under half, half to
                   four-fifths, four-fifths or more); and the vote (duty confirmed or lifted)
Each cell: held-out products and cases, the model's average prediction, and the share that actually
came back. The cells use the uncalibrated prediction, because the calibration test above made later
years worse once it was restricted to labels already published. Cells with fewer than 20 products or 5 cases are marked too few.
Episode-weighted, as everywhere else.

Usage:  python3 calibrated_lookup.py      # after prediction_stage2.py
```

## chapter_quantity.py

```text
Rebuild the chapter anomaly ranking on quantity instead of dollars.

Kylie Bemis asked for this in the presentation on 2026-10-16, after the cocoa example: a dollar
series cannot tell a price spike from a volume surge, so the detector on slide 6 was measuring
the wrong thing for at least two of the ten chapters it flagged.

It is not a simple swap. Quantity is reported in the unit native to each product, and at chapter
level those units are mixed: apparel is in dozens, footwear in pairs, ships in units, and 56 of
98 chapters report kilograms for under 70% of their value. The anomaly measure is scale-free,
since it asks how far a chapter went outside its OWN band, so the unit does not have to match
across chapters. It does have to be stable within one.

So this keeps only the dominant unit per chapter, and only chapters where that unit covers at
least MIN_COVER of chapter value. Everything else has no usable quantity series at chapter level
and is reported as such rather than silently dropped.

Usage:  python3 chapter_quantity.py      # from the repo root
```

## copper_split.py

```text
The copper tonnage split either side of the Section 232 duty.

Reported in the appendix of REPORT1.md. Committed because the figures were first computed
interactively and nothing in the repository reproduced them, which is not a standard we want to
apply to other people's work and not our own.

Headings 7407 to 7413 are the semi-finished products the duty names; 74031100 is refined cathodes,
which paragraph 8 of Proclamation 10962 treats as an input material and does not tax. Both series
count only rows reported in kilograms. Windows are stated explicitly because the result moves with
them: a pre-action baseline of August 2024 to January 2025, the peak month of March to July 2025,
and a settled average over March to August 2026.

Usage:  python3 copper_split.py      # from the repo root
```

## coverage/build_coverage.py

```text
Map each HTS chapter 99 surcharge code to the products and countries it covers.

A surcharge code says a duty exists. What it applies to is either written in the code's own
description or delegated to a U.S. note published separately. Chapter 99 has several subchapters
with independent note numbering, and the tariff actions live in subchapter III, so notes are
parsed within that span only.

Outputs
  coverage/surcharge_codes.csv   one row per 9903 code: rate, countries, note reference, status
  coverage/coverage_map.csv      one row per 9903 code and HS chapter it touches
  coverage/unresolved.csv        codes whose product scope could not be determined
```

## coverage/explode_products.py

```text
Export the actual HS8 lines behind each surcharge code, not just a count per chapter.

build_coverage.py already resolves every 9903 code to its enumerated subheadings, but it
collapses them to n_products_in_chapter on the way out. Chapter-level counts are what forced
the earlier analysis to treat a whole chapter as treated when the median action names about
five lines in it, which is the dilution the HS8 panel exists to remove.

This re-runs the same resolution and keeps the codes.

Output
  coverage/product_lines.csv   one row per (9903 code, HS8 line)

Usage:  python3 coverage/explode_products.py      # from the repo root
```

## coverage/join_events.py

```text
Attach product and partner scope to each tariff event, then flag treated panel cells.

Scope is resolved by three routes, in order of reliability:
  1. the event cites a 9903 code that exists in the current schedule  -> use its coverage
  2. the event is Section 232, which names a material class           -> use the chapter rule
  3. the event is IEEPA, which is country-wide                        -> every chapter the partner ships

Route 1 fails for older Section 232 actions because the schedule has since renumbered those
headings, which is why route 2 exists.

Outputs
  coverage/event_scope.csv    one row per event and chapter, with partner scope and dates
  coverage/treated_cells.csv  one row per chapter, partner and month that sits inside a window
```

## coverage/rules.py

```text
Coverage rules for tariff actions that do not enumerate product lists.

Three authorities define scope three different ways:

  Section 301   enumerates HS8 subheadings in a U.S. note. Parsed directly; see build_coverage.py.
  Section 232   names a material or product class ("articles of aluminum"). The schedule itself
                states the core chapters: heading 9903.82.03 reads "Except for articles
                classifiable in chapters 72, 73, 74 or 76", which fixes the metals scope.
                Derivatives reach beyond those chapters and are listed separately.
  IEEPA         applies to a whole country with named carve-outs, so coverage is every chapter
                for that partner rather than a product list.

Each rule records where it comes from so it can be audited.
```

## coverage_share.py

```text
How much of a chapter does each tariff action actually touch?

The earlier analysis treated a whole HS chapter as treated whenever an action named
anything inside it. If an action names five HS8 lines out of four hundred, the chapter
series is mostly untreated trade and any real response is averaged away. That is the
dilution the HS8 panel exists to remove, and this measures it in dollars rather than
in line counts: a chapter can have few lines named and still be nearly fully covered
if those lines carry the value.

Reads the HS8 panel and coverage/product_lines.csv. Value shares are computed over a
reference window so they describe the trade mix before the tariffs, not after.

Usage:  python3 coverage_share.py [--ref 2017]
```

## decision_value.py

```text
Decision value: potential net benefit of acting on the forecasts, under assumed costs.

The decision: start qualifying an alternative supplier (act) or wait. Acting is right if the
targeted country's position in the product falls and does not come back by month 18 ("bad").
With an assumed qualification cost C and an assumed avoidable loss L when the outcome is bad,
acting pays when P(bad) >= t = C / L. This is a potential benefit under those assumptions, not a
measured saving. It assumes (i) the country-level outcome stands in for the loss to an importer
buying from that country, and (ii) qualifying at the decision date can still avoid that loss
(qualification takes days to about 18 months, see evidence/USE_EVIDENCE.md).

Net benefit (decision-curve analysis, Vickers and Elkin 2006) of a policy at threshold t, per
product:  NB(t) = share acted on that turned out bad - share acted on that did not x t / (1 - t).

Policies, all as probabilities of the bad outcome (non-recovery):
  model           logistic regression, the common model at every decision point (chosen for
                  consistency across points, not preregistered); P(bad) = 1 - P(recover) for the
                  stage-2 files, P(bad) directly for day one
  history         the training-years base rate; act on everything if >= t, else nothing
  history by vote at the ITC vote only, the base rate split by the vote
  share only      at the ITC vote only, the logistic model of the latest published share
  always / never  qualify for every product / for none (NB = 0)
Boosting and Cox are reported as sensitivity columns and do not enter any comparison.

Inference. The threshold grid is fixed in advance: 0.10 to 0.90 in steps of 0.05 (17 points).
Every policy is scored on the same 2,000 paired resamples of investigation groups. For each
baseline b and threshold t, D(b, t) = NB(model) - NB(b). Pointwise 90 percent intervals are the
5th and 95th percentiles of D. Simultaneous one-sided 90 percent lower bounds over all (b, t) use
the max-t method: with s(b, t) the bootstrap standard deviation of D, c is the 90th percentile of
max over (b, t) of (D* - D) / s, and the bound is D - c x s. The model is supported at t only if
its simultaneous bound is above zero against every baseline at t. All intervals hold the fitted
models fixed; they do not reflect refitting on other training data.

Usage:  python3 decision_value.py      # after prediction_test.py and prediction_stage2.py
```

## deflation_check.py

```text
Does the dollar ranking of unusual 2025 months survive deflating by import prices?

The appendix ("Dollars and quantity at the category level") ranks chapters by how far their
largest 2025 month sat above a line drawn from their own trend and seasonal pattern, the score of
slides/fig_units.py, repeated here. A dollar series mixes price and volume, so this recomputes the
score on dollars divided by the BLS import price index, for all imports (EIUIR) and for nonfuel
imports (EIUIREXFUELS), and counts how many of the top 10 chapters stay in the top 10: over every
product chapter with a full dollar history (96, the figure the appendix reports) and over the 63
that also have quantity data.

The two BLS series are fetched once from the public BLS API and kept in eda/bls_import_prices.csv,
so later runs work offline.

Writes deflation_check.csv.    Usage:  python3 deflation_check.py      # from the repo root
```

## eda_summary.py

```text
Small summary tables so the EDA notebook runs without the 1 GB panel cache.

panel/hs10 and panel/hs8 are gitignored and rebuilt by the acquisition scripts, which takes
about an hour. A teammate opening the notebook should not have to do that first, so the views
the notebook actually plots are written out here as CSVs small enough to commit.

Outputs
  eda/chapter_month.csv     chapter x month totals, value and quantity
  eda/chapter_partner.csv   chapter x partner totals, for the share-of-trade views
  eda/featured_series.csv   chapter x partner x month for the chapters the notebook features

Usage:  python3 eda_summary.py
```

## event_study.py

```text
Month-by-month version of the within-product test.

The three-bin test said the enumerated events had a +64.6% "pre" period, which is larger
than its own rush. A pre-period that big means the design is tracking something already in
motion, so the rush number cannot be read. Three bins cannot show what. This traces the
coefficient month by month around the announcement instead.

What a genuine rush looks like: flat before the announcement, a spike between announcement
and effective date, a dip after. What contamination looks like: already climbing well
before the announcement.

Contamination control: a cell-month is dropped if it sits inside the window of any OTHER
event, so one tariff's rush cannot be read as another's pre-period. China alone has
roughly twenty actions, so without this the windows overlap constantly.

Baseline is k in [-12,-7], i.e. a year to half a year before announcement.

Usage:  python3 event_study.py [--mech ENUMERATED] [--outcome lv|lq]
```

## events/build_301_lists.py

```text
Section 301 China Lists 1 to 3 as 8-digit product lists, dated at the month duties started.

The Federal Register publishes the List annexes as images, so the product codes cannot be read
from the notices. They come instead from the Harmonized Tariff Schedule's Chapter 99 notes, as
already parsed into coverage/product_lines.csv: heading 9903.88.01 (List 1, note 20(b)),
9903.88.02 (List 2, note 20(d)) and 9903.88.03 (List 3, note 20(f)). The notes are the 2026
edition, so codes renumbered since 2018 are missing; the match to the 2017 import data is logged
but not used as a filter.

Dates (first month duties were collected):
  List 1   July 6, 2018, 25 percent
  List 2   August 23, 2018, 25 percent
  List 3   September 24, 2018, 10 percent, raised to 25 percent from May 10, 2019
List 4A (September 1, 2019) is left out: its mapping here is incomplete, and its window runs into
China's COVID shutdown in early 2020, which would read as a tariff effect.

Products also under the 2018 Section 232 steel and aluminum duties (chapters 72, 73, 76) are
dropped, so China's rivals in the same product are not themselves newly taxed.

Usage:  python3 events/build_301_lists.py      # from the repo root
```

## events/build_release_calendar.py

```text
Census release date of each month's detailed trade data (FT-900), for "published by the decision".

Source: ALFRED (St. Louis Fed), vintage dates of series BOPGSTB, the trade balance published in each
FT-900 release (https://alfred.stlouisfed.org/series?seid=BOPGSTB, read 2026-11-07). Each release adds
one new data month, in order. ALFRED has no vintage for the March 2020 release; it was May 5, 2020
(BEA 20-21 / CB 20-66, archived on FRASER as bea_newsreleases_20200505). Gaps in the list are real:
no release in January 2019 or October 2025 (federal shutdowns), with catch-up releases after.
Months before October 2014 are assumed released on day 5 of month m + 2; no decision in the
project depends on them.

Usage:  python3 events/build_release_calendar.py      # writes census_release_calendar.csv
```

## events/fix_effective_dates.py

```text
Re-extract effective dates from document text.

The original parser took the first date near an effective-date phrase. Proclamations recite the
history of earlier rate changes using the same phrasing, so it often picked a date from years
earlier. Two rules fix almost all of it:

  1. an effective date cannot precede the announcement
  2. among the dates that survive, the operative one is the date the document repeats most often

Announcement dates are taken from the Federal Register signing_date where present, which is the
date the President actually signed, and from the publication date otherwise.
```

## events/harvest_adcvd.py

```text
Harvest antidumping and countervailing duty notices from the Federal Register.

The original harvest (harvest_fr.py) searched five Section 232/301/IEEPA phrases, so AD/CVD
notices were only caught incidentally: 155 documents in 2018 but 14 in 2025, which tracks the
search terms rather than Commerce's actual caseload. AD/CVD actions are the largest source of
product-specific, single-country tariff events available, and the project needs them because
21 Section 232/301/IEEPA events is too few to estimate repayment.

Strategy: pull the whole International Trade Administration index by year, which is where
AD/CVD lives, then fetch full text only for the notices whose titles mark a stage that starts
or changes duties. Investigations are kept and administrative reviews are dropped, because a
review adjusts the rate on an order that already exists while an investigation is what creates
the duty importers would front-load against.

Outputs
  events/adcvd_index.json   metadata for every ITA notice found
  events/raw/<doc>.txt      full text, shared with the existing harvest

Usage:  python3 events/harvest_adcvd.py      # from the repo root
```

## events/itc_audit.py

```text
Audit of the episodes events/itc_check.py classed as "verified negative".

For each one, re-reads the cached ITC notices behind the verdict and records the evidence: the
investigation numbers the notice covers, its issue date, and the sentence that names the country
and carries the negative vote. Flags any case where that sentence also mentions critical
circumstances (where "negative" can refer to retroactivity rather than injury) and any case where
the notice's investigation numbers do not match the case numbers in our preliminary notices.

Reads only the cache in events/raw/itc_cache/; run events/itc_check.py and adcvd_stacked.py
first.

Usage:  python3 events/itc_audit.py      # from the repo root
```

## events/itc_check.py

```text
Bounded check: which preliminaries with no linked order were negative at the ITC?

A preliminary whose case numbers appear in no harvested order notice is either a case that ended
without an order (usually a negative final injury vote at the ITC) or a harvest gap. This script
classifies each unlinked investigation group (product family x initiation month) by searching the
Federal Register API for (a) the ITC's final determination notice and (b) a Commerce order notice
the harvest missed. Responses are cached in events/raw/itc_cache/ so the result can be retraced.

Classes per group:
  verified order       a Commerce order notice exists, or the ITC final is affirmative for all
  verified negative    the ITC final determination is negative for every country named
  mixed                the ITC final is affirmative for some countries and negative for others
  unresolved           nothing found, or the text could not be read

Descriptive only: whether a case becomes an order is itself selected.

Usage:  python3 events/itc_check.py      # from the repo root
```

## events/parse_adcvd.py

```text
Parse antidumping and countervailing duty notices into tariff events with windows.

These are the largest source of product-specific, single-country tariff actions available,
and the project needs them: 21 Section 232/301/IEEPA events is too few to estimate repayment,
and their median announcement-to-effective window is days, which monthly data cannot resolve.
An AD/CVD case runs for months between becoming public and duties being collected.

What is extracted
  case number   A-570-053 / C-580-891. Letter is the programme, middle three digits
                Commerce's country code, so it links the stages of one case.
  stage         initiation -> preliminary -> final -> order. The preliminary determination
                is when duties start being collected, so it is the operative date.
  initiation    read out of the preliminary notice's own background section, because the
                initiation notice itself often falls outside the harvest window. Text is
                whitespace-normalised first: the source is hard-wrapped, which splits dates
                across lines and otherwise loses a third of them.
  scope         HTSUS numbers in the notice, truncated to HS8 to match the panel.
  country       from the title, which reads "<Product> From <Country>: <Action>". Titles
                naming several countries are split, since each is a separate treatment.

Outputs
  events/adcvd_events.csv     one row per document: case, stage, country, dates, window
  events/adcvd_products.csv   one row per document and HS8 line

Usage:  python3 events/parse_adcvd.py      # from the repo root
```

## events/parse_margins.py

```text
Preliminary duty rate per AD/CVD preliminary notice, read from the notice's own rate table.

Commerce publishes each preliminary determination with a table of company rates in percent: an
estimated weighted-average dumping margin (AD) or an ad valorem subsidy rate (CVD). Most tables
end with an "All Others" row, the rate for exporters not individually examined; non-market
economy cases instead carry a country-wide entity rate (for example "China-wide entity"). That
row is the rate most of the country's trade faces, so it is the feature:

  rate      All Others row if present, else the country-wide entity row, else the largest rate
            in the table
  rate_src  which of the three it came from; blank if no table was found
  rate_max  the largest company rate in the table(s)

Read from the fixed-width text the Federal Register serves (events/raw/), where each table row
ends in its rate(s). Page markers and footnote markers are ignored. Rates above 500 percent are
kept only if they sit on an All Others or entity row, since a bare number that large in a table is
more often a page number than a rate.

Usage:  python3 events/parse_margins.py      # from the repo root
```

## feature_ladder.py

```text
Feature ladder at month 4: where does the forecast's information come from? (docs/SCOPE.md, item 1)

The month-4 model is retrained five times, each time with one more group of inputs, and every version
is scored the same way. Everything else is exactly as in prediction_landmark.py: one model pooled
over checkpoints 3 to 14, the same forward-chained test years, the same rule for which training
cases are allowed, the same tuning grids and models, each case counted once per checkpoint. Only the
inputs change. Rules fixed before any step was run (2026-11-10); every step is reported whatever it
shows; results are exploratory, because the held-out years have been looked at before.

Steps (each adds to the one before)
  a  case facts known by the decision date: pre-case share, its trend, pre-case size (log value),
     market concentration, number of rival suppliers, duty rate and its missing flag, critical
     circumstances, both kinds of duty, China
  b  + the latest published share over its pre-case level
  c  + how the fall has gone: month of the fall, months since, depth, recent slope, share of months
     with no imports, pre-case rush, unit-value change and its missing flag.  This is the current
     model; the script stops unless step c reproduces prediction_landmark_heldout.csv exactly.
  d  + other countries' pickup, from all countries' imports of the product (including countries left
     out of the comparison group), comparing the visible months after the duty (0 to kv) with the
     same calendar months a year earlier (so seasons cancel):
       rival_growth  log change in every other country's imports of the product
       total_growth  log change in the product's total U.S. imports
     Together they say whether the lost volume moved to other countries or disappeared.
  e  + dutied_rivals: the share of rivals' pre-case imports (months -18 to -7) that came from
     countries already facing their own duty on the same product by the decision date (their first
     preliminary published by the end of month 3, products named at that preliminary)
  Every step also carries the checkpoint inputs the pooled model needs (the month L and the three
  ITC-vote indicators). At month 4 the vote is never public, so those are constant there.

Scoring at month 4 (held-out years 2020 to 2025)
  main     share of reviewed relationships not back by month 18, reviewing 20 percent of each
           calendar month's queue (review_queue.py's rule: ties share reviews, each relationship
           counts once); also the share of all persistent declines reviewed
  others   Brier score and AUC, each case weighted once (as prediction_landmark.py)
  ranges   90 percent, from 1,000 resamples of investigation groups, fitted models held fixed;
           differences against the latest-share ranking and against the previous step

Writes feature_ladder.csv and feature_ladder_heldout.csv (every step's held-out predictions at
every checkpoint, for items 3, 4 and 6).

Limit: duties from before 2015 are not in the notice table, so step e misses rivals under older orders.

Usage:  python3 feature_ladder.py      # after prediction_landmark.py
```

## harvest_hs10.py

```text
Census intltrade imports, HS10 x partner x month, 2015 onward.

HS10 is the finest published level and nests exactly under the HS8 lines the
tariff orders are written at, so product matching is exact rather than
approximate. GEN_QY1_MO is carried because it is only populated at this level
and, unlike the weight fields, it counts truck and rail arrivals.

One API call per month, each checkpointed to its own gzip, so a restart skips
whatever is already on disk. Written atomically via .tmp + os.replace so an
interrupted run never leaves a half file that looks cached.

Usage:  CK=<census key> python3 harvest_hs10.py
```

## itc_compare.py

```text
Aftermath for AD/CVD cases that became orders against cases the ITC voted negative.

Uses the stacks and estimator from adcvd_stacked.py, split by what happened at the final stage:
  order      the episode's case numbers appear in a harvested order notice, or events/itc_check.py
             found an order notice or an affirmative ITC final for that country
  negative   events/itc_check.py found a negative ITC final determination for that country
Unresolved episodes are left out. Preliminary dated before mid-2025 and full 18-month follow-up.

Descriptive only. Whether a case ends in an order is decided by the ITC on the record, which
includes the import trend itself, so the two groups are selected, not randomly assigned.

Usage:  python3 itc_compare.py      # from the repo root
```

## model_calibration.py

```text
When can the month-4 forecast be trusted? (docs/SCOPE.md, item 3)

Held-out month-4 predictions of the forecast (boosting, prediction_landmark_heldout.csv), unchanged.
Fixed before running (2026-11-10); exploratory, because the held-out years have been looked at before.
Every measure weights each case once, as prediction_landmark.py does.

  reliability   predicted chance of coming back, in five bins of equal weight, against what happened;
                calibration in the large (mean predicted against realized) and calibration slope
                (logistic regression of the outcome on the log-odds of the prediction; 1 is ideal)
  errors        Brier score of the forecast and of the historical rate, and AUC, by kind of product
                (HS section, groups with at least 30 relationships) and by how much the country sold
                before the case (thirds of pre-case value); also by test year
  largest case  all of the above with and without the largest investigation group (2024 aluminum
                extrusions, nearly half the month-4 relationships)
  ranges        90 percent, from 1,000 resamples of investigation groups

Writes model_calibration.csv, model_errors.csv and slides/fig/23_reliability.png.

Usage:  python3 model_calibration.py      # after prediction_landmark.py
```

## model_explain.py

```text
Why does the month-4 forecast flag what it flags? (docs/SCOPE.md, item 2)

The forecast is the boosting model of prediction_landmark.py, unchanged. Fixed before running
(2026-11-10); exploratory, because the held-out years have been looked at before.

  importance    permutation importance on held-out data: for each test year, the model trained for
                that year is scored on that year's month-4 relationships with one input shuffled
                (20 shuffles); importance = how much worse the Brier score gets, pooled over years,
                each case weighted once. 90 percent ranges from 1,000 resamples of investigation
                groups of the per-relationship change. The refit models must reproduce
                prediction_landmark_heldout.csv, or the script stops.
  dependence    partial dependence of the chance of coming back on the most important inputs and on
                the duty rate, from one boosting model fitted on all cases (tuned the same way),
                evaluated on the month-4 rows.

Inputs that move together (the latest share, the depth of the fall and the months since it) share
credit under permutation, so a small importance for one of them does not mean the information is
unused.

Writes model_importance.csv, model_partial_dependence.csv and slides/fig/22_model_explain.png.

Usage:  python3 model_explain.py      # after prediction_landmark.py
```

## model_recalibration.py

```text
Can the month-4 forecast's probabilities be fixed using earlier years only? (calibration fix)

model_calibration.py found the forecast too pessimistic at month 4: it predicts a 19 percent chance of
coming back on average where 26 percent came back, most of the gap in the middle of the range. This
recalibrates it without touching the test years. Fixed before running (2026-11-15); exploratory,
because the held-out years have been looked at before.

  method      for each test year, the boosting model of prediction_landmark.py (same training cases,
              same tuning, same settings) makes out-of-fold predictions on its own training cases
              (grouped 5-fold by investigation group, the number of trees fixed at the value tuned on
              the whole training set). A logistic recalibration (Platt scaling: the outcome on the
              log-odds of the prediction, each case weighted once) is fitted to those out-of-fold
              predictions and applied to the test year's predictions.
              primary    fitted on the training cases' month-4 rows
              secondary  fitted on all checkpoints 3 to 14 (reported, not used to choose)
  scored      at month 4, held out 2020 to 2025: mean predicted against realized, calibration slope,
              Brier score (and its change from the raw model), AUC, reliability in five bins, and the
              same by thirds of pre-case size; 90 percent ranges from 1,000 resamples of
              investigation groups. The recalibration preserves the order of predictions within a test
              year, and every review queue lies within one year, so the review ranking cannot change.
              AUC, which pools all years, can move slightly, because each year gets its own
              recalibration. (Corrected after the first run, which showed AUC 0.795 to 0.790.)
  check       the raw predictions must reproduce prediction_landmark_heldout.csv, or the script stops.

Writes model_recalibration.csv, model_recalibration_heldout.csv and slides/fig/24_recalibration.png.

Usage:  python3 model_recalibration.py      # after prediction_landmark.py
```

## pharma_mix.py

```text
Why pharmaceuticals look opposite on dollars and on quantity.

chapter_quantity.py ranks chapter 30 at 2.86 on dollars and -0.33 on quantity, which reads at
first like the dollar signal was an illusion. It is not. The surge is real; it is a shift in
product mix rather than in tonnage, and tonnage cannot see it.

This matters beyond pharmaceuticals. Cocoa shows that dollars confuse a price rise with a volume
surge. Pharmaceuticals shows that quantity confuses a mix shift with no surge at all. Neither
measure is safe at chapter level, which is the same argument as the coverage dilution: one HS8
line is one product with one unit, and both problems go away there.

Usage:  python3 pharma_mix.py      # from the repo root
```

## prediction_landmark.py

```text
A forecast that updates every month: how soon can a sourcing team tell which products come back?

prediction_stage2.py scores two fixed moments. A team sees new trade data every month, so this
re-scores the question at every landmark month L = 3, 4, ..., 14 after the duty starts.

At landmark L (data visible through k = L - 2, the Census release lag, or earlier when a release
slipped past month L, as in the 2025 shutdown; census_release_calendar.csv), the eligible products are
those whose fall is already visible (fall month <= L - 2) and that are not yet visibly back (no
completed three-month run at or above the pre-case share by L - 2). Target: back by month 18.
Comparison panels, outcomes and products are the decision-time ones (build_decision_stacks.py).

Features at L, all public by then:
  day one        pre-case share, trend, size, rival count and concentration; duty rate from notices
                 published by L, missing flag; critical circumstances; both AD and CVD opened by then; China
  trade so far   month of the fall, months since it, deepest and latest smoothed share (ratio to
                 pre-case), change in the smoothed share over the last three visible months, share
                 of months with no trade, share in k -6..-1, unit-value change against rivals
  ITC vote       duty confirmed / lifted / not yet public by the decision date (the last day
                 before landmark month L, the same date used for notices)
  landmark       L itself
One model pools all landmarks (a "landmark supermodel"); each product-landmark row is weighted
1 / (eligible products in its case at that landmark), so each case counts once at each landmark.
At the fall itself the deepest and latest smoothed share are equal by construction, and since_fall
is L - 2 - k_fall, so those coefficients cannot be read separately.

Validation: forward-chaining by year of k = 0, training only on cases whose month 18 was published
before the test year (as prediction_stage2.py). Models: L2 logistic regression, shallow gradient
boosting, and a benchmark using only the latest published share and the landmark month (what a team
could read off the data without a model). Baseline at each landmark: the training cases' recovery rate among products eligible at
that same landmark. Scored per landmark (Brier, AUC) with 90 percent intervals from 1,000 resamples
of investigation groups, holding fitted models fixed.

Usage:  python3 prediction_landmark.py      # after build_decision_stacks.py
```

## prediction_stage2.py

```text
Second decision point: once a targeted product has visibly fallen, can we tell whether it recovers?

prediction_test.py asks the hardest version of the question, on the day the duty starts, and
finds no reliable gain over the historical rates. A sourcing team gets two later looks: when the
fall shows up in the published trade data, and when the ITC votes on the final injury
determination a few months later. This script tests both.

Population: targeted product-country pairs from recovery_benchmark.py (20 percent fall rule,
complete 18-month follow-up) whose position fell within k = 0..6.
Target: recovered = back at or above the pre-case share for three months running by k = 18.

Decision points, each with the trade data a team could have seen (Census publishes a month's
trade about five weeks after it ends, so at decision month M the last visible month is usually
M - 2; exact release dates are in census_release_calendar.csv, events/build_release_calendar.py):
  fall   decision month: the month Census released month k_fall (k_fall + 2, later when a release
         slipped, as in the 2025 shutdown), the first month the fall is visible. Visible data through
         k_fall. Case facts from notices published by then (the ITC vote is not yet known).
  ITC    decision month = month of the final-stage notice: the ITC's negative final
         determination, or the Commerce order that follows an affirmative vote. Visible data
         through the last month Census had released on or before that notice's date. Only pairs whose fall is visible by then and that are not yet
         visibly back. Episodes whose final stage is unresolved, or whose first order notice in
         the harvest comes after k = 12 (a later continuation notice, not the order itself), are
         left out.

Information sets compared on the ITC population:
  day 0      the 10 facts prediction_test.py uses (pre-case structure, preliminary rate, case type)
  + trade    adds what the published data show by the decision: month of the fall, deepest
             smoothed share so far and the latest one (both as a ratio to the pre-case level),
             share of months with no trade since the duty, the share in k -6..-1 against the
             pre-case level (any rush before the duty), and the targeted exporter's change in
             import unit value against rivals (same product, one reporting unit), with a
             missing flag
  + vote     adds whether the ITC found no injury

Baselines: the historical recovery rate in the training cases (same population), and the same
rate split by the ITC vote.
Models (on the fullest information set): L2 logistic regression; shallow gradient boosting
(depth 2, learning rate 0.05, strong L2); penalized Cox proportional hazards on months to
recovery with delayed entry at the decision, converted to a probability of recovery by k = 18.
Hyperparameters by 5-fold cross-validation grouped by investigation group inside the training
cases.
Validation as prediction_test.py: forward-chaining by year of k = 0; training cases only once
their month 18 had been published before the test year began. Every score episode-weighted.
Brier gains carry 90 percent intervals from 2,000 resamples of investigation groups.

Descriptive and predictive only: the ITC's vote rests on the import record itself.

Usage:  python3 prediction_stage2.py
```

## prediction_test.py

```text
One held-out test: can facts known at the preliminary beat the historical recovery benchmark?

Target, per targeted product-country pair with complete follow-up (recovery_benchmark.py):
  bad = fell by 20 percent or more and had not recovered by k = 18 (categories "not recovered"
  or "exited"); good = "no fall" or "recovered".
Features, all known by the preliminary determination (k = 0), none from later months:
  from the raw panel, every country trading the product in k -18..-7: the targeted country's
  share, its monthly share trend (slope), log of its pre-case value, number of rival countries
  (log), concentration of shares (HHI); from the notices published by k = 0 only: affirmative
  critical circumstances and the preliminary duty rate (sum of the AD and CVD all-others or
  country-wide rates, events/parse_margins.py; log of one plus the rate) with a missing
  indicator; whether both AD and CVD investigations had been opened by the decision (RL.both_programs_known); China as the
  targeted country.
Model: L2-regularized logistic regression on standardized features, C chosen by grouped
cross-validation inside the training years.
Validation: forward-chaining by year of k = 0. Training uses only episodes whose month k = 18
had been released by Census before the test year began, so every training label was observable
at test time.
Baseline: the benchmark, i.e. the episode-weighted share of bad outcomes in those training
episodes. Every score is episode-weighted, as in recovery_benchmark.py.
Scores: Brier score (lower is better), log loss, and AUC. The test passes only if the model's
pooled Brier is below the benchmark's.

Usage:  python3 prediction_test.py
```

## q3_absorbers.py

```text
When a tariff displaces volume from one origin, which origins absorb it?

This decides the project's stakeholder. If a few named origins absorb the volume, there is a
lane story: same US port, different ocean leg, different transit time and service string, and
carriers and forwarders plan exactly that. If absorption is spread thinly across dozens of
origins, no single lane changes enough to matter and the exposure sits with suppliers and
lenders instead.

For each AD/CVD case, within the products it names:
  share(origin) before = that origin's share of the product basket, 12 months pre-initiation
  share(origin) after  = the same, 12 months from the preliminary determination
  delta                = after - before, so the treated origin's loss is spread over the rest

Concentration of the positive deltas is the whole question:
  top1, top3   fraction of all gains taken by the largest one and three absorbers
  1/HHI        effective number of absorbers. Near 1 means one country took it, near 20
               means it dissolved into the background.

Paired with the usual 24 month placebo, because share churn happens anyway. The placebo is the
benchmark for "how concentrated do share shifts look when nothing happened".

Usage:  python3 q3_absorbers.py [--h 12]
```

## recovery_benchmark.py

```text
Recovery benchmark: after an AD/CVD preliminary, what usually happens to the targeted supplier?

For a sourcing team buying one product from a country just named in a preliminary AD/CVD
determination, the useful historical facts are: how often the supplier's position falls, how often
it comes back within 18 months, how long that takes, and how often trade stops altogether.

Unit: one targeted product-country pair in one episode (stacks from adcvd_stacked.py).
Position: the targeted country's share of the product's imports among the stack's countries
(targeted plus eligible rivals), smoothed as a 3-month trailing mean. A month in which the targeted
country does not trade but rivals do counts as a share of zero; a month in which none of the stack's
countries trades has no share and is missing (the 3-month mean needs three real months). A pair with
no measurable month in k = 0..6 gets no label.
Benchmark: mean share over k = -18..-13, which precedes the case's initiation for all but one of
the 502 episodes (adcvd_stacked.py prints the count).

Categories, mutually exclusive, each pair in exactly one:
  no fall        smoothed share never below (1 - FALL) x benchmark in k = 0..6
  recovered      fell, then smoothed share at or above the benchmark for 3 consecutive months by
                 k = 18; recovery time is the first month of that run, counted from the fall
  not recovered  fell, not recovered by 18, traded at least once in k = 13..18
  exited         fell, not recovered, no trade in any month of k = 13..18
Recovered pairs that then stop trading in k = 13..18 are counted separately; they stay
"recovered" (ever recovered within 18 months).

Follow-up: pairs whose 18 months run past the data end are left out of the four-category shares
whatever their outcome so far, and censored at their last observed month for the Kaplan-Meier
estimate. The Kaplan-Meier clock starts at the month of the fall, and events are observed only up
to k = 18 after the duty.
Weighting: each episode counts once (each of its pairs weighted 1 / pairs in the episode). By pair,
the ten largest episodes, all 2024 aluminum extrusions cases, hold 30 percent of the pairs.
Uncertainty: 1,000 bootstrap draws of investigation groups.
Placebo: the same on stacks dated 24 months earlier.
Benchmark evaluation: for each year Y, category rates from episodes whose 18 months had finished
before Y began, scored against the realised categories of episodes with k = 0 in Y (multiclass
Brier score), against the rates from all years (in-sample, optimistic) and a uniform guess.

Usage:  python3 recovery_benchmark.py [--fall 0.2]
```

## recovery_by_final_stage.py

```text
Recovery categories (recovery_benchmark.py) split by how the case ended at the final stage.

The ITC's final injury vote comes a few months after the preliminary and is public, so it is a
second point at which a sourcing team can update. Final stage per episode as in
itc_compare.py: order (linked to an order notice, or verified order) or negative (verified
negative ITC final for that country). Episode-weighted, 90 percent bootstrap intervals over
investigation groups. Fall threshold 20 percent.

Usage:  python3 recovery_by_final_stage.py      # after itc_compare.py has written its log
```

## recovery_lib.py

```text
Shared pieces for the recovery outcomes and the at-the-fall features, so AD/CVD cases and the
Section 301 lists go through exactly the same rules.

categorize()   per targeted product: pre-case share, month of the fall, month of recovery, and the
               four outcome categories, for any horizon H (recovery_benchmark.py uses H = 18).
               Run on panel/adcvd_stacks_real.parquet with H = 18 it reproduces
               recovery_pairs_real_fall20.csv (checked in sec301_benchmark.py).
build_stack()  a stack in the format of adcvd_stacked.py for one targeted country and a product list
fall_features() what the published data show when the fall first becomes visible (k_fall + 2),
               the same definitions as prediction_stage2.py
```

## review_queue.py

```text
A review queue for a sourcing analyst: which tariff-hit product-country relationships to look at first?

Proposed use (not validated with users). A sourcing analyst can review only some of the product-country
relationships hit by antidumping or countervailing duties, and wants to start with those whose trade
decline is likely to persist. The output ranks relationships for review alongside the company's own
supplier information. It predicts the supplier country's recovery in the product (its share of U.S.
imports of that product), not whether any one supplier fails.

Rules, fixed before the results were seen (2026-11-09)

  checkpoint   month 4 after the duty starts (landmark L = 4 of prediction_landmark.py). Data visible
               through month 2, or less when a Census release slipped (census_release_calendar.csv).
  population   the landmark model's eligible products at L = 4: the fall is already visible (share
               below four-fifths of its pre-case level, smoothed, by the last visible month) and the
               product has not visibly come back. Products that never fell, or fell and were already
               back by then, are not in the queue.
  queue        one queue per decision month (the calendar month k = 4): only relationships at their
               month-4 checkpoint in that same month are ranked against each other. No later case
               enters an earlier queue.
  predictions  the held-out predictions in prediction_landmark_heldout.csv, unchanged: forward-chained
               by year of k = 0, each model trained only on cases whose month 18 was published before
               the test year, features limited to what was published by the decision date.
  target       remains down: not back at or above the pre-case share for three months running by
               month 18 (y = 0 in the held-out file).
  rankings     forecast   gradient boosting, the month-4 model of Table 3 (primary); logistic is
                          reported alongside it, not used to choose.
               latest     the latest published share over its pre-case level, lowest first: what an
                          analyst reads off Census data without a model (the landmark "share only"
                          benchmark is a monotone function of it at a fixed landmark).
               history    the training cases' recovery rate at month 4. It is one number for every
                          relationship in a queue, so ranking by it is a random order: its expected
                          result is the queue's own rate of persistent declines.
  capacity     20 percent of each queue (primary); 10 and 30 percent as sensitivity checks. These
               are assumed review capacities, not documented company budgets. A queue of n gets
               c x n reviews; where the boundary falls inside one relationship, that relationship
               counts as reviewed in part (the expected value of a random tie-break).
  ties         relationships with equal scores share the remaining capacity equally (a block of
               k tied relationships with m reviews left gives each m / k). This matters for the
               latest share, where several relationships can sit at exactly zero.
  weighting    each relationship counts once: it is the unit an analyst reviews. One case naming
               many products can dominate a queue, so intervals resample whole investigation groups.
               A case-weighted version (each case's eligible products share one unit) is reported as
               a check, and so (added after the first results) is a run without the largest
               investigation group, which holds nearly half the relationships.
  measures     precision: share of reviewed relationships that remain down. Capture: share of all
               persistent declines in the queues that were reviewed. Differences between rankings
               with 90 percent intervals from 1,000 resamples of investigation groups (whole groups
               drawn with replacement, queues rebuilt, fitted predictions held fixed).
  decision     the forecast replaces the latest share as the ranking only if, at 20 percent capacity,
               its precision is higher with the 90 percent interval above zero. Otherwise the latest
               share is the ranking, and the historical rate is reported as the benchmark it is.

Writes review_queue_eval.csv and review_queue_watchlist.csv (every held-out month-4 queue, ranked
by the chosen method; the report shows one month as an example).

Usage:  python3 review_queue.py      # after prediction_landmark.py
```

## review_queue_curves.py

```text
Does the review-queue result depend on the assumed capacity or on month 4? (docs/SCOPE.md, items 4 and 6)

Item 4, capacity curve. The month-4 queues of review_queue.py, scored at every capacity from 5 to 50
percent in steps of 5. Item 6, later checkpoints. The same queue rule at months 6 and 8 as a
secondary check; month 4 stays the main decision point.

Fixed before running (2026-11-10), as in review_queue.py: held-out predictions from
prediction_landmark_heldout.csv, unchanged; one queue per calendar month (the month of the
checkpoint), ranking only relationships at that checkpoint in that month; ties share reviews equally;
each relationship counts once; rankings: the forecast (boosting, named in advance), logistic
(reported, not used to choose), the latest published share (lowest first) and the historical rate (one
number per month, so a random order). Main measure: share of reviewed relationships not back by
month 18; also the share of all persistent declines reviewed, and the most any order could reach.
90 percent ranges from 1,000 resamples of investigation groups, fitted models held fixed. At months
6 and 8 the eligible relationships are those still falling and not yet back at that month, so the
three checkpoints are not compared on the same products.

Writes review_queue_capacity.csv, review_queue_checkpoints.csv and slides/fig/21_capacity_curve.png.
Results are exploratory: the held-out years have been looked at before.

Usage:  python3 review_queue_curves.py      # after prediction_landmark.py and review_queue.py
```

## sec301_benchmark.py

```text
Section 301 Lists 1 to 3: what happened to China's position in each taxed product.

Same design as the AD/CVD work: for each list, a stack of its products with China and every rival
country that traded them in k -18..-7, months with no trade kept as zeros, reference k -18..-13.
Rivals named on the same product by an AD/CVD case with k = 0 within 36 months before to 18 after
are left out, and so are products where China itself had such a case, so the comparison isolates
Section 301. Fake date: the same lists 24 months earlier, cohort rebuilt from its own window. A
third, strict sample uses only AD/CVD cases whose first preliminary was published on or before the
list's start date (exact dates) for those exclusions,
so the in-time transfer test (sec301_transfer_test.py, test B) selects nothing on later cases.

Horizon: every window stops at January 2020, before China's COVID shutdown, which would otherwise
read as a tariff effect. List 3 (September 2018) then has 16 months, so the outcomes use H = 16
throughout, with "stopped trading" meaning no imports in months 11 to 16, and the AD/CVD rates are
recomputed at the same horizon for the comparison.

Unit: one product. Each list is one tariff date, so there is no honest standard error for the
list-level effect; the shares carry 90 percent intervals from resampling 2-digit chapters, which
covers product heterogeneity but not the common shock of each list date.

First, a check that recovery_lib.categorize reproduces recovery_pairs_real_fall20.csv on the AD/CVD
stacks at H = 18: same category, pre-case share, fall month, recovery month and follow-up for every
pair. Both share the calendar-month rule, so this checks the shared code, not the rule itself.

Usage:  python3 sec301_benchmark.py
```

## sec301_transfer_test.py

```text
Does the at-the-fall recovery model learned on AD/CVD cases transfer to Section 301?

Population in both domains: targeted products that fell (sec301_benchmark.py, horizon H = 16,
complete follow-up). Target: back at or above the pre-case share for three months running by
k = 16. Decision: the month the fall first shows in published data (k_fall + 2, later when a Census
release slipped; census_release_calendar.csv).

Both domains use decision-time comparison panels: AD/CVD from build_decision_stacks.py, Section 301
from the strict sample of sec301_benchmark.py (rivals left out only for cases already started).

Features, as prediction_stage2.py at the fall, minus three that cannot transfer: China (always 1
under Section 301), both AD and CVD, and critical circumstances (always 0). Kept: pre-case share,
trend, size, rival count and concentration (every country trading in k -18..-7), the duty rate
known at the decision (AD/CVD: notices published by then; Section 301: 25 percent for Lists 1 and
2, 10 percent for List 3 until the May 2019 increase is public, 25 after) with a missing flag, and
the trade so far: month of the fall, deepest and latest smoothed share, months with no trade,
share in k -6..-1, unit-value change against rivals.

Tests:
  A  regime transfer     train on every AD/CVD case, score Section 301. Not a forecast anyone
                         could have made in 2018, since most AD/CVD training cases come later; it
                         asks whether the relationship carries across laws.
  B  strict, in time     train only on AD/CVD cases whose month 16 was published before the first
                         Section 301 decision (September 2018), score Section 301.
  C  strict, reverse     train on Section 301 (published by March 2020), score AD/CVD cases whose
                         fall decision comes after that.
  D, E  pooling         AD/CVD cases published by March 2020 forecast AD/CVD cases decided from
                         April 2020, without (D) and with (E) Section 301 added to the training set
                         (whose labels are published by March 2020); hyperparameters for E are chosen
                         by cross-validation on the pooled set; the paired E minus D Brier difference
                         carries a 90 percent interval from resampling investigation groups
  ref in-domain         Section 301 scored by a model trained on other Section 301 chapters
                         (5-fold, grouped by chapter): how predictable it is from its own data.
Baselines: the training domain's historical recovery rate (what you would use with no model) and,
for reference only, the target domain's own rate, which no one knows in advance.
Weights: AD/CVD products weighted 1 / products in the case, Section 301 products 1 each.
Intervals: 90 percent, 2,000 resamples of chapters (Section 301) or investigation groups (AD/CVD)
of the scored products, with the fitted models held fixed: they cover which products are scored,
not how the model would change with other training cases or other tariff dates.

Usage:  python3 sec301_transfer_test.py      # after sec301_benchmark.py
```

## slides/build_deck2b.py

```text
Build the Presentation 2 resubmission (v2) as an editable .pptx.

Same deck as slides/build_deck2.py (which built the version submitted on 2026-11-06 and is kept
unchanged), with the results replaced by the November corrections in FINAL_REPORT.md:

  slide 5   new: the public evidence that importers make this decision
  slide 6   method now says months with no trade count as zero, and how many notices were read
  slide 6   the aftermath split by whether the duty became permanent (fig 12), replacing "the
            targeted country does not bounce back" and its "42 percent above its usual level"
  slide 7   new: what happened to each targeted product within 18 months (fig 14)
  slide 9   notes: the antidumping result points the same way in physical quantity
  slide 10  discussion rewritten to the corrected numbers
  slide 11  checks: quantity, and the 31 notices removed
  slide 12  the monthly forecast (fig 19), with the latest-share baseline on the slide
  slide 13  the month-4 review queue (fig 20) and the next step; the lookup stays in the final deck

Every number traces to FINAL_REPORT.md. Style and helpers are build_deck2.py's, unchanged.

Usage:  python3 slides/build_deck2b.py      # from the repo root
```

## slides/build_deck_final.py

```text
Build the final presentation as an editable .pptx.

Built from slides/build_deck2b.py (the Presentation 2 resubmission draft) with its helpers and
style unchanged. Adds the three-questions slide (Kylie: "Analytic problem is given but lacks
clarity"), the time-to-recovery curve (fig 13), the held-out results at three decision points (fig
15), and a closing
slide on what each question's answer is. Every number traces to FINAL_REPORT.md and the CSVs
written by the scripts it cites.

Usage:  python3 slides/build_deck_final.py      # from the repo root
```

## slides/fig_copper_split.py

```text
Copper, split into the part the duty taxed and the part it did not.

The total copper line (01_context.png) rushes before the 2025 Section 232 duty, crashes, then
climbs back to new highs, which reads as "borrowed": the business came back. It did not, for the
part that was taxed. Proclamation 10962 taxed semi-finished copper (headings 7407 to 7413) and,
in paragraph 8, left refined cathodes (74031100) untaxed as an input material. Split that way,
the taxed series falls to about half its old level and stays there; the untaxed series is what
recovers.

One product and one action, with no placebo, so this is an illustration of the question rather
than a result. The monthly lines are drawn in full rather than as window averages so the shape is
visible and nothing depends on the chosen windows. Kilogram-reported rows only, as in
copper_split.py, which prints the window averages quoted in REPORT1.md.

Usage:  python3 slides/fig_copper_split.py      # from the repo root
```

## slides/fig_event.py

```text
Figure: what happens to the named country's imports around an antidumping case.

k = 0 is the month duties start being collected; the baseline is k in [-18,-13]. Product-month
and product-origin fixed effects mean each point is the named country relative to other suppliers
of the same product in the same month, not a level series.

The shape matters more than any single number, and it is not the one we expected. Imports from
the named country are already about 37 percent above baseline a year out and still climbing to
k = -5. They then fall steadily, cross baseline two months after duties start, and stay there.

Two readings follow. There is no rush: the decline begins long before the duty, which fits the
fact that these duties can be applied retroactively to the initiation notice, so buying ahead
buys nothing. And the elevated pre-period is not noise, it is part of the story, because a surge
in imports is often what triggers the petition in the first place.

Usage:  python3 slides/fig_event.py      # from the repo root
```

## slides/fig_sankey.py

```text
Sankey: what a tariff action actually names inside the chapter it touches.

Kylie Bemis suggested this in the presentation on 2026-10-16, to show "what these different
chapters are and what things are actually affected". Copper is the right case because it is the
example the deck already uses, and because the answer is counter-intuitive: the 50 percent duty
missed two thirds of the chapter by value.

The split comes from Proclamation 10962 itself, not from a parsed annex. Paragraph 1 applies the
duty to "semi-finished copper products and intensive copper derivative products, as set forth in
the Annex". Paragraph 8 handles "copper input materials and high-quality copper scrap"
separately, under the Defense Production Act, with no tariff. The annex table is not in the
Federal Register text we hold, so headings are assigned to those two categories by their standard
meaning and the figure says so. Treat the shares as close, not exact.

Usage:  python3 slides/fig_sankey.py      # from the repo root
```

## slides/fig_stacked.py

```text
Figures for the corrected AD/CVD results (stacked design, November 2026).

  12_order_vs_negative.png  targeted country vs rival suppliers, month by month, for cases that
                            became permanent orders, cases the ITC voted down, and the fake date
  13_recovery_km.png        of products whose position fell, the share back at the pre-case level
                            by months since the fall, real cases vs the fake date
  14_outcomes.png           what happened to each targeted product within 18 months, real vs fake

Palette is the deck's own: red for the focal series, ink for the comparison, grey dashed for the
fake-date baseline. Every line is labelled directly (grey is low-contrast on white, so it never
carries identity by colour alone).

Usage:  python3 slides/fig_stacked.py      # from the repo root, after adcvd_stacked.py,
                                           # itc_compare.py and recovery_benchmark.py
```

## slides/fig_units.py

```text
Figure: the same chapters, ranked on dollars and on quantity.

Kylie Bemis asked for Fig. 4 in kilograms. The honest answer is not a redrawn ranking but a
comparison, because neither measure is right on its own: dollars confuse a price rise with a
volume surge (cocoa), quantity confuses a mix shift with no surge at all (pharmaceuticals).
Showing both at once is the finding.

Deliberately no colour split by "is this a tariff story". That was a judgement call in the
presentation version and it did not hold up when she looked at it. Interpretation belongs in
the text, where it can be hedged; the figure shows what was measured.

Usage:  python3 slides/fig_units.py      # from the repo root
```

## slides/speech.py

```text
The words to actually say, one entry per talk slide.

Single source of truth. build_deck.py puts these into the speaker notes and write_script.py
writes slides/SCRIPT.md from them, so the deck and the script cannot drift apart. Earlier they
were two copies and they did drift: the notes pointed at a 9:15 script that was 9:03.

Written to be spoken, not read. Contractions throughout, because nobody says "it does not wait
for July" out loud. Every figure is named by number because the communication rubric asks for
figures to be referenced and interpreted, and in a talk that is something you say.
```

## within_product_test.py

```text
Did treated imports rise between announcement and effective date, relative to the
same product from origins that were not tariffed?

This is the comparison the chapter-level work could not make. A commodity price shock
moves every origin of a product together. A tariff moves one origin relative to the
others. So the control for "aluminum from Canada in March 2018" is aluminum from every
origin not tariffed, in March 2018.

Two-way fixed effects by iterative demeaning:
  product x month   absorbs anything that moved a product globally that month
  product x origin  absorbs the fact that some origins are simply bigger suppliers

Terms, all relative to the same product from untreated origins in the same month:
  pre    three months before announcement. Should be flat. This is the placebo: if it
         is large, the design is picking up trends rather than the tariff.
  rush   announcement month through effective month, when buying ahead can happen
  post   six months after it took effect, where payback would show up

On action_kind: the classifier labels most real impositions SCOPE_CHANGE, including the
original Section 301 action and the 2025 reciprocal tariffs. Filtering to IMPOSE left two
events. So direction is taken the other way round, by excluding the actions that plainly
reduce exposure (REVOKE, DECREASE, SUSPEND) and keeping the rest.

Usage:  python3 within_product_test.py [--outcome lv|lq]
```
