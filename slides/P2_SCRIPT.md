# Presentation 2, spoken script

Generated from the speaker notes in `slides/Mandadi_Khalsa_Presentation2_v3.pptx`. Do not edit this
file: change the notes in `slides/build_deck2c.py`, rebuild, then run `python3 slides/write_script2.py`.

**1472 words.** At a careful 130 words a minute that is 11:19; at a normal 145, 10:09.
Rahul, slides 1 to 8: 841 words, about 5:48. Raunak, slides 9 to 13: 631 words, about 4:21.
Per-slide times below are at the normal pace. Rehearse once with a clock.

You do not have to say it word for word. Keep the numbers exact.

---

## Rahul

### Slide 1. Borrowed or Real

*about 0:12*

We're Rahul and Raunak. Our project asks a simple question: when the U.S. puts a duty on imports, does the business come back afterwards, or is it gone?

### Slide 2. What this project is about.

*about 0:39*

Here's the project in three parts.

The problem. When the U.S. puts a duty on a product from one country, imports from that country often fall. We want to know if they come back.

Who cares. Picture an analyst at a U.S. company that imports goods. They track many products hit by duties. They can't look into every decline, so they need to know which ones matter.

The data science problem. Using only public trade data, we predict which declines will last. Then we put those first on the list.

**If asked:**

- If asked what changed since Presentation 1: last time we asked three questions. Can we see a rush coming? What happens after the duty? How long does it last? Public data couldn't tell a rush apart from normal growth. So we focused on the last two, using antidumping cases, and added the forecast.

### Slide 3. Copper came back, but not the taxed part.

*about 0:58*

Our title asks if the drop is borrowed or real. Borrowed means buyers bought early and will come back. Real means the business has moved somewhere else.

Copper got us started. In August 2025 the U.S. put a 50% duty on some copper products. Total copper imports fell, then came back. So it looked borrowed.

But look at what the duty actually taxed. Wire, tubes and sheets fell from about 49 thousand tonnes a month to 27, and stayed there. Refined copper wasn't taxed, and that's what came back.

So the total hid the real story. We have to look at the exact products a duty names. But copper is one example, and every country paid the duty, so there's no one to compare with. That's why we turned to hundreds of past duty cases.

**If asked:**

- If asked why copper, when the method uses antidumping cases: copper shows why we look at the exact products. Its duty taxed every country, so there's no untaxed country to compare with. That's also why the 2025 tariffs are not in the method.

### Slide 4. What we did, in four steps.

*about 0:46*

Here's what we did, in four steps. The marker at the top of each slide shows which step we're on.

One, collect. We read every duty notice since 2015, found 502 cases, and matched them to monthly import data.

Two, measure. For each case, we compared the named country with other countries selling the same product.

Three, predict. Four months after a duty, we rank the declines by how likely they are to last.

Four, test. We checked that ranking on 44 past months.

All four are done. One test is still running: a forecast we froze on November 15. We'll score it as new data comes out.

### Slide 5. We follow one product from one country.

*about 0:43*

Most tariffs in the news tax almost every country at once. That leaves nobody untaxed to compare with.

There's a narrower kind of duty, called antidumping and countervailing duties. Each one names one product from one country. For example, mattresses from Vietnam.

Other countries keep selling mattresses here. So we follow Vietnam's share, month by month, next to theirs. Anything that hits all mattresses, like inflation, hits them all and cancels out.

We read every duty notice since 2015 and matched them to import data: 502 cases. As a check, we also run everything on a fake date, two years before each case.

**If asked:**

- antidumping duties answer goods sold below fair value. Countervailing duties answer government subsidies.

### Slide 6. Where duties stayed: 31% below rivals.

*about 1:02*

Here's what happens after the duty. Zero is where the country stood against its rivals before the case.

The red line is the 326 cases where the trade commission kept the duty, so it became permanent. On average, the country fell about 31 percent against its rivals over the next 18 months. It was still falling at the end: about 37 percent down in months 13 to 18.

