# Raunak, this is your half

Slides 5 to 8. Rahul takes 1 to 4 and hands over by saying your name, at about 3:42.

**Your half is about 6:07.** The whole talk has to come in under 10 minutes, so there is not much slack. The same words are in the speaker notes in the pptx, under SAY THIS on each slide, so you can present straight off the notes.

You do not have to say it word for word. Say it however it comes out naturally. The one thing to keep exact is the numbers.

---

## What Rahul has already said, so you can pick up from it

- A tariff is a tax on imports. It gets announced one day and starts on a later day, and importers rush to get goods in before it starts. Then imports drop.
- Our question is what that drop means. Borrowed means the goods just came early and it evens out. Real means the business went somewhere else and stayed there.
- The reason anyone cares: somebody has to decide on announcement day whether to find a new supplier, and the official data does not arrive for about two months.
- He ends on our three questions, then says your name.

---

## Slide 5. What we have

*1:28*

**What this slide is for:** This is the data slide. You are telling them where the numbers come from, what one row is, and why we pulled it at ten digits instead of something broader. The ten digit bit is the part that matters later, so do not rush it.

**Say:**

Thanks Rahul. Two data sources, both free and public.

Figure 3 on the left is US Census trade data, every month from January 2015 to August 2026. 140
months, about 15.9 million rows. The last bar is grey because 2026 is only eight months so far.

Table 1 on the right shows what one row is. One product, one country, one month. This product
code, from Chile, March 2025, 715 million dollars and about 74 million kilograms.

Now look at that first column. Those are eight digit codes, and we pull our data at ten digits.
Here's why. A tariff order doesn't say "copper". It lists specific eight digit codes. And ten
digits sit inside eight, so we can match a tariff to exactly the products it names instead of
guessing.

How do we know the data's right? Add up 2017 and we get two point three four trillion dollars. The
published figure is two point three four trillion. And all 140 months check against a separate
total the API gives us.

Second source is the Federal Register. Nearly two thousand eight hundred documents, a hundred and
thirty four real tariff actions.

**While you say it:** Point left for Figure 3, then right for Table 1. Say the figure numbers out loud.

---

## Slide 6. Unusual is not the same as tariffed

*1:22*

**What this slide is for:** This is the honest slide. You show the first thing we tried, and then you say why it is not enough. The thing to get across is that finding a weird month is not the same as finding a tariff. Cocoa is the example that proves it.

**Say:**

The first thing we tried was to find the months that look weird.

For each product group, we used the earlier years to work out what it would normally have done.
Then we drew a band around that for ordinary month to month wobble. Anything outside the band
counts as unusual.

Figure 4 ranks the ten groups that went furthest outside their own normal range in 2025. The scale
along the bottom is how many times outside the band, so one is right at the edge.

Some look like tariff stories, like organic chemicals and pharmaceuticals, both under tariff
threat in 2025.

But look at the red ones. Silk is only about 55 million dollars a year, so almost any month looks
extreme. And cocoa's up there because cocoa prices roughly tripled after bad harvests in West
Africa. We measure in dollars, so a price spike looks exactly like a surge in volume.

So the detector finds unusual months, but it has no idea why. It can't tell a tariff from a bad
harvest. That's the next slide.

**While you say it:** Point at the bottom axis when you explain the scale, then at the red bars.

---

## Slide 7. And this is where it nearly came apart

*1:46*

**What this slide is for:** This is the most important slide in the deck. You are telling them our first attempt found nothing, and then telling them exactly why. If you only nail one slide, nail this.

**Say:**

A tariff order never says "chapter 74, copper". It points at a list of specific eight digit codes,
usually in a separate legal notice. So if you haven't read those lists, there's only one thing you
can do. You mark a whole product group as tariffed whenever any action touches anything inside it.

That's what we did. And we got nothing.

So we went and read the lists. Nine thousand and eighty three eight digit codes.

Figure 5 is what we found. Each bar counts a tariff action paired with a product group. The
typical one covers about five percent of that group's value, and the red on the left is a third of
them covering less than one percent.

