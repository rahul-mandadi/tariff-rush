# Presentation 1: the story

Eight slides, plus two backup. Scope is the data and what it can and cannot support.
Modelling results are deliberately not in here.

Every number comes from `explore_data.ipynb`, which runs clean off `eda/*.csv`, so the deck and
the notebook cannot drift apart.

---

## The story in one sentence

We set out to measure whether tariffs cause an import rush, built the data and the detector,
and found that the obvious approach is 95 percent noise. That number is the finding.

## The shape

Three acts.

- **Slides 2 to 4** set up a real problem with money riding on it.
- **Slides 5 and 6** build confidence: good data, a working method.
- **Slide 7 pulls the rug.** It did not work, and here is exactly why.
- **Slide 8** banks what that bought.

The reversal on slide 7 is the talk. Without it this is an inventory of a dataset. With it,
something goes wrong and we are the ones who found it.

---

## Slide by slide, with the transitions

The transitions matter as much as the slides. A deck only works if each slide leaves a question
the next one answers.

### 1. Borrowed or Real
Title, authors, stakeholders, repository. Do not linger.

> "Let me start with what a tariff actually does to trade."

### 2. Every tariff comes with a date.
Establishes the phenomenon for someone who knows nothing about trade. A tax is announced, it
starts later, people rush to beat it. Visible in the copper line.

The audience should be thinking: *obviously, that is just incentives.* Good. That is the floor
we build on.

> "So the pattern is real and visible after the fact. The problem is who can see it in time."

### 3. The decision comes before the data.
Where the stakes arrive. An importer has to commit on announcement day. The data showing what
actually happened lands about five weeks after the month closes. The audience should feel the
squeeze.

This slide has to land emotionally or nothing after it matters.

> "So that is the gap. Here is what we are trying to answer inside it."

### 4. So we ask three questions.
The signpost. Keep it short. Say out loud that today is data and limits, not answers. That
sentence buys permission for everything after it.

> "To answer any of that you need two things: the imports, and the tariffs."

### 5. What we have.
Confidence building. 140 months, one row shown concretely so nobody has to imagine it, and it
reconciles against published totals.

The audience should be thinking: *these people have their data straight.*

> "Good data. But having it does not mean you can find a tariff in it."

### 6. Unusual is not the same as tariffed.
First complication, and the slide that proves we are honest. Cocoa sits near the top because
cocoa prices roughly tripled after bad West African harvests, not because of any tariff. We
found our own false positive and we are showing it.

> "So we need something that connects an unusual month to an actual tariff. That is where it
> got interesting."

### 7. And this is where it nearly came apart.
The reversal. A tariff order names 8-digit product codes, not chapters. Read those lists and
the typical action covers about 5 percent of its chapter's value, a third cover under
1 percent. So chapter-level measurement is mostly untouched trade.

Then say the line plainly: **our first attempt to measure an effect found nothing, and this is
why. The null was our ruler, not the world.**

Say it with your chin up. This is not a confession, it is a measurement that explains a null
result, and it is the most credible thing in the deck.

> "So that is the trap, and the number. Here is where it leaves us."

### 8. Where we are.
Bank it. The data, a detector whose limits we can state, 134 actions with the product lists
behind them, and one measured reason the obvious approach fails.

---

## Notes for delivering it

**The two moments that carry the talk** are slide 3 and slide 7. Everything else is scaffolding
holding those two up.

**Timing.** Eight slides over 10 to 15 minutes. Slides 2, 3 and 7 want more than a minute.
Slides 4 and 5 want less. Rehearse once with a clock.

**Speaker split.** Slides 1 to 4 one of us, 5 to 8 the other. The rubric requires both of us to
speak. The natural break is after the three questions, because the first half is the problem
and the second half is what we did about it.

**Do not claim an effect.** This presentation is data and limits. The modelling is out of scope
and better held for later.

**Do not claim a port or terminal operator as the user.** An earlier version of this project
did. We have since tested it: when volume is displaced from one country it arrives from another
through substantially the same US customs districts, so a terminal's throughput barely changes.
That test is not in this presentation, but the claim it killed should not be in it either.

## Questions to expect

**"So is there a rush?"**
We now have the data and the product-level matching to answer it. The chapter-level version of
the question was unanswerable, for the reason on slide 7.

**"Who exactly is the customer?"**
The decision is where to source next and when, and it sits with whoever is exposed to a
particular country rather than to total volume: the importer requalifying a supplier, the
lender behind either side, the carrier running that origin's service. Then say we are still
testing which of those the data best serves. That is true, and it is a better answer than
naming one confidently.

**"Why not just watch the data and react?"**
Census publishes about five weeks after the month closes. By the time two bad months are
visible, the duty has been in force for a quarter. Slide 3.

**"How do you know the data is right?"**
2017 adds up to 2,340 billion dollars against a published 2.34 trillion, and all 140 months
reconcile against a separate all-country total the API returns on its own.

## Backup slides

Slide 9 is the tariff-action timeline, for questions about where the dates come from.
Slide 10 is the copper normal-range chart, for questions about how slide 6's band is built.
Neither is part of the talk.
