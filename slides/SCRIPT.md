# Presentation 1, spoken script

Eight talk slides, **under 10 minutes**. This is written to 9:12 measured, which leaves margin,
because live delivery always runs longer than a read.

**Split:** Rahul slides 1 to 4, Raunak slides 5 to 8. Both must speak, the rubric requires it.

**There is no slack. Do not ad-lib.** Everything that could be cut has been without losing
content the rubric asks for. The long version of each point lives in the deck's speaker notes,
for questions only.

**9:12 is a measured read, not a delivered talk.** Pointing at figures, pauses and a handover add
roughly ten percent, so expect about 10:05 on the first run. One timed rehearsal is not optional.
If it comes in over 10:00, the honest fix is fewer slides rather than faster talking: slide 4 is
49 seconds of signposting and could be spoken over slide 3.

Three sentences that must not be garbled:

1. "If you label a product group tariffed when ninety-five percent of it was not, any real
   reaction gets averaged away." (slide 7)
2. "A price shock moves every country together, so it cancels. A tariff hits one country, so it
   does not." (slide 8)
3. "The rush does not start when the tariff becomes official. It starts when it becomes likely."
   (slide 2)

---

## 1. Title. RAHUL. 0:35

I'm Rahul, this is Raunak. Our project is Borrowed or Real.

A tariff is a tax on imports. It gets announced on one day and starts on a later day. In between,
importers rush to beat it. Afterwards imports drop.

Our question is what that drop means. If the goods just came early, it is borrowed and it comes
back. If the business left for good, it is real.

I will take the first four slides.

---

## 2. Every tariff comes with a date. RAHUL. 1:03

Tariffs do not happen overnight. They get announced, and they take effect on a named date later.

**[point]** Figure 1 is copper imports, by month, in dollars. Here is July 2025, when a fifty
percent duty was announced. Here is August, when it started. Three weeks apart.

But look at the line. It does not wait for July. It starts climbing in February and nearly triples
by the announcement. The investigation behind that tariff was public months earlier, so everyone
saw it coming. The rush does not start when the tariff becomes official. It starts when it becomes
likely.

Then August, and it drops hard.

That is front-loading. Goods that would have arrived in October came in in June. Nothing new was
created, it just moved forward. We call that borrowed, because the later months pay it back.

---

## 3. The decision comes before the data. RAHUL. 1:03

Why does this matter? Because someone has to make an expensive decision on announcement day, and
the data they would need does not exist yet.

**[point]** Figure 2. Day zero, the tariff is announced. If you are importing from the country
that just got hit, you decide: wait it out, or go find a new supplier. Requalifying a supplier
takes months and real money. A lender behind that trade and a carrier running the route face the
same question.

Day thirty, the duty takes effect.

Day sixty-five is the first time official data shows what happened. Census publishes about five
weeks after the month closes.

So by the time you have seen two bad months, the tariff has been in force a quarter and the
decisions are already made.

That is the gap we are trying to close.

---

## 4. So we ask three questions. RAHUL. 0:49, then hand over

So, three questions.

One. Will there be a rush, and how big. Classification, then regression.

Two. What happens after the duty starts. This is the hard one, and it is our title. Three
answers: the goods were borrowed and come back, the demand was lost for good, or the same goods
now come from a different country.

Three. How long does it last. Some are still running at the end of our data, so it is a duration
problem.

This presentation is our data and its limits. No results today. But we did find something the hard
way, and Raunak will take you through it.

Raunak.

---

## 5. What we have. RAUNAK. 1:12

Thanks. Two sources, both free and public.

**[point left]** Figure 3 is US Census trade data. Every month from January 2015 to August 2026.
140 months, 15.9 million rows. The last bar is grey because 2026 is only eight months so far.

**[point right]** Table 1 is what one row actually is. One product, one country, one month. This
code, from Chile, March 2025, 715 million dollars, 74 million kilograms.

Look at that first column. Those are eight digit product codes, and we pull the data at ten
digits. Here is why. A tariff order does not say "copper", it lists specific eight digit codes,
and ten sits inside eight. So we can match a tariff to exactly the products it names instead of
guessing.

Is the data right? 2017 adds up to 2,340 billion dollars against a published 2.34 trillion, and
all 140 months check against a separate total.

Second source, the Federal Register. 2,792 documents, 134 real tariff actions.

---

## 6. Unusual is not the same as tariffed. RAUNAK. 1:21

First thing we tried was to find the months that look weird.

For each product group we worked out from earlier years what it would normally have done, drew a
band for ordinary wobble, and anything outside it is unusual.

**[point]** Figure 4 ranks the ten groups that went furthest outside their own normal range in
2025. The scale is how many times outside the band. One is right at the edge.