Copper again. Ten actions touch copper. Three cover more than half of it. The other seven cover
less than one percent.

And that's why we got nothing. If you label a product group tariffed when ninety-five percent of
it wasn't, the real reaction in that five percent gets averaged away by everything that didn't
move. The zero wasn't telling us about the world. It was telling us about our ruler.

It was one of three reasons, and it's the one anyone doing this would hit.

The fix is to work at eight digits, where a tariff either names a product or it doesn't.
Everything from here is built that way.

**While you say it:** Slow down. This is the slide that matters most. Point at the red bars on the left.

---

## Slide 8. Where we are

*1:30*

**What this slide is for:** This is the close. A list of what exists, how we will measure it, how we will check it is real, and one thing for them to take away.

**Say:**

Built and checked. We've got 140 months of trade at the level tariffs are actually written, and it
adds up to the published totals.

We've got a detector that finds unusual months, and we're upfront that on its own it can't tell a
tariff from a price shock.

134 tariff actions, with the real product lists behind each one.

How we'll measure it, and this is what fixes the detector. Instead of comparing a product to its
own past, we compare one product across countries in the same month. A price shock moves every
country together so it cancels out. A tariff hits one country, so it doesn't.

How we'll know it's real. Every estimate gets paired with a placebo, which is the exact same
calculation with every event shifted back two years. If it doesn't separate from its placebo, we
don't report it. That's already killed three methods we built.

Next, question one, then two and three for the final report.

And the takeaway, even if you never touch tariff data. Don't measure this at product group level.
The typical action touches five percent, so a real effect averages away to nothing.

Happy to take questions.

**While you say it:** Stand still and let the list do the work. Slow down for the last two lines.

---

## The numbers to get exactly right

Everything else you can say in your own words. These three are the argument on slide 7:

- **five percent** : the typical tariff action covers about 5% of its product group's value
- **a third** : a third of them cover less than 1%
- **ninety-five percent** : so about 95% of what you measure was never tariffed

And the sentence that carries it, which is worth saying slowly:

> If you label a product group tariffed when ninety-five percent of it wasn't, the real
> reaction in that five percent gets averaged away by everything that didn't move.

---

## If someone asks you something

These are the ones likely to land on your slides. Short answers are fine, and "we are still testing that" is a real answer. Nobody expects finished results.

**"So is there a rush?"**

We have the data and the product level matching to answer it now. The product group version of the question was unanswerable, for the reason on slide 7.

**"Who exactly is the customer?"**

Whoever is tied to one country rather than to overall volume: an importer looking for a new supplier, a lender behind either side, a carrier running that route. We are still working out which of those the data helps most. An earlier version of this project said port and terminal operators; we tested that and dropped it, because the goods that stop coming from one country just arrive from another, through much the same US ports.

**"Five percent of what, exactly?"**

It is the middle value across 1,350 pairs of one tariff action and one product group. If you work it out per action instead, the middle value is 1.3 percent, so the slide uses the safer number.

**"What were the other two reasons?"**

First, most of the dates we have come from notices that just put an earlier decision into effect. So the gap between the date we hold and the start date is only about nine days, which leaves almost no run-up to measure. The copper story answers that one: the rush runs on news, not on paperwork. Second, we had lumped all the supplying countries together, which comparing across countries fixes.

**"Your copper chart recovers, so what is the problem?"**

Correct, and we are not claiming copper proves anything. In tonnage it goes 293 thousand tonnes in July 2025, down to 93 thousand in November, back to 245 thousand by August 2026. One product, one event. It is on slide 2 to explain front-loading.

**"Why not just watch the data and react?"**

That is slide 3. The first usable data lands about five weeks after the month closes, and the decision is on announcement day.

**"What is your data science problem, in technical terms?"**

Classification for whether a surge occurs, regression for how large, and duration analysis with right-censoring for how long the aftermath lasts.

---

## If you want to swap

Slide 7 is the hardest one and it is in your half. If you would rather Rahul took 7 and you closed on 8, that works and it is easy to switch. Slide 8 is a list and a takeaway line. Just say so before the rehearsal rather than on the day.

