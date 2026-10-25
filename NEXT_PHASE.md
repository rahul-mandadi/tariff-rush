# Next phase: the plan, and whether this works


**SUPERSEDED 2026-10-13.** This proposed moving to HS6. We went to HS10 rolled to HS8 instead,
because tariff orders are written at HS8 and HS6 would have left partial treatment inside every
cell. Kept for the reasoning; do not follow the plan. See DESIGN.md.
Internal. Written 2026-10-12.

## Three problems, one cause

We ended phase one with three blockers:

1. only 18 usable events
2. coverage diluted, a typical tariff touches 5 product lines in a chapter holding hundreds
3. countries pooled, so a China tariff is measured against imports from everywhere

These are not three problems. They are one problem seen three ways. **We are measuring at the
wrong resolution.** The outcome is currently a chapter summed across all partners. Tariffs are
written at the product line for a named country. Everything downstream inherits that mismatch.

## The change

Move the outcome from

    chapter  x  all partners  x  month          98 x 1 x 139

to

    HS6 product  x  partner  x  month           ~5,300 x 234 x 139

Nothing else about the method changes. Same counterfactual, same episode logic, same labels.

## Why this fixes all three

**Dilution disappears.** Section 301 lists are HS8, which roll into HS6 cleanly. A tariffed product
line is tariffed, not averaged against its untariffed neighbours.

**Sample size stops being the constraint.** Today 18 events across roughly 5 chapters each gives
about 90 units of analysis. At product and partner level the same 18 events cover thousands of
cells. The events are few; the treated cells are not.

**We gain a control that was never available before.** For a tariff on China, the same HS6 product
from Vietnam or Germany in the same months is an almost ideal comparison: same good, same global
demand, same shipping conditions, no tariff.

That last point matters more than the other two. It solves the identification problem we have been
circling since the cocoa result. A commodity price shock moves every origin together. A tariff
moves one origin relative to the others. Differencing within product across origins separates
them, and nothing we have built so far could do that.

It also answers the objection raised in the stakeholder review, that our output unit does not match
any decision. Product and partner is much closer to how a carrier or a terminal thinks than an
HS chapter is.

## Cost

| step | work | time |
| --- | --- | --- |
| harvest HS6 by partner, 2015 to now | 139 API calls, larger payloads | ~1 hour, parallelised |
| storage | roughly 19M rows, about 860 MB | gitignored, as the current panel is |
| rebuild counterfactual at new resolution | same code, more cells | a few hours of compute |
| re-join coverage at HS6 | mapping already exists, finer target | a day |
| treated versus within-product control | the result | a day |

No new data source. No new method. The Census API serves HS6 from the same endpoint we already use.

## Risks, honestly

**Thinner series are noisier.** An HS6 and partner cell has far less volume than a chapter, so
tolerance bands widen and some cells will be unusable. Mitigation: restrict to cells with
continuous history and meaningful volume, and lean on the within-product control, which removes
common shocks rather than trying to model them.

**Not every tariff line maps cleanly.** HS8 to HS6 is a rollup, so where a tariff covers some HS8
lines inside an HS6 we are back to partial treatment, just far less of it. Mitigation: compute
coverage as a share of value rather than a flag, which we should do regardless.

**The effect may genuinely be narrow.** It is possible front-loading is large for broad material
tariffs like Section 232 metals and small for scattered product lists like Section 301. If so we
will find that cleanly, and it is a real finding rather than a failure. Aluminum at +49% and copper
at +111% are not noise, so the phenomenon exists somewhere.

## Is the project on track

Yes, with one qualification.

What is solid: the phenomenon is real and measured, the pipeline runs end to end, the data is free
and already in hand, and the remaining work is a resolution change rather than a redesign.

What is not yet solid: we have not produced a defensible positive result. We have produced a
well-understood negative one, which is a reasonable place to be at the halfway mark but not a
place to finish.

The qualification is that the honest downside is a narrower finding, not an empty one. Even if the
within-product design shows front-loading only for broad material tariffs, that is a defensible
answer to the research question, supported by a clean comparison, and it tells a port operator
something true.

## Sequence

1. harvest HS6 by partner
2. rebuild panel and counterfactual at that resolution
3. express coverage as a share of value per product and partner
4. treated versus within-product, within-month control; this is the result that was missing
5. only then the three prediction questions

Steps 1 to 4 are about two weeks. That leaves the rest of the term for the models and the writeup.
