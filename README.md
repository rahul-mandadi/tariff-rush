# tariff-rush

**Borrowed or Real: Forecasting Import Surges Around U.S. Tariffs**

Rahul Reddy Mandadi, Raunaksingh Khalsa
DS 5500 Data Science Capstone, Northeastern University, Fall 2026

## Summary

United States tariffs are announced with a published effective date, which creates a window in
which importers can accelerate shipments to clear customs before the duty applies. This behavior,
known as front-loading, is followed by an extended period of below-normal imports.

The difficulty is not seeing the surge. Terminals and carriers can see roughly three weeks ahead
from security and manifest filings. The difficulty is that they commit capacity on horizons
measured in months, and nothing in that forward view says whether volume returns after a surge.
That turns on whether the surge was inventory borrowed from later months or a genuine rise in
demand, which the import series does not resolve until long after the commitment is made.

This project forecasts, using only information available on the day a tariff is announced, whether
the months following the effective date represent temporary payback of borrowed volume or a
durable reduction in demand. Two supporting quantities feed it, since any repayment is bounded by
what was borrowed: whether a surge occurs at all, and how large it is.

## Status

Panel and measurement built and validated. Event sample is being expanded before modeling.

**Import panel.** Census international trade API at HS10, the level tariff orders are written
at, rolled up to HS8 x partner x month: 140 months (2015-01 to 2026-08), 15.9M cells, 12,253
HS8 lines, 234 partners. Every month reconciles against the API's own all-country total, and
2017 sums to $2,340B against published imports of about $2.34 trillion. After inclusion rules
(36 months of history, $100k median monthly value) the analysis panel holds 6.1M rows carrying
95.7 percent of all import value.

**Coverage.** Each Chapter 99 surcharge code resolved to the HS8 lines it names: 23,462
(code, line) pairs over 9,083 distinct lines. Measured in dollars, the median tariff action
covers 5.4 percent of its chapter's value and a third cover under 1 percent, which is why
chapter-level treatment flags found nothing.

**Surge timing, by authority.** Within product and across origins, with product-month and
product-origin fixed effects, on month-over-month growth. Section 301 actions rush in the
announcement month (+26.8 percent, reversing to -36.5 percent the next month, flat
pre-period). IEEPA country-wide actions rush two to three months before the announcement.
Section 232 actions rush one month before. Lead time tracks how much warning the legal
mechanism gives.

**The aftermath of a tariff: substitution, not payback.** Measured on antidumping and
countervailing duty cases, which are the same kind of action as Section 232/301 but far more
numerous, single-country, with an explicit product list and months between a case becoming
public and duties being collected. 508 episodes against 473 placebo episodes built by shifting
every event back 24 months.

Imports from a targeted origin fall about 27 percent against other origins of the same product
and do not recover within eighteen months (p < 0.0001, stable across horizons of 6, 9 and 12
months).
Decomposing that gap into absolute series, the named origin ends about 36 points below its
placebo trend while the product's total ends about 8 points below, so roughly **79 percent of
the displaced volume is absorbed by other origins and roughly 21 percent disappears**. The
"other origins rise" leg does not separate from its own placebo, so the replacement share rests
on the comparison of totals rather than on observing other origins grow. Per episode the total
roughly holds in 29 percent of cases and falls in 39 percent, so the average covers two
regimes.

There is no rush beforehand. The month-by-month path is flat from twelve to four months before
duties start and then declines, so importers pull back once a case becomes public rather than
buying ahead. That fits the law: AD/CVD duties can be applied retroactively to the initiation
notice, so goods brought in during the window risk being taxed anyway. Section 301 actions,
which carry no such provision, show the opposite.

Three earlier estimators of the reversal ratio were built and discarded because they did not
survive the same placebo test. See PHASE2_RESULTS.md, which records what failed as well as
what held.

**Event table.** 2,792 Federal Register documents on Section 232/301/IEEPA actions, of which
134 are tariff actions; 21 have a usable window. Separately, 10,730 International Trade
Administration notices yield 3,399 duty-starting AD/CVD stages, parsed to 993 cases, 70
countries, 1,297 HS8 lines and 1,064 preliminary determinations with a recoverable
initiation-to-determination window, median 150 days.

## Planned structure

```
01_acquire_census.py     raw Census monthly pulls
02_acquire_fedreg.py     raw Federal Register documents
03_build_panel.py        tidy monthly import panel
04_build_events.py       deduplicated tariff events with dates, authority, rate
05_build_coverage.py     event x chapter x partner treatment map
06_build_labels.py       surge occurrence, magnitude, reversal ratio
07_build_features.py     announcement-day features only
08_split.py              leave-one-event-out splits, frozen before modeling
09_model_*.py            hurdle model and aftermath classifier
```

Large raw caches are not tracked and are rebuilt by stages 01 and 02.

## Known open problems

1. **The Section 232/301/IEEPA event set is still too thin on its own.** 21 usable events,
   median window 23 days. The AD/CVD cases carry the aftermath result; the rush results still
   rest on the small set and should be treated as weaker.
2. Partner extraction conflates the included set with the exception set.
3. Documents are not yet deduplicated into distinct events, which is why two notices of the
   same China action currently count twice.
4. Announcement dates measure the Federal Register filing, not when the market learned. For
   IEEPA actions the rush runs two to three months ahead of the filing, so an earlier
   information date is needed to put the three mechanisms on one clock.

Two problems previously listed here are resolved. Chapter 99 codes now join to the panel
through coverage/explode_products.py. The air-and-vessel weight gap is closed by GEN_QY1_MO,
which is published at HS10 and counts truck and rail: seaborne partners show a quantity to
shipping-weight ratio of 1.00 while Canada shows 0.31, confirming the overland share directly.
BTS TransBorder is no longer needed.

## Expanding the event sample

Section 232, 301 and IEEPA together give 21 usable events, which is not enough to estimate
repayment. Antidumping and countervailing duty cases are the same kind of action at far greater
volume: each names a specific product scope and a single country, which is exactly the
within-product across-origin comparison this project already uses, and the window from case
initiation to preliminary determination is measured in months rather than the current median of
four days.

560 such documents are already in the harvest, set aside as TRADE_REMEDY_CASE: 75 initiations,
57 preliminary affirmative determinations, 191 final determinations, 114 duty orders. Raw text
for all of them is on disk, so the scopes can be parsed without refetching.

The Census HS10 series also extends back to 2010, five years earlier than the current panel,
which widens the window in which those cases fall.

## Data sources

Census international trade API, Federal Register API, USITC Harmonized Tariff Schedule,
Global Trade Alert, WTO-IMF Tariff Tracker, IMF PortWatch, University of Michigan Surveys of
Consumers. All public and free for research use.

BTS TransBorder was listed here and in the proposal as necessary to close a land-mode blind
spot. The HS10 quantity field closes it directly, so it has been dropped.
