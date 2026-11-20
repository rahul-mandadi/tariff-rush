# Presentation 2, spoken script

Generated from the speaker notes in `slides/Mandadi_Khalsa_Presentation2_v3.pptx`. Do not edit this
file: change the notes in `slides/build_deck2c.py`, rebuild, then run `python3 slides/write_script2.py`.

**1610 words.** At a careful 130 words a minute that is 12:23; at a normal 145, 11:06.
Rahul, slides 1 to 8: 913 words, about 6:18. Raunak, slides 9 to 13: 697 words, about 4:48.
Per-slide times below are at the normal pace. Rehearse once with a clock.

You do not have to say it word for word. Keep the numbers exact.

---

## Rahul

### Slide 1. Borrowed or Real

*about 0:12*

We're Rahul and Raunak. Our project asks a simple question: when the U.S. puts a duty on imports, does the business come back afterwards, or is it gone?

### Slide 2. What this project is about.

*about 0:46*

Here's the project in three parts.

The problem. When the U.S. puts a duty on a product from one country, imports from that country often fall. We want to know if they come back.

Who cares. Picture an analyst at a U.S. company that imports goods. They track many products hit by duties. If a drop will pass, they can wait. If it lasts, they may need another supplier. They can't look into every decline, so they need to know which ones matter.

The data science problem. Using only public trade data, we predict which declines will last. Then we put those first on the list.

**If asked:**

- If asked what changed since Presentation 1: last time we asked three questions. Can we see a rush coming? What happens after the duty? How long does it last? Public data couldn't tell a rush apart from normal growth. So we focused on the last two, using antidumping cases, and added the forecast.

### Slide 3. Copper came back, but not the taxed part.

*about 0:51*

Our title asks if the drop is borrowed or real. Borrowed means buyers bought early and will come back. Real means the business has moved somewhere else.

Copper got us started. In August 2025 the U.S. put a 50% duty on some copper products. Total copper imports fell, then came back. So it looked borrowed.

But look at what the duty actually taxed. Wire, tubes and sheets fell from about 49 thousand tonnes a month to 27, and stayed there. Refined copper wasn't taxed, and that's what came back.

So the total hid the real story. We have to look at the exact products a duty names. But copper is one example. So we turned to hundreds of past duty cases.

**If asked:**

- If asked about the jump in refined copper just before the duty: buyers brought copper in ahead of the 2025 duty. That's a different kind of tariff. In antidumping cases we find no clear rush.
- If asked why copper, when the method uses antidumping cases: copper shows why we look at the exact products. Its duty taxed every country, so there's no untaxed country to compare with. That's also why the 2025 tariffs are not in the method.

### Slide 4. What we did, in four steps.

*about 0:38*

Here's what we did, in four steps. The marker at the top of each slide shows which step we're on.

One, collect. We read every duty notice since 2015, found 502 cases, and matched them to monthly import data.

Two, measure. For each case, we compared the named country with other countries selling the same product.

Three, predict. Four months after a duty, we rank the declines by how likely they are to last.

Four, test. We checked that ranking on 44 monthly lists from the past.

All four are done.

### Slide 5. We follow one product from one country.

*about 0:43*

Most tariffs in the news tax almost every country at once. That leaves nobody untaxed to compare with.

There's a narrower kind of duty, called antidumping and countervailing duties. Each one names one product from one country. For example, mattresses from Vietnam.

Other countries keep selling mattresses here. So we follow Vietnam's share, month by month, next to theirs. Anything that hits all mattresses, like inflation, hits them all and cancels out.

As a check, we also run everything on a fake date, two years before each case. If the drop shows up there too, it comes from our method, not the duty.

**If asked:**

- antidumping duties answer goods sold below fair value. Countervailing duties answer government subsidies.

### Slide 6. Where duties stayed: 31% below rivals.

*about 1:06*

Here's what happens after the duty. Zero is where the country stood against its rivals a year and a half before the duty.

The red line is the 326 cases where the trade commission kept the duty, so it became permanent. Averaged over the 18 months after, the country was about 31 percent below its rivals. By the last six months it was about 37 percent below, and still falling.

The grey line is the fake date. Same cases, same method, two years earlier. It shows no drop. If anything, it drifts up about 6 percent. So the drop isn't something our method creates.

That still doesn't prove the duty alone caused it. Other things could matter, like which companies get named in a case.

