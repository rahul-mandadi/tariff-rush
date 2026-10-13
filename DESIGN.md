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

## What stays open

Whether HS8 cells carry enough volume to support a per-cell baseline. If they do not, the fallback
is HS6, which reintroduces some dilution but far less than chapter level. This is the main
technical risk and it is answerable as soon as the panel exists.