The grey line is the fake date. Same cases, same method, two years earlier. It shows no drop. If anything, it drifts up about 6 percent. So the drop isn't something our method creates.

That still doesn't prove the duty alone caused it. Other things could matter, like which companies get named in a case.

Two more things. There's no clear rush of buying before the duty. And where the duty was lifted, there's no lasting fall (backup).

**If asked:**

- If asked for the exact numbers: minus 0.37 log points, standard error 0.065. The fake date is plus 0.06, standard error 0.03, on the 283 cases with enough earlier data.
- If asked whether the country fell or its rivals grew: we measure its share against its rivals, not its imports alone. Two things we can add. The chance the product is traded at all falls 9 points. And quantity falls about as much as dollars. Where the trade went instead, we have not measured.
- If asked about goods rerouted through another country: Census records the declared country of origin. Relabelled goods would count as the other country's. We can't separate that. It's a limit.

### Slide 7. More than half did not come back.

*about 0:50*

Now case by case. First, what we mean by recovery.

A country fell if its share dropped at least a fifth below its level before the case. It came back if its share returned to that level and stayed there three months in a row, within 18 months.

Across 380 cases, 26 percent never fell. 17 percent fell and came back. 57 percent fell and did not come back. That includes 16 percent where the country had stopped selling the product completely a year later.

On the fake date, only 21 percent fell without coming back.

So for these duties, the answer is closer to real than borrowed. But that's an average. An analyst needs to know which declines will last.

### Slide 8. Which declines should an analyst check first?

*about 0:36*

Back to our analyst. They can't look into every decline. So the question is: which ones first?

Four months after a duty, Census has usually published two months of data since it started. By then, some declines are visible. Each month's list holds every product from a country that has fallen and not yet recovered.

The simplest rule is to check the biggest drops first. It needs no model, and anyone can do it with public data. That's the bar our model has to clear.

*Handoff:* Raunak will show how our model orders that list, and whether it beats the biggest drops.

**If asked:**

- If asked what checking means: looking into that decline with the company's own supplier information. What the analyst does next, we did not test.
- If asked why month 4: it's a checkpoint we studied, not a business deadline. On the day a duty starts, facts like the duty rate don't predict recovery any better than past averages. So we wait for some trade data.

---

## Raunak

### Slide 9. How the model ranks each month's list.

*about 1:01*

Thanks, Rahul. Here's how the model orders the list.

For each decline, the model looks at 23 inputs that were public on the decision date. The latest share Census has published. How the fall has gone so far. Facts about the case, like the duty rate. And what the market looked like before.

The model is gradient boosting. It's many small decision trees, each fixing the mistakes of the ones before. It gives each decline a chance of not recovering by month 18. The list is sorted by that chance.

We tested it the way an analyst would have used it. Each prediction only used older cases whose outcomes were already known.

The chart shows what the model relies on. We scramble one input and see how much worse the forecast gets. The latest share matters most, about five times more than the next one.

**If asked:**

- If asked how it was tuned: the settings were tuned on the older cases only, keeping each investigation together.
- If asked why month 4: we chose it after seeing the test accuracy, so months 6 and 8 are our checks.
- If asked what share just before the duty means: the share in the six months before the duty, compared with its earlier level. The report calls it the pre-case rush.

### Slide 10. What the model hands the analyst.

*about 0:44*

So what does the model actually give the analyst? This is its real output for January 2025.

That month, 36 declines were on the list. The model sorted them, and the analyst checks the top seven.

Each row is one product from one country. You see how far its share has fallen, and the model's chance it stays down. The last column is where the biggest-drop rule would put it.

Five of the model's top seven are 20th or lower on that rule. So the model isn't just picking the deepest falls.

Row two is epoxy resins from Taiwan. Let's follow it.

**If asked:**