Two more things. The line sits a little above zero before the duty, but there's no clear rush of buying. And where the duty was lifted, there's no lasting fall.

**If asked:**

- If asked for the exact numbers: minus 0.37 log points, standard error 0.065. The fake date is plus 0.06, standard error 0.03, on the 283 cases with enough earlier data.
- If asked whether the country fell or its rivals grew: we measure its share against its rivals, not its imports alone. Two things we can add. The chance the product is traded at all falls 9 points. And quantity falls about as much as dollars. Where the trade went instead, we have not measured.
- If asked about goods rerouted through another country: Census records the declared country of origin. Relabelled goods would count as the other country's. We can't separate that. It's a limit.

### Slide 7. More than half did not come back.

*about 0:58*

Now case by case. First, what we mean by recovery.

A country fell if its share dropped at least a fifth below its level before the case. It came back if its share returned to that level and stayed there three months in a row, within 18 months.

These are the 380 cases with a full 18 months of data so far. 26 percent did not fall in the first six months. 17 percent fell and came back. 57 percent fell and did not come back. That includes 16 percent where the country had stopped selling the product completely a year later.

On the fake date, only 21 percent fell without coming back.

So for these duties, the answer is closer to real than borrowed. But that's an average. An analyst needs to know which declines will last.

**If asked:**

- If asked why 42 and 16 make 58: rounding. Unrounded, it's 57.3 percent.

### Slide 8. Which declines should an analyst check first?

*about 1:03*

Back to our analyst. Here's how one month plays out, with a real list.

In September 2024, new duties start, including one on epoxy resins from Taiwan. Census publishes trade data about two months late. So by January 2025, month 4, the analyst can see the first three months after the duty.

That month, 36 declines have fallen and not come back. The analyst can check about seven. Which ones?

That's where our model comes in. It ranks the list, and the analyst checks the top seven. Eighteen months after the duty, in March 2026, we see which ones came back. Six of the model's seven picks had not. Picking seven at random would have found about four.

The simplest rule is to check the biggest drops first. It needs no model, and anyone can do it with public data. That's the bar our model has to clear.

*Handoff:* Raunak will show how our model orders that list, and whether it beats the biggest drops.

**If asked:**

- If asked whether the biggest-drop rule did as well this month: about as well. Ten declines were tied at no imports at all, and 8 of those 10 had not come back. The model's edge shows across all 44 lists, which Raunak covers.
- If asked what checking means: looking into that decline with the company's own supplier information. What the analyst does next, we did not test.
- If asked why month 4: it's a checkpoint we studied, not a business deadline. On the day a duty starts, facts like the duty rate don't predict recovery any better than past averages. So we wait for some trade data.

---

## Raunak

### Slide 9. How the model ranks each month's list.

*about 1:00*

Thanks, Rahul. Here's how the model orders the list.

For each decline, the model looks at 23 inputs that were public at the time. The latest share Census has published. How fast it is falling. Facts about the case, like the duty rate. And what the market looked like before.

The model is gradient boosting. It's many small decision trees, each fixing the mistakes of the ones before. It gives each decline a chance of not coming back by month 18. The list is sorted by that chance.

We tested it the way an analyst would have used it. Each prediction only used older cases whose outcomes were already known.

The chart shows what the model relies on. We scramble one input and see how much worse the forecast gets. The latest share matters most, about five times more than the next one.

**If asked:**

- If asked how it was tuned: the settings were tuned on the older cases only, keeping each investigation together.
- If asked why month 4: we chose it after seeing the test accuracy, so months 6 and 8 are our checks.
- If asked what share just before the duty means: the share in the six months before the duty, compared with its earlier level. The report calls it the pre-case rush.

### Slide 10. What the model hands the analyst.

*about 1:02*

So what does the model actually give the analyst? This is its real output for January 2025.

That month, 36 declines were on the list. The model sorted them, and the analyst checks the top fifth, about seven.

Each row is one product from one country. You see how far its share has fallen, and the model's chance it doesn't come back. The last column is where the biggest-drop rule would put it. Brazil's ferrosilicon is on twice because it is two product codes.

Five of the model's top seven are 20th or lower on that rule. Why, if the latest share matters most? Once a share is below about 60 percent of its earlier level, falling further barely changes the model's answer. Then the case and the market decide the order.

Row two is epoxy resins from Taiwan. Let's follow it.

