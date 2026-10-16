# Presentation 1, spoken script

Eight talk slides, 10 to 15 minutes. Target 12:00 so there is room to breathe.

**Split:** Rahul slides 1 to 4, Raunak slides 5 to 8. Both must speak, the rubric requires it.

**Lines in `[ ]` are cut-if-behind.** Everything outside them is load-bearing.

Three sentences that must not be garbled, in order of importance:

1. "If you label a product group tariffed when ninety-five percent of it was not, any real
   reaction gets averaged away." (slide 7)
2. "A price shock moves every country together, so it cancels. A tariff hits one country, so it
   does not." (slide 8)
3. "The rush does not start when the tariff becomes official. It starts when it becomes likely."
   (slide 2)

---

## Slide 1, title. RAHUL. 0:45

Hi, I'm Rahul, this is Raunak. Our project is called Borrowed or Real, and it is about what
happens to imports when the US announces a tariff.

Here is the one sentence version. A tariff is a tax on imports. It gets announced on one day and
starts on a later day. In between, importers rush to get goods in before the tax applies. Then
imports drop.

The question in our title is what that drop actually means. If the goods just arrived early, the
drop is borrowed, and it comes back. If the business went somewhere else and stayed there, it is
real.

I will take the first half, Raunak takes the second.

---

## Slide 2, every tariff comes with a date. RAHUL. 1:50

Let me start with the thing that makes any of this possible.

When the US puts a tariff on something, it does not happen overnight. It gets announced, and it
takes effect on a named date later.

**[point at the chart]** Figure 1 is copper. This line is how many dollars of copper came into the
US each month.

Here is July 2025, when a fifty percent duty on copper was announced. Here is August, when it
started. Three weeks apart.

Now look at what the line actually does. It does not wait for July. It starts climbing in
February. [In February copper is about one and a quarter billion dollars a month. By July it is
three point two billion.] It nearly triples before the announcement.

Why? Because the investigation behind that tariff was public months earlier. Everyone in the
industry could see it coming. So the rush does not start when the tariff becomes official. It
starts when the tariff becomes likely.

Then here is August, and it falls off a cliff.

That behaviour has a name, front-loading. Goods that would have arrived in October came in in
June instead. Nothing new was created, it just moved forward in time. We call that borrowed,
because the later months pay it back.

One honest note on this chart. Copper does come back up at the end. This is one product and one
tariff. It is here to show you the idea, not to prove anything. The measuring starts in a few
slides.

---

## Slide 3, the decision comes before the data. RAHUL. 1:40

So why does anyone care?

Because somebody has to make an expensive decision on announcement day, and the information they
would need does not exist yet.

**[point]** Figure 2 is that timeline. Day zero, the tariff is announced. If you are an importer
buying from the country that just got hit, you have a choice. Wait it out and hope it gets
reversed? Or go find a supplier somewhere else? Qualifying a new supplier takes months and costs
real money. Either way, getting it wrong is expensive.

[And it is not only importers. A bank that lent against that trade has the same question as credit
risk. A shipping line running that route has to decide whether to keep running it.]

Day thirty, the duty takes effect.

And here, day sixty-five, is the first time you can look at official data and see what actually
happened. Census publishes monthly trade about five weeks after the month closes.

So by the time you have seen two bad months, the tariff has been in force for a quarter, and all
of those decisions are already made.

That is the gap we are trying to close. Not to explain the past. To say something useful on day
zero.

---

## Slide 4, so we ask three questions. RAHUL. 1:10, then hand over

So we turned that into three questions.

One. Will there be a rush, and how big? That is really two problems. First, does it happen at
all. Then, how large. Classification, then regression.

Two. What happens after the duty starts? This is the hard one, and it is the title of the
project. Three possible answers. The goods were borrowed and they come back. The demand was lost
for good. Or the same goods are now bought from a different country.

Three. How long does it last? Some of these are still running at the end of our data, so it is a
duration problem.

One thing before I hand over. This presentation is about our data and what it can and cannot
support. We are not showing results today. What we are showing is something we found out the hard
way, and that is the part Raunak will take you through.

Raunak.

---

## Slide 5, what we have. RAUNAK. 1:50

Thanks Rahul. I will talk about the data.

Two sources, both public and both free.

**[point left]** The first is US Census trade data. Figure 3 is what we pulled. Every month from
January 2015 to August 2026. That is 140 months, about 15.9 million rows. One note on this chart,
the last bar is grey because 2026 is only eight months so far, not a full year.

**[point right]** Table 1 shows what one row actually is. One product, one country, one month. So
this product code, from Chile, in March 2025, 715 million dollars, about 74 million kilograms.

The important part is that first column. Those are eight digit product codes, and we pull the data
at ten digits.

Here is why that matters. A tariff order does not say "copper". It lists specific eight digit
codes. Ten digits sit inside eight. So pulling at ten means we can match a tariff to exactly the
products it names, instead of guessing.

[For scale: both codes in that table are copper. Copper has 88 separate eight digit codes in
that one month alone.]

How do we know the data is right? Add up 2017 and we get 2,340 billion dollars. The published
figure for US imports that year is 2.34 trillion. And all 140 months check against a separate
total the API gives us on its own.

The second source is the Federal Register, which is where tariffs get published. We went through
2,792 documents and classified 134 of them as real tariff actions.

---

## Slide 6, unusual is not the same as tariffed. RAUNAK. 1:55

So we have trade data, and we have tariff dates. The first obvious thing to try is to find the
months that look weird.

That is what we built. For every product group we used the earlier years to work out what it
would normally have done, then drew a band around that for ordinary month to month wobble.
Anything outside the band is unusual.

