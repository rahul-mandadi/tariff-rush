# Phase two design

Decided 2026-10-12, before the harvest. Each choice has a reason and a cost.

## 1. Resolution: HS10, not HS6

Tariff lists are written at HS8. HS10 is HS8 plus two statistical digits, so HS10 rolls up to HS8
exactly and tariff lines match without approximation. HS6 would leave partial treatment inside
every cell, which is the dilution problem we are trying to remove.

Cost: 294,285 detail rows per month, roughly 41M rows and 1.8 GB over 139 months. That is twice
HS6, not the order of magnitude assumed earlier.

Pulling HS10 also keeps every coarser view available, since we can aggregate up to HS8, HS6 or
chapter at any time. Pulling HS6 would close off exact matching permanently.

## 2. Outcome: GEN_QY1_MO, with value as a cross-check

Census reports a statistical quantity at HS10 that the aggregated levels do not carry. For
unwrought aluminum in June 2024 it is reported in kilograms, and comparing it against the
air plus vessel shipping weight:

| partner | quantity | air + vessel | ratio |
| --- | --- | --- | --- |
| UAE, Argentina, South Africa, India, Bahrain, Brazil | | | 1.00 |
| Canada | 232.6M kg | 72.4M kg | 0.31 |

Seaborne partners sit at exactly 1.00, which means shipping weight equals total quantity for them.
Canada sits at 0.31, so 69% of its tonnage arrives by truck or rail and the quantity field counts
it while the weight fields do not.

**This closes the land-mode gap, and removes BTS TransBorder from the plan.** It also confirms the
69% Canada estimate we had derived indirectly from price benchmarks.

Two caveats. Quantity is reported in the unit native to each product, so it is not comparable
across products; that is fine because every baseline is fit per cell. And it is not populated on
every row, 71 of 109 in the sample above, so cells without it fall back to value.

Value stays as the secondary outcome. It is complete and it is customs value, which is measured
before duty is applied, so a tariff does not mechanically inflate it. It does move with prices,
which is why quantity leads.

Air and vessel weight is retained for one purpose only: identifying which cells are seaborne, which
matters for anything said about ports.

## 3. Unit of analysis

    HS8 product  x  partner  x  month

Aggregated up from HS10. Where an HS8 cell is too thin, fall back to HS6.

## 4. Identification: within product, across origins

For a tariff on one country, the control is the same product from countries without that tariff in
the same month.

This is the piece that has been missing. A commodity price shock moves every origin together. A
tariff moves one origin relative to the others. Comparing within a product across origins separates
them; nothing built so far could do that. It is also what finally rules out the cocoa problem,
where our detector flagged a supply shock as if it were a tariff response.

Specification: product by month fixed effects, treatment indicator on the tariffed origin. The
fixed effects absorb anything that moves a product globally in a given month.

## 5. Inclusion rules, to be set empirically before any model is fit

- minimum months of continuous history per cell
- minimum trade value, to drop cells that are noise
- at least one untreated origin for the same product and month, or the cell cannot be identified

These get fixed and written down before fitting, not tuned afterwards.

## What this plan drops

BTS TransBorder integration, which the proposal lists as necessary. The quantity field makes it
unnecessary, and we should say so rather than quietly skipping it.

## What stayed open, now settled

**Whether HS8 cells carry enough volume to support a per-cell baseline. They do, so the HS6
fallback is not needed.**

The panel is 2015-01 to 2026-08, 140 months, 15.9M HS8 x partner x month cells over 12,253 HS8
lines and 234 partners. 2026-09 is not published yet; Census runs about a 35 day lag.

Only 28.4% of cells have the 36 months of history an STL baseline needs. That sounds fatal and is
not: those cells carry **97.1% of all import value**. The thin cells are thin because almost
nothing moves through them. Requiring 36 months and a median of $100k a month leaves 52,452 cells
still holding 95.7% of value, which is a workable panel rather than a sacrifice.

Quantity holds up as the primary outcome: 95.5% of those cells report it in most months.

**The within-product design also has the controls it needs.** For product-months where an action
names the line, 89.6% have two or more supplying origins, with a median of 7. So for nearly nine
in ten treated product-months there is an untreated origin of the same product in the same month
to compare against. This is the comparison nothing built so far could make.

Inclusion rules, fixed here before any model is fit: at least 36 months of history, median monthly
value at least $100,000, and at least one untreated origin for the same product and month.

## Corrections found during the harvest build, 2026-10-12

Three things were wrong or missing in the plan above. Recorded here rather than quietly fixed.

**Volume was underestimated.** A full HS10 month is 507,065 rows, not the 294,285 assumed, so the
panel is roughly 70M rows rather than 41M. Compressed size is better than feared: about 7 MB per
month gzipped, so ~1 GB on disk rather than 1.8 GB. One month downloads in about 90 seconds, so the
harvest runs four months at a time to finish in under an hour instead of three and a half.

**The response carries a total row that double counts everything.** `CTY_CODE = "-"` is
TOTAL FOR ALL COUNTRIES and sits in the same response as the 226 partners it sums. Left in, it
doubles every figure: January 2015 came out at $362.4B against a true $181.2B. It is dropped, and
because the partners add back to it exactly, it is kept aside as a per-month reconciliation check
that the builder now runs on every month.

**We did not actually have the HS8 lines.** The design assumes exact matching to the lines the
tariff orders name, but `coverage_map.csv` only ever stored a count per chapter; the parser
resolved the individual subheadings and then discarded them. `coverage/explode_products.py` now
re-runs the same resolution and keeps them: 23,462 (code, line) pairs covering 9,083 distinct HS8
lines. Without this the HS10 pull would have had nothing exact to match against.

### What the lines say about the null result

Measured in dollars rather than line counts, over the months available so far, the median
(action, chapter) pair covers **5.1%** of its chapter's value. A third cover under 1%. Only 12%
cover more than three quarters. So a chapter-level treatment flag was mostly labelling untreated
trade as treated, which is consistent with the null and is the specific thing the HS8 panel fixes.

Preliminary: the reference window should be 2017, and only 2015 months are on disk at the time of
writing. To be recomputed on the full panel.
