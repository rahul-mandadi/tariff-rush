# Coverage pull: what we built and what it showed

Written 2026-10-12. This is the stopping point for presentation 1.

## What was built

A coverage map linking tariff actions to the products and countries they touch, which is the join
that was missing between the import panel and the tariff event table.

```
coverage/pull_hts99.py        fetch HTS chapter 99 from USITC
coverage/build_coverage.py    parse surcharge codes and the U.S. notes that list products
coverage/rules.py             scope rules for authorities that do not enumerate products
coverage/assemble_coverage.py combine parsed lists and rules
coverage/join_events.py       attach scope to each Federal Register event
coverage/treated_vs_untreated.py   the test
```

**488 of 637 surcharge codes now have a product or country scope**, and 87 of 134 tariff events
resolve to chapters, including all 27 IEEPA events and 42 of 47 Section 232 events.

## The structural finding

The three authorities define scope in three different ways, and only one is a list.

| authority | how scope is defined | how we resolve it |
| --- | --- | --- |
| Section 301 | enumerates HS8 subheadings in a U.S. note | parse the note |
| Section 232 | names a material class, "articles of aluminum" | chapter rule from the schedule |
| IEEPA | whole country with carve-outs | every chapter the partner ships |

This was not obvious in advance and it shaped the whole build. A single parser was never going to
work.

## The test, and the honest result

For every chapter we measured how far imports ran from what a pre-2025 counterfactual predicted,
then compared months inside a tariff's announcement-to-effective window against all other months.

**There is no significant front-loading signal at chapter level.** Treated months have a slightly
lower median than untreated, and the one-sided test fails outright.

Three identified reasons, in order of severity.

**1. We do not have real announcement dates.** The median window between our announcement and
effective dates is **7 days**. Most of the 134 records are implementing notices published shortly
before a duty starts, not the original announcement. Aluminum is the clear example: the real window
ran from 10 February to 12 March 2025, but the document we hold is dated 5 March. For most events
there is no anticipation window left to measure.

**2. Coverage is diluted at chapter level.** For enumerated tariffs the median is **5 product
lines per chapter**. A chapter marked treated is typically tariffed on five HS8 lines out of
hundreds, so any effect is averaged away. This is the Section 301 problem stated quantitatively.

**3. The partner dimension is collapsed.** Anomalies are computed across all partners, so a
China-only tariff competes against every other supplier in the same chapter.

## What survives, and why it matters

Splitting events by how much time they actually allowed:

| window between announcement and effect | events | chapter-months | months running >40% above normal |
| --- | --- | --- | --- |
| 0 to 6 days | 19 | 220 | 5% |
| 7 to 20 days | 13 | 40 | 8% |
| 21 to 60 days | 4 | 24 | **17%** |
| no tariff (control) | | 7,977 | 4% |

The effect rises monotonically with the length of the window, which is exactly what the theory
predicts: front-loading requires time to front-load. It is not statistically significant, p = 0.26,
because only four events in the whole table gave importers three weeks or more.

The method also catches the case we already knew was real. Chapter 76 in February and March 2025
is correctly flagged, at +45% and +49% above normal.

## What has to be fixed next

In priority order, because the first one alone may change the result.

**Get real announcement dates.** Presidential proclamations and USTR press releases carry the
announcement; the Federal Register carries the publication. These are different dates and we have
been using the wrong one. 60 event records currently have an effective date before their
announcement date, which is a parsing error on top of the conceptual one.

**Measure coverage as a share, not a flag.** Compute what fraction of each chapter's import value
the tariffed lines represent, using one finer-grained pull. Treatment becomes a number between 0
and 1 instead of yes or no.

**Add the partner dimension.** Compare China-origin imports of a tariffed product against the same
product from untariffed origins, rather than against the chapter total.

---

# Update: the dates are fixed, the result is unchanged

## We already had announcement dates

The Federal Register records the date a proclamation was signed, separately from the date it was
published. We had harvested that field and never used it. All 80 presidential documents carry a
signing date, and for aluminum it is correct: signed 10 February 2025.

So the earlier claim that we lacked announcement dates was wrong. What was broken was the
effective date.

## What was actually wrong

Proclamations recite the history of earlier rate changes using the same language as the operative
date. The aluminum proclamation says "on or after" eleven times, listing changes going back to
2020, and names March 12 2025 nine separate times. The parser took February 8 2020.

Two rules fix it: an effective date cannot precede the announcement, and among what remains the
operative date is the one the document repeats most.

| | before | after |
| --- | --- | --- |
| events with an effective date | 93 | 96 |
| effective date before announcement | 17 | 0 |
| events with a window of 21 days or more | 4 | 30 |

Aluminum now reads: announced 10 February 2025, effective 12 March 2025, a 30 day window.

## The result did not change

Testing again with corrected dates, and looking at the months just before a duty starts rather
than the whole window:

| month relative to the duty starting | chapter-months | share >20% above normal |
| --- | --- | --- |
| two months before | 108 | 17% |
| month before | 107 | 13% |
| month it starts | 106 | 16% |
| no tariff (control) | 7,977 | 9% |

Treated months run modestly hotter in the tail, but medians sit below control and nothing reaches
significance.

## Why, and what is left

Only **18 events** have both a window long enough to front-load into and product scope we can
resolve to chapters. That is the real sample size, and it is too small to detect a moderate effect.

The two problems named earlier are still unfixed and are now the binding ones.

**Coverage is diluted.** The median enumerated tariff touches 5 product lines in a chapter that
contains hundreds. Treating the whole chapter as tariffed averages the effect away.

**Partners are pooled.** A China-only tariff is measured against imports from every country at
once, so the effect competes with every untariffed supplier in the same chapter.

Both are fixable and both are real work rather than a parsing patch. Fixing coverage means pulling
imports at a finer product level and computing what share of each chapter a tariff actually covers.
Fixing partners means comparing tariffed origins against untariffed origins of the same product.

That is the next phase, and it is where presentation 2 should start.
