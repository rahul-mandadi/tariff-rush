# Presentation 1: the story

The arc the EDA supports, with the number that carries each beat. Scope is deliberately the
data and what it can and cannot do. Modelling results are not in here.

Every number below is produced by `explore_data.ipynb`, which runs clean off `eda/*.csv`.

---

## 1. The problem belongs to someone

When a tariff is announced with a future start date, imports from the targeted country rush in
before the duty applies, then fall away.

Somebody has to decide what to do about that. An importer with a supplier in that country has
to choose between waiting it out and qualifying a supplier somewhere else, and requalification
runs months and costs real money. A lender financing that importer, or financing the supplier
on the other side, holds the same question as credit risk. A carrier that runs a service from
that origin has to decide whether to keep the string.

All of them decide on announcement day, with no idea yet whether this is a disruption or a
permanent loss of a supplier.

**The beat:** the decision is where to buy next and when. It gets made before the answer is
knowable.

## 2. Why it is hard

Two reasons, and the second is the one people miss.

A surge and a boom look identical while they are happening. One is volume borrowed from later
months that will be repaid; the other is real growth. The series does not separate them until
long after the decision has been made.

And you cannot simply watch and react, because the data arrives late. Census publishes monthly
trade about five weeks after the month closes. By the time two bad months are on the screen,
the duty has been in force for a quarter.

**The beat:** the difficulty is not detection, it is interpretation, and the clock runs against
you while you wait for certainty.

## 3. What we have

Monthly US imports from the Census Bureau, January 2015 to August 2026.

- 140 months, 15.9 million product-partner-month cells
- Pulled at HS10, the finest level published, because tariff orders are written at HS8 and
  HS10 nests exactly inside it
- 234 trading partners, 98 product chapters, $32.4 trillion

**Why anyone should believe it:** 2017 sums to $2,340 billion against a published figure of
about $2.34 trillion. Every one of the 140 months reconciles against a separate total the API
returns on its own.

**One judgement worth showing:** we use quantity in kilograms rather than dollars where we can.
Dollars move when prices move. Quantity also counts goods arriving by truck and rail, which the
shipping-weight fields miss entirely. For Canada that is 69 percent of tonnage. This removed a
whole external dataset from the plan.

## 4. What a tariff looks like

Copper, 50 percent duty from 1 August 2025. A visible climb before the date and a drop after.

Then the honest turn: a single chart is not evidence. Imports move for prices, seasons and the
business cycle. So we build what the series would have done anyway from pre-event data only,
and draw a band for ordinary variation.

Copper peaks 89 percent above normal against a band of 50 percent, so it clears.

Aluminium does not, and that is worth a sentence. It peaks at 26 percent against a band of
100 percent, because aluminium's own history is volatile enough that 26 percent is an ordinary
month for it. Same tariff, same year, and the test says no.

**The beat:** now it is a measurement rather than a picture, and a measurement that can say no
is the only kind worth having.

## 5. The detector cannot tell you why

Run that across all 98 chapters rather than the ones we suspected, and the top of the list is a
mix.

Plausible: organic chemicals and pharmaceuticals were under open tariff threat in 2025, and
gold and gems surged as metal moved into US vaults ahead of expected duties.

Not tariff stories at all: silk is a $60 million chapter, so almost any month looks extreme.
Cocoa is the trap worth dwelling on, sitting near the top because cocoa prices roughly tripled
after bad West African harvests. We measure in dollars, so a price spike reads as a surge.

**The beat:** finding unusual months is the easy half. Connecting an unusual month to an actual
tariff is the real work, and it is where the project nearly came apart.

## 6. The trap, which is the finding

A tariff order does not say "chapter 74". It points at a list of 8-digit product codes, usually
published in a separate legal notice. Until those lists are read, the only available move is to
treat a whole chapter as tariffed whenever an action touches anything inside it.

We read them: 9,083 distinct 8-digit codes across 162 actions.

**The median tariff action covers 5.4 percent of its chapter's value. A third cover under
1 percent.**

So chapter-level treatment means about 95 percent of what is being measured is trade the tariff
never touched. A real reaction in the 5 percent gets averaged into nothing by the 95 percent
that did nothing.

**The beat, and the one to land:** our first attempt to measure an effect found nothing. This
is why. The null was our ruler, not the world. Everything afterwards is built at the 8-digit
level, where a tariff either names a product or it does not.

## 7. Where that leaves us

- 140 months at the exact level tariffs are written, checked against published totals
- A detector that finds unusual months, and a clear statement of what it cannot do alone
- 134 tariff actions with corrected dates, and the product list behind each one
- A measured account of the trap that made the first attempt fail

---

## Notes for building slides

**Lead with section 6 if time is short.** It is the only beat that is genuinely ours: a
specific, quantified reason a reasonable approach fails. Sections 1 to 5 set it up.

**The cocoa example earns its place.** It shows the method being sceptical of itself, which is
worth more than another chart that works.

**Do not claim an effect.** This presentation is the data and its limits. The modelling is not
in scope and is better held.

**Three charts carry it:** copper against its expected band, the chapter ranking with cocoa and
silk visible, and the coverage-share bar chart. The third is the one to spend time on.

**If asked "so is there a rush?":** the honest answer is that we now have the data and the
product-level matching to answer it, and that the chapter-level version of the question was
unanswerable for the reason in section 6.

**If asked "who exactly is the customer?":** say the decision is where to source next and when,
and that it sits with whoever is exposed to a particular country rather than to total volume:
the importer requalifying a supplier, the lender behind either side, the carrier running that
origin's service. Then say you are still testing which of those the data actually serves. That
is true, and it is a better answer than naming one confidently.

Do not claim a port or terminal operator as the user. An earlier version of this project did,
and we have since tested it: when volume is displaced from one country it arrives from another
through substantially the same US districts, so a terminal's throughput barely changes. That
test is not in this presentation, but the claim it killed should not be in it either.
