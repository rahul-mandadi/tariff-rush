"""The words to actually say, one entry per talk slide.

Single source of truth. build_deck.py puts these into the speaker notes and write_script.py
writes slides/SCRIPT.md from them, so the deck and the script cannot drift apart. Earlier they
were two copies and they did drift: the notes pointed at a 9:15 script that was 9:03.

Written to be spoken, not read. Contractions throughout, because nobody says "it does not wait
for July" out loud. Every figure is named by number because the communication rubric asks for
figures to be referenced and interpreted, and in a talk that is something you say.
"""

WPM = 130          # a steady speaking pace, used for every timing in the deck
WHO = {1: "RAHUL", 2: "RAHUL", 3: "RAHUL", 4: "RAHUL",
       5: "RAUNAK", 6: "RAUNAK", 7: "RAUNAK", 8: "RAUNAK"}

SPEAK = {
1: """Hi everyone. I'm Rahul, this is Raunak, and our project is called Borrowed or Real.

Imports drop after a tariff starts. We want to know whether the goods just arrived early, or
whether the business left for good.

I'll take the first four slides.""",

2: """So, tariffs don't happen overnight. They get announced, and they take effect on a named date
later.

Figure 1 is monthly copper imports, in dollars. Here's July 2025, when a fifty percent duty was
announced. Here's August, when it started. Three weeks apart.

But look at what the line does. It doesn't wait for July. It starts climbing in February, and
nearly triples by the time of the announcement. Why? Because the investigation behind that tariff
was public months earlier. Everyone in the industry could see it coming.

So the rush doesn't start when a tariff becomes official. It starts when it becomes likely.

Then August, and it drops hard.

You'll also see it climb back up at the end. That's one product and one tariff, so we're not
reading anything into it. The measuring comes later.

That's front-loading. Goods that would have come in October came in June instead. Nothing got
created, it just moved forward in time. We call that borrowed, because the later months pay it
back.""",

3: """So why does this matter?

Because somebody has to make an expensive decision on announcement day, and the data they'd need
doesn't exist yet.

Figure 2 is that problem. Day zero, the tariff gets announced. If you're importing from the
country that just got hit, you have a decision. Wait it out, or go and find a new supplier?
Qualifying a new supplier takes months and real money.

And it isn't just importers. A bank that lent against that trade is asking the same question. So
is the carrier running that route.

Day thirty, the duty takes effect.

Day sixty-five is the first time official data shows what happened, because Census publishes about
five weeks after the month closes.

So by the time you've seen two bad months, the tariff's been in force for a quarter, and every one
of those decisions is already made.

That's the gap we're trying to close.""",

4: """So we turned that into three questions, and they're on the slide.

One, will there be a rush and how big. Classification, then regression.

Two, what happens after the duty starts. This is the hard one, and it's our title. Either the
goods were borrowed and come back, or the demand was lost for good, or the same goods now come
from a different country.

Three, how long it lasts. That's a duration problem, because some are still running at the end of
our data.

Today is about our data and its limits, not results. But we found something the hard way, and
Raunak's going to take you through it.

Raunak.""",

5: """Thanks Rahul. Two data sources, both free and public.

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

Second source is the Federal Register. We went through nearly two thousand eight hundred
documents, and a hundred and thirty four of them are real tariff actions.""",

6: """The first thing we tried was to find the months that look weird.

For each product group, we used the earlier years to work out what it would normally have done.
Then we drew a band around that for ordinary month to month wobble. Anything outside the band
counts as unusual.

Figure 4 ranks the ten groups that went furthest outside their own normal range in 2025. The scale
along the bottom is how many times outside the band, so one is right at the edge.

Some look like tariff stories. Organic chemicals and pharmaceuticals were both under open tariff
threat in 2025.

But look at the red ones. Silk is only about 55 million dollars a year, so almost any month looks
extreme. And cocoa's up there because cocoa prices roughly tripled after bad harvests in West
Africa. We measure in dollars, so a price spike looks exactly like a surge in volume.

So the detector finds unusual months, but it has no idea why. It can't tell a tariff from a bad
harvest. That's the next slide.""",

7: """A tariff order never says "chapter 74, copper". It points at a list of specific eight digit codes,
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

It was one of three reasons, and it's the one that isn't just our problem. Anyone doing this
would hit it.

The fix is to work at eight digits, where a tariff either names a product or it doesn't.
Everything from here is built that way.""",

8: """Built and checked. We've got 140 months of trade at the level tariffs are actually written, and it
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

Next, question one first, then two and three for the final report.

And the takeaway, even if you never touch tariff data. Don't measure this at product group level.
The typical action touches five percent, so a real effect averages away to nothing.

Happy to take questions.""",
}

# physical cues, kept out of the spoken text so nothing on the page gets read aloud by mistake
CUE = {
1: "Look up, not at the screen. Nobody needs the slide for this bit.",
2: "Point at the two red dashed lines when you name July and August, then sweep back along the\n"
   "climb when you say February. The sweep is the whole point of the slide.",
3: "Walk the three dots left to right as you name them. Pause on day sixty-five.",
4: "Do not read the sub-lines under each question, they are already on the slide.",
5: "Point left for Figure 3, then right for Table 1. Say the figure numbers out loud.",
6: "Point at the bottom axis when you explain the scale, then at the red bars.",
7: "Slow down. This is the slide that matters most. Point at the red bars on the left.",
8: "Stand still and let the list do the work. Slow down for the last two lines.",
}

# only said if someone asks. Never read these out as part of the talk.
QA = [
("So is there a rush?",
 "We have the data and the product level matching to answer it now. The product group version of "
 "the question was unanswerable, for the reason on slide 7."),
("Who exactly is the customer?",
 "Whoever is tied to one country rather than to overall volume: an importer looking for a new "
 "supplier, a lender behind either side, a carrier running that route. We are still working out "
 "which of those the data helps most. An earlier version of this project said port and terminal "
 "operators; we tested that and dropped it, because the goods that stop coming from one country "
 "just arrive from another, through much the same US ports."),
("Five percent of what, exactly?",
 "It is the middle value across 1,350 pairs of one tariff action and one product group. If you "
 "work it out per action instead, the middle value is 1.3 percent, so the slide uses the safer "
 "number."),
("What were the other two reasons?",
 "First, most of the dates we have come from notices that just put an earlier decision into "
 "effect. So the gap between the date we hold and the start date is only about nine days, which "
 "leaves almost no run-up to measure. The copper story answers that one: the rush runs on news, "
 "not on paperwork. Second, we had lumped all the supplying countries together, which comparing "
 "across countries fixes."),
("Your copper chart recovers, so what is the problem?",
 "Correct, and we are not claiming copper proves anything. In tonnage it goes 293 thousand tonnes "
 "in July 2025, down to 93 thousand in November, back to 245 thousand by August 2026. One product, "
 "one event. It is on slide 2 to explain front-loading."),
("Why not just watch the data and react?",
 "That is slide 3. The first usable data lands about five weeks after the month closes, and the "
 "decision is on announcement day."),
("What is your data science problem, in technical terms?",
 "Classification for whether a surge occurs, regression for how large, and duration analysis with "
 "right-censoring for how long the aftermath lasts."),
]


def secs(n):
    return len(SPEAK[n].split()) / WPM * 60


def clock(n):
    return sum(secs(i) for i in range(1, n + 1))


def ms(t):
    return f"{int(t)//60}:{int(t)%60:02d}"