**[point]** Figure 4 ranks the ten product groups that went furthest outside their own normal
range in 2025. The scale along the bottom is how many times outside the band they went. One means
right at the edge.

Some of these look like tariff stories. Organic chemicals and pharmaceuticals were both under open
tariff threat during 2025. [Gold moved into US vaults ahead of expected duties.]

But look at the red ones. Silk is a tiny category, about 55 million dollars a year, so almost any
month looks extreme next to its own history. [Works of art and clocks are small and lumpy.]

And then cocoa. Cocoa is on this list because cocoa prices roughly tripled after bad harvests in
West Africa. We measure in dollars. So a price spike looks exactly like a surge in volume.

That is the problem with this slide. The detector finds unusual months. It has no idea why they
are unusual. It cannot tell a tariff from a bad harvest.

So we needed something that connects an unusual month to an actual tariff. That is the next slide,
and that is where this got difficult.

---

## Slide 7, and this is where it nearly came apart. RAUNAK. 2:35

This is the slide I would keep if we only had one.

Here is the problem. A tariff order never says "chapter 74, copper". It points at a list of
specific eight digit codes, and that list is usually in a separate legal notice. So if you have
not read those lists, the only thing you can do is mark a whole product group as tariffed whenever
any action touches anything inside it.

That is what we did first. And we got nothing. No effect at all.

So we went and read the lists. 9,083 separate eight digit codes.

**[point]** Figure 5 is what we found. Each bar counts a tariff action paired with a product
group, and the height is how many land in each band of coverage. The typical one covers about five
percent of its group's value. The red on the left is the part that matters: a third of them cover
less than one percent.

Copper again, since you have seen it twice already. Ten tariff actions touch copper. Three of them
cover more than half of it. The other seven cover less than one percent. [Several are carve-outs
for civil aircraft parts that name a single product line.] The middle one covers under a tenth of
one percent.

[So if you mark copper as tariffed whenever any action fires, seven times out of ten you have
flagged the whole thing over something that touches almost none of it.]

And that is why we got nothing. If you label a product group tariffed when ninety-five percent of
it was not, any real reaction in the five percent gets averaged away by the ninety-five percent
that did nothing. The zero was not telling us about the world. It was telling us about our ruler.

[This is not just us. The main paper on these tariffs works at eight to ten digits for the same
reason, and there is work from the US trade commission showing estimates get smaller the coarser
your data is.]

The fix is to work at eight digits, where a tariff either names a product or it does not.
Everything from here is built that way.

---

## Slide 8, where we are. RAUNAK. 1:40

So where does that leave us.

Built and checked: 140 months of trade at the level tariffs are actually written, reconciled
against published totals.

A detector that finds unusual months, and we are upfront that on its own it cannot tell a tariff
from a price shock.

134 tariff actions with the real product lists behind each one. [And start dates we had to
re-read from the order texts, because our first pass kept picking up old dates the documents were
quoting.]

How we will measure it, and this is what fixes the detector. Instead of comparing a product to its
own past, we compare one product across countries in the same month. A price shock moves every
country together, so it cancels. A tariff hits one country, so it does not. That is the method.

How we will know it is real: every estimate gets paired with a placebo. We run the identical
calculation with every event shifted back two years. If a result does not separate from its own
placebo, we do not report it. That has already killed three methods we built.

Next, question one first, then two and three for the final report.

And the one thing to take away even if you never touch tariff data: do not measure this at product
group level. The typical action touches five percent of a group, so a real effect averages away to
nothing.

Happy to take questions.

---

## Running total

Measured at 130 words a minute, which is a steady speaking pace. Live delivery with pointing and
pauses runs longer, so treat these as a floor.

| slide | who | full | every bracket cut |
| --- | --- | --- | --- |
| 1 title | Rahul | 0:53 | 0:53 |
| 2 every tariff has a date | Rahul | 1:54 | 1:43 |
| 3 decision before data | Rahul | 1:35 | 1:19 |
| 4 three questions | Rahul | 1:11 | 1:11 |
| 5 what we have | Raunak | 1:56 | 1:46 |
| 6 unusual is not tariffed | Raunak | 1:58 | 1:50 |
| 7 nearly came apart | Raunak | 2:47 | 2:09 |
| 8 where we are | Raunak | 1:51 | 1:40 |
| | | **14:05** | **12:31** |

So the brackets buy about a minute and a half, not more. If a full read comes in over 15:00,
the cut has to come from content, not from talking faster.

**Checkpoints.** Hand over to Raunak by **5:40**. Be starting slide 7 by **9:40**. If slide 7
starts later than 10:30, drop the bracketed lines on 7 and 8 and go straight to the takeaway.

## If asked

**"So is there a rush?"** We now have the data and the product level matching to answer it. The
product group version of that question was unanswerable, for the reason on slide 7.

**"Who exactly is the customer?"** Whoever is exposed to one country rather than to total volume:
an importer requalifying a supplier, a lender behind either side, a carrier running that route. We
are still testing which of those the data serves best, and that is a better answer than naming one
confidently. An earlier version of this project named port and terminal operators. We tested it
and dropped it, because displaced volume arrives from a different country through much the same
US customs districts.

**"Five percent of what, exactly?"** The median over 1,350 action and product group pairs. Collapse
it to one number per action and the median is 1.3 percent, so the slide is the conservative
version.

**"Your copper chart recovers, so what is the problem?"** Correct, and we are not claiming copper
proves anything. It is on slide 2 to explain front-loading. In tonnage copper goes from 293
thousand tonnes in July 2025 down to 93 thousand in November and back to 245 thousand by August
2026. That is one product and one event. The measurement is the within product across origin
design on slide 8.

**"Why not just watch the data and react?"** That is slide 3. The first usable data lands about
five weeks after the month closes, and the decision is on announcement day.