Some look like tariff stories. Organic chemicals and pharmaceuticals were both under open tariff
threat in 2025.

But look at the red ones. Silk is about 55 million dollars a year, so almost any month looks
extreme next to its own history. And cocoa is up there because cocoa prices roughly tripled after
bad West African harvests. We measure in dollars, so a price spike looks exactly like a surge in
volume.

So the detector finds unusual months but has no idea why. It cannot tell a tariff from a bad
harvest. Connecting an unusual month to an actual tariff is the next slide.

---

## 7. And this is where it nearly came apart. RAUNAK. 1:42

A tariff order never says "chapter 74, copper". It points at a list of specific eight digit codes,
usually in a separate legal notice. If you have not read those lists, all you can do is mark a
whole product group as tariffed whenever any action touches anything inside it.

That is what we did. And we got nothing.

So we read the lists. 9,083 eight digit codes.

**[point]** Figure 5. Each bar counts a tariff action paired with a product group. The typical one
covers about five percent of that group's value. The red on the left is a third of them covering
less than one percent.

Copper again. Ten actions touch copper. Three cover more than half of it. The other seven cover
less than one percent.

And that is why we got nothing. If you label a product group tariffed when ninety-five percent of
it was not, any real reaction in the five percent gets averaged away by the ninety-five percent
that did nothing. The zero was not telling us about the world. It was telling us about our ruler.

It was one of three reasons, and it is the one that generalizes.

The fix is to work at eight digits, where a tariff either names a product or it does not.
Everything from here is built that way.

---

## 8. Where we are. RAUNAK. 1:23

Built and checked: 140 months at the level tariffs are actually written, reconciled against
published totals.

A detector that finds unusual months, and cannot on its own tell a tariff from a price shock.

134 tariff actions, with the real product lists behind each one.

How we will measure it, and this is what fixes the detector. Instead of comparing a product to its
own past, we compare one product across countries in the same month. A price shock moves every
country together, so it cancels. A tariff hits one country, so it does not.

How we will know it is real: every estimate gets a placebo, the same calculation with every event
shifted back two years. If it does not separate from its placebo, we do not report it. That has
already killed three methods we built.

Next, question one first, then two and three for the final report.

And the takeaway: do not measure this at product group level. The typical action touches five
percent of a group, so a real effect averages away to nothing.

Questions?

---

## Clock

| slide | who | target | cumulative |
| --- | --- | --- | --- |
| 1 title | Rahul | 0:35 | 0:35 |
| 2 every tariff comes with a date | Rahul | 1:03 | 1:39 |
| 3 the decision comes before the data | Rahul | 1:03 | 2:42 |
| 4 so we ask three questions | Rahul | 0:49 | 3:32 |
| 5 what we have | Raunak | 1:12 | 4:45 |
| 6 unusual is not the same as tariffed | Raunak | 1:21 | 6:06 |
| 7 and this is where it nearly came apart | Raunak | 1:42 | 7:48 |
| 8 where we are | Raunak | 1:23 | 9:12 |

**Hand over at 3:32.** If the handover is past 4:30, Raunak drops the "is the data right" sentence
on slide 5 and the organic chemicals sentence on slide 6. That buys about twenty seconds.

If you are over 7:00 when slide 7 starts, cut the copper sentences on slide 7 and go straight from
Figure 5 to "and that is why we got nothing". Slide 7's argument survives without copper; it does
not survive without that sentence.

---

## If asked

**"So is there a rush?"** We have the data and the product level matching to answer it now. The
product group version of the question was unanswerable, for the reason on slide 7.

**"Who exactly is the customer?"** Whoever is exposed to one country rather than to total volume:
an importer requalifying a supplier, a lender behind either side, a carrier running that route. We
are still testing which the data serves best. An earlier version of this project named port and
terminal operators; we tested it and dropped it, because displaced volume arrives from a different
country through much the same US customs districts.

**"Five percent of what?"** The median over 1,350 action and product group pairs. Per action the
median is 1.3 percent, so the slide is the conservative version.

**"What were the other two reasons?"** Our announcement dates are mostly implementing notices, so
the median official window is nine days and there is almost no anticipation period in the data.
That is what the copper story answers: the rush runs on news, not on documents. And the partner
dimension was collapsed, which the across-origins design fixes.

**"Your copper chart recovers, so what is the problem?"** Correct, and we are not claiming copper
proves anything. In tonnage it goes 293 thousand tonnes in July 2025, down to 93 thousand in
November, back to 245 thousand by August 2026. One product, one event. It is on slide 2 to
explain front-loading.

**"Why not just watch the data and react?"** That is slide 3. The first usable data lands about
five weeks after the month closes, and the decision is on announcement day.