**If asked:**

- If asked about the chances: they run about 6 points high on average (report Appendix K). So the analyst uses the order, not the exact number.
- If asked about the 0% rows: ten declines had no imports in the latest three months, so they tie for first on biggest drop.

### Slide 11. Later: Taiwan had not come back.

*about 0:54*

This is row two, epoxy resins from Taiwan. The duty started in September 2024.

The red line is what the analyst could see in January. Census runs two months behind, so the data stops at month 2. Taiwan's share had been sliding even before the duty. By then it was 42 percent of its level a year and a half before. The biggest-drop rule ranked it 20th, so it wouldn't get checked. The model ranked it 2nd.

The grey line is what happened next. By month 18, March 2026, Taiwan was at 26 percent. It never came back. And of the model's top seven that month, six never came back.

But one month doesn't prove the model is better. For that, we need every month.

**If asked:**

- If asked what 42 percent means: Taiwan went from 10.3 percent of these imports to 4.4 percent. That's 42 percent of its old share, not 42 percent of all U.S. imports.

### Slide 12. The model's picks: 82% did not come back.

*about 1:00*

Now every month, not just one. We ran this on 44 monthly lists, from 2020 to 2025.

Each month, the analyst checks the top fifth of the list. That's about 187 checks in total. Then we wait until month 18 and ask: did each checked decline come back?

With the model's order, 82 percent of the checks found declines that never came back. With biggest drop first, 70 percent. With a random order, 62 percent, the rate for all the declines on these lists.

The line shows the same at every share the analyst might check, from 5 percent of the list to half of it.

So with the same 187 checks, the model finds about 22 more lasting declines. The gap is 12 points. Our 90 percent range for it runs from 3.9 to 15.7, so it is clearly above zero.

**If asked:**

- If asked whether it holds up: yes at every share on the chart. Yes at months 6 and 8: 88 against 76, and 89 against 81. Yes without the biggest case. And three other models score 81 to 84 percent.
- If asked why 62 here and 57 on slide 7: different groups. 57 is all 380 cases, including ones that never fell. 62 is the declines on the 2020 to 2025 lists, counted one product at a time.

### Slide 13. What this means.

*about 0:53*

Three things to take away.

First, after these duties, the drop is mostly real. More than half of the named countries fell and still hadn't come back 18 months later.

Second, at month 4, the model's list finds more lasting declines than just checking the biggest drops.

Third, the limits. We haven't tested this with real analysts. How many they can check is our assumption, though the result holds from 5 to 50 percent. And we predict a country's recovery in a product, not whether one company survives.

What's next. On November 15 we froze a forecast of 197 declines whose outcomes aren't known yet. We'll score it as Census publishes the data, from December to early 2028. Thank you.

**If asked:**

- If asked how many get scored: 184. One month's list, 13 declines, already had its outcome public when we froze it.

---

## Questions, and the backup slide that answers each

| question | backup slide |
| --- | --- |
| What does a term mean? | 15. Terms we use. |
| Why gradient boosting and not another model? | 16. Other models give the same answer. |
| What could the analyst see in January, before the outcome? | 20. Taiwan, January 2025: what the analyst saw. |
| Why a fifth? What if the fall cutoff moves? | 17. A different cutoff, the same answer. |
| Why aren't the no-import rows at the top of the list? | 18. Below 60%, how far it fell matters little. |
| How do the model's picks differ from the biggest drops? | 19. Two ways to pick 7 of 36. |
| What if the analyst can check more, or fewer? | 21. Review these first: 82% stayed down. |
| How accurate is the model, and when does it start to work? | 22. By month 4, the forecast ranks them better. |
| What happens when the trade commission lifts the duty? | 23. Losses persist in cases that become orders. |
| How did you get from the notices to 502 cases? | 24. From 10,730 notices to 502 cases. |
| How exactly is the comparison built? | 25. How we measure it, product by product. |
| Do importers actually change suppliers? | 26. Buyers respond to duties, but slowly. |
| Did copper's total really come back? | 27. Copper's total imports came back. |
| How much of copper did the duty cover? | 28. But most copper was outside this duty. |
| What about inflation, and the other data checks? | 29. What the checks confirmed. |
| Presentation 1 feedback: the unusual-month score | 30. How we spot an unusual month. |
| Presentation 1 feedback: dollars against quantity | 31. Dollars alone can fool you. |