- If asked about the chances: they run about 6 points high on average (report Appendix K). So the analyst uses the order, not the exact number.
- If asked why Brazil's ferrosilicon appears twice: it is listed under two product codes.
- If asked why the 0% rows aren't all at the top: ten declines had no imports at all, so they tie for first on biggest drop. But below about 60 percent of the old share, the model treats them all about the same. Other inputs decide the order (backup).

### Slide 11. Later: Taiwan had not recovered.

*about 0:44*

This is row two, epoxy resins from Taiwan. The duty started in September 2024.

The red line is what the analyst could see in January. Taiwan's share had dropped to 42 percent of where it was before the duty. The biggest-drop rule ranked it 20th, so it wouldn't get checked. The model ranked it 2nd.

The grey line is what happened next. By month 18, March 2026, Taiwan was at 26 percent. It never recovered. And of the model's top seven that month, six never recovered.

But one month doesn't prove the model is better. For that, we need every month.

**If asked:**

- If asked what 42 percent means: Taiwan went from 10.3 percent of these imports to 4.4 percent. That's 42 percent of its old share, not 42 percent of all U.S. imports.

### Slide 12. The model's picks: 82% did not recover.

*about 0:54*

Now every month, not just one. We ran this on 44 monthly lists, from 2020 to 2025. Each prediction only used older cases whose outcomes were already known.

Each month, the analyst checks the top fifth of the list. That's about 187 checks in total. Then we wait until month 18 and ask: did each checked decline recover?

With the model's order, 82 percent of the checks found declines that never recovered. With biggest drop first, 70 percent. With a random order, 62 percent, which is just the overall rate.

So with the same 187 checks, the model finds about 22 more lasting declines. The gap is 12 points. Our 90 percent range for it runs from 3.9 to 15.7, so it is clearly above zero.

**If asked:**

- If asked whether it holds up: yes, if the analyst checks 10 or 30 percent instead. Yes at months 6 and 8: 88 against 76, and 89 against 81. Yes without the biggest case. And three other models score 81 to 84 percent (backup).

### Slide 13. What this means.

*about 0:58*

Three things to take away.

First, after these duties, the drop is mostly real. More than half of the named countries fell and still hadn't come back 18 months later.

Second, at month 4, the model's list finds more lasting declines than just checking the biggest drops.

Third, the limits. We haven't tested this with real analysts. How many they can check is our assumption. And we predict a country's recovery in a product, not whether one company survives.

What's next. On November 15 we froze a forecast of 197 declines whose outcomes aren't known yet. For one month's list, 13 declines, the outcome was already public. So the other 184 are the real test. We'll score them as Census publishes the data, starting in December and finishing in early 2028. Thank you.

---

## Questions, and the backup slide that answers each

| question | backup slide |
| --- | --- |
| What does a term mean? | 15. Terms we use. |
| Why gradient boosting and not another model? | 16. Other models give the same answer. |
| What could the analyst see in January, before the outcome? | 19. Taiwan, January 2025: what the analyst saw. |
| Why a fifth? What if the fall cutoff moves? | 17. A different cutoff, the same answer. |
| Why aren't the no-import rows at the top of the list? | 18. Below 60%, how far it fell matters little. |
| What if the analyst can check more, or fewer? | 20. Review these first: 82% stayed down. |
| How accurate is the model, and when does it start to work? | 21. By month 4, the forecast ranks them better. |
| What happens when the trade commission lifts the duty? | 22. Losses persist in cases that become orders. |
| How did you get from the notices to 502 cases? | 23. From 10,730 notices to 502 cases. |
| How exactly is the comparison built? | 24. How we measure it, product by product. |
| Do importers actually change suppliers? | 25. Buyers respond to duties, but slowly. |
| Did copper's total really come back? | 26. Copper's total imports came back. |
| How much of copper did the duty cover? | 27. But most copper was outside this duty. |
| What about inflation, and the other data checks? | 28. What the checks confirmed. |
| Presentation 1 feedback: the unusual-month score | 29. How we spot an unusual month. |
| Presentation 1 feedback: dollars against quantity | 30. Dollars alone can fool you. |
