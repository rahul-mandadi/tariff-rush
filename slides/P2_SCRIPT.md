# Presentation 2, spoken script

Generated from the speaker notes in `slides/Mandadi_Khalsa_Presentation2_v3.pptx`. Do not edit this
file: change the notes in `slides/build_deck2c.py`, rebuild, then run `python3 slides/write_script2.py`.

**1931 words.** At a careful 130 words a minute that is 14:51; at a normal 145, 13:19.
Rahul, slides 1 to 8: 1015 words, about 7:00. Raunak, slides 9 to 14: 916 words, about 6:19.
Per-slide times below are at the normal pace. Rehearse once with a clock.

You do not have to say it word for word. Keep the numbers exact.

---

## Rahul

### Slide 1. Borrowed or Real

*about 0:12*

We're Rahul and Raunak. Our project asks a simple question: when the U.S. puts a duty on imports, does the business come back afterwards, or is it gone?

### Slide 2. What this project is about.

*about 0:46*

What this project is about, in three parts.

The problem. After a U.S. duty, imports from the named country often fall. Do they come back? Our title asks if the drop is borrowed or real. Borrowed: buyers bought early and will come back. Real: the business has moved somewhere else.

Who needs it. An analyst at a U.S. importer, who can check only a few declines. They track many products hit by duties. If a drop will pass, they can wait. A lasting one may mean a new supplier.

The data science problem. We predict which declines will last, from public trade data, and put those first on the list.

**If asked:**

- If asked what changed since Presentation 1: last time we asked three questions. Can we see a rush coming? What happens after the duty? How long does it last? Public data couldn't tell a rush apart from normal growth. So we focused on the last two, using antidumping cases, and added the forecast.

### Slide 3. Copper came back, but not the taxed part.

*about 0:48*

Copper came back, but not the taxed part. Copper is what got us started.

In August 2025 the U.S. put a 50% duty on some copper products. Total copper imports fell, then came back. So it looked borrowed.

But look at what the duty actually taxed. In red, taxed by the 2025 duty: wire, tubes and sheets fell from about 49 thousand tonnes a month to 27, and stayed there. In grey, not taxed: refined copper, and that's what came back.

So the total hid the real story. We have to look at the exact products a duty names. But copper is one example. So we turned to hundreds of past duty cases.

**If asked:**

- If asked about the jump in refined copper just before the duty: buyers brought copper in ahead of the 2025 duty. That's a different kind of tariff. In antidumping cases we find no clear rush.
- If asked why copper, when the method uses antidumping cases: copper shows why we look at the exact products. Its duty taxed every country, so there's no untaxed country to compare with. That's also why the 2025 tariffs are not in the method.

### Slide 4. What we did, in four steps.

*about 1:07*

What we did, in four steps. The marker at the top of each slide shows which step we're on.

One, collect. 10,730 duty notices since 2015. From them, 502 cases, matched to U.S. imports.

Two, measure. The named country against its rivals, for 18 months after the duty. We use the cases with all 18 months of data.

Three, predict. At month 4: each decline's chance of not coming back by month 18. That yes or no is what the model predicts.

Four, test. Each month's list, against a simple rule: check the biggest drops first.

The bars show the years. Monthly U.S. imports, January 2015 to August 2026. In red, the test: 44 monthly lists, 2020 to 2025.

And a fair test: each year's lists are ranked by a model trained only on cases already finished, using data out by month 4. So the model never sees the answer it is graded on.

**If asked:**

- If asked what "out by month 4" means: Census runs about two months behind. So at month 4 we use trade data through month 2, and notices already published.
- If asked how many were scored: 198 cases, 936 product and country pairs.

### Slide 5. We follow one product from one country.

*about 0:50*

We follow one product from one country. Most tariffs in the news tax almost every country at once. That leaves nobody untaxed to compare with.

Antidumping and countervailing duties are narrower: one product from one country, like mattresses from Vietnam. Antidumping answers goods sold below fair value. Countervailing answers goods helped by government subsidies.

Rivals keep selling it. Other countries keep selling mattresses here, so we compare Vietnam's share of U.S. mattress imports with theirs, month by month. Anything that hits all mattresses, like inflation, hits them all and cancels out.

A check: the same method on a fake date, two years earlier. If the drop shows up there too, it comes from our method, not the duty.

### Slide 6. Where duties stayed: 31% below rivals.

*about 1:16*

Where duties stayed, the named country averaged 31 percent below its rivals over the 18 months after. Zero on this chart is where it stood against them a year and a half before the duty.

The red line is the 326 cases where the trade commission kept the duty, so it became permanent. Averaged over the 18 months after, the country was about 31 percent below its rivals. By the last six months it was about 37 percent below, and still falling. The shading is where the true value likely falls, a 95 percent range.

The grey line is the fake date. Same cases, same method, two years earlier. It shows no drop. If anything, it drifts up about 6 percent. So the drop isn't something our method creates.

That still doesn't prove the duty alone caused it. Other things could matter, like which companies get named in a case.

Two more things. The line sits a little above zero before the duty, but there's no clear rush of buying. And where the duty was lifted, there's no lasting fall.

**If asked:**

- If asked for the exact numbers: minus 0.37 log points, standard error 0.065. The fake date is plus 0.06, standard error 0.03, on the 283 cases with enough earlier data.
- If asked whether the country fell or its rivals grew: we measure its share against its rivals, not its imports alone. Two things we can add. The chance the product is traded at all falls 9 points. And quantity falls about as much as dollars. Where the trade went instead, we have not measured.
- If asked about goods rerouted through another country: Census records the declared country of origin. Relabelled goods would count as the other country's. We can't separate that. It's a limit.

### Slide 7. More than half did not come back.

*about 1:00*

More than half did not come back. Now case by case. First, what we mean by recovery.

A country fell if its share dropped at least a fifth below its level before the case. It came back if its share returned to that level and stayed there three months in a row, within 18 months.

These are the 380 cases with a full 18 months of data so far. 26 percent did not fall in the first six months. 17 percent fell and came back. 57 percent fell and did not come back. That includes 16 percent where the country had stopped selling the product completely a year later.

On the fake date, only 21 percent fell without coming back.

So for these duties, the answer is closer to real than borrowed. But that's an average. An analyst needs to know which declines will last.

**If asked:**

- If asked why 42 and 16 make 58: rounding. Unrounded, it's 57.3 percent.

### Slide 8. Which declines should an analyst check first?

*about 1:01*

Which declines should an analyst check first? Here's how one month plays out, with a real list.

September 2024: new duties start, including one on epoxy resins from Taiwan. Then the data arrives, but Census runs about two months behind. So by January 2025, month 4, the analyst can see the first three months after the duty.

The list: 36 declines, fallen and not back yet. The analyst can check about seven. Which ones?

That's where our model comes in. The model ranks it: the most likely to last go first, and the analyst checks the top seven.

The answer comes at month 18, in March 2026. Six of the seven picks had not come back. Seven random picks would have found about four.

The obvious rule: check the biggest drops first. Anyone can do that with public data. Our model has to beat it.

*Handoff:* Raunak will show how our model orders that list, and whether it beats the biggest drops.

**If asked:**

- If asked whether the biggest-drop rule did as well this month: about as well. Ten declines were tied at no imports at all, and 8 of those 10 had not come back. The model's edge shows across all 44 lists, which Raunak covers.
- If asked what checking means: looking into that decline with the company's own supplier information. What the analyst does next, we did not test.
- If asked why month 4: it's a checkpoint we studied, not a business deadline. On the day a duty starts, facts like the duty rate don't predict recovery any better than past averages. So we wait for some trade data.

---

## Raunak

### Slide 9. How the model ranks each month's list.

*about 1:09*

Thanks, Rahul. How the model ranks each month's list, in three lines.

First, 23 public inputs, in four groups. The market before, like how concentrated it was. The case, like the duty rate. The fall so far, like the latest share Census has published. And the month, with the trade commission's vote once it is public.

Second, gradient boosting. It's many small decision trees, each fixing the mistakes of the ones before. It gives each decline a chance of not coming back by month 18, and the list is sorted by that chance.

Third, no automatic selection. The inputs were set before the list test and never changed.

Which inputs matter most? The chart shows what the model leans on. We scramble one input and see how much worse the forecast gets. The latest share matters most, about five times more than the next one.

And each prediction used only data out by month 4, and only older cases whose outcomes were known.

**If asked:**

- If asked how it was tuned: the number of trees was tuned on the older cases only, keeping each investigation together. The other settings were fixed by hand.
- If asked about the trade commission's vote: it's an input, but at month 4 it isn't public yet in any case. It only matters at later months.
- If asked why month 4: we chose it after seeing the test accuracy, so months 6 and 8 are our checks.
- If asked what share just before the duty means: the share in the six months before the duty, compared with its earlier level. The report calls it the pre-case rush.

### Slide 10. What the model hands the analyst.

*about 1:00*

What the model hands the analyst: its real output for January 2025.

That month, 36 declines were on the list. The model sorted them, and the analyst checks the top fifth, about seven.

Each row is one product from one country. You see how far its share has fallen, and the model's chance it doesn't come back. The last column is where the biggest-drop rule would put it. Brazil's ferrosilicon is on twice because it is two product codes.

Five of the model's top seven are 20th or lower on that rule. Why, if the latest share matters most? Once a share is below about 60 percent of its earlier level, falling further barely changes the model's answer. Then the case and the market decide the order.

Row two is epoxy resins from Taiwan. Let's follow it.

**If asked:**

- If asked about the chances: they run about 6 points high on average (report Appendix K). So the analyst uses the order, not the exact number.
- If asked about the 0% rows: ten declines had no imports in the latest three months, so they tie for first on biggest drop.

### Slide 11. Later: Taiwan had not come back.

*about 0:53*

This is row two, epoxy resins from Taiwan. The duty started in September 2024.

The red line is what the analyst could see in January. Census runs two months behind, so the data stops at month 2. Taiwan's share had been sliding even before the duty. By then it was 42 percent of its level a year and a half before. The biggest-drop rule ranked it 20th, so it wouldn't get checked. The model ranked it 2nd.

The grey line is what happened next. By month 18, March 2026, Taiwan was at 26 percent. It had not come back, like five others in the model's top seven that month.

But one month doesn't prove the model is better. For that, we need every month.

**If asked:**

- If asked what 42 percent means: Taiwan went from 10.3 percent of these imports to 4.4 percent. That's 42 percent of its old share, not 42 percent of all U.S. imports.

### Slide 12. The model's picks: 82% did not come back.

*about 1:15*

Now every month, not just one. We ran this on 44 monthly lists, from 2020 to 2025.

Each month, the analyst checks the top fifth of the list. That's about 187 checks in total. Then we wait until month 18 and ask: did each checked decline come back?

This is precision. We score the top of the list, because that's all the analyst acts on.

With the model's order, 82 percent of the checks found declines that had not come back by month 18. With biggest drop first, 70 percent. With a random order, 62 percent, the rate for all the declines on these lists.

The line shows the same at every share the analyst might check, from 5 percent of the list to half of it.

So with the same 187 checks, the model finds about 22 more lasting declines. The gap is 12 points. Our 90 percent range for it runs from 3.9 to 15.7, so it is clearly above zero. It also holds at months 6 and 8, and without the biggest investigation.

**If asked:**

- If asked for those numbers: month 6, 88 against 76. Month 8, 89 against 81. Without aluminum extrusions in 2024, 14 countries and nearly half the pairs, 89 against 77. We added that last check after seeing the first results.
- If asked whether you chose things with the test years in view: yes. Month 4 and boosting were picked with these years' accuracy in view. That's why the frozen forecast on the last slide matters. It's the first test on outcomes nobody has seen yet.
- If asked whether the fall cutoff matters: with a cutoff of 10 or 30 percent instead of 20, the outcome shares barely move (backup). We did not rerun the lists with other cutoffs.
- If asked why 62 here and 57 on slide 7: different groups. 57 is all 380 cases, including ones that never fell. 62 is the declines on the 2020 to 2025 lists, counted one product at a time.

### Slide 13. Four models, one answer.

*about 1:05*

Four models, one answer. So is it the model? We tried four, on the same inputs and the same years.

Same score as before: checking the top fifth of each list, how many had not come back. Gradient boosting gets 82 percent. A random forest, 84. Two kinds of regression, 82 and 81. None differs from boosting beyond its 90 percent range, so the type of model isn't what matters.

Where the gain comes from: on the right, our model, adding one group of inputs at a time. The market before and the case alone get 71, about the same as biggest drop first. Add the latest share, and it jumps to 83. Adding the rest of the fall so far, which is our full model, gives 82. No better.

So in our model, the jump comes from adding the latest share to the case and the market. Either one alone only matches the simple rule.

**If asked:**

- If asked why boosting, when the random forest scored higher: we fixed boosting as the ranking before the list test, after seeing its accuracy on held-out years. The gap is 1.4 points, inside the uncertainty.
- If asked for AUC: 0.795 for boosting, 0.791 for the random forest, 0.75 for the two regressions.
- If asked whether the split holds for every model: no. A logistic regression gets 79 from the case and the market alone. How the gain splits depends on the model. What holds for all four is that they beat the rule.
- If asked why the share just before the duty ranks second on slide 9 but its group adds nothing here: they answer different questions. Scrambling one input shows what the model uses. Adding a group shows what it adds beyond the others, and that group overlaps with them.
- If asked why keep all 23 inputs: we fixed them before testing. This breakdown came afterwards, as a check. Dropping inputs after seeing it would be tuning to the answer.
- If asked whether the latest share alone is a model: it's the biggest-drop rule, sorting by the latest share. A model given only the latest share and the month sorts each list the same way.

### Slide 14. What this means.

*about 0:58*

What this means. Three things.

First, mostly real, not borrowed. 57 percent of cases fell and had not come back by month 18.

Second, at month 4, use the model's list. 82 percent of its picks had not come back, against 70 percent for biggest drop first.

Third, not yet tested with analysts. We assumed 1 in 5 checked, and the model's lead holds from 5 to 50 percent. And we predict a country's recovery in a product, not whether one company survives.

Next: on November 15 we froze a forecast of 197 declines whose outcomes aren't known yet. We'll score it as new data comes out, from December 2026 to early 2028. Thank you.

We'd be glad to take your questions. And one for you: who would you hand this list to?

**If asked:**

- If asked how many get scored: 184. One month's list, 13 declines, already had its outcome public when we froze it.

---

## Questions, and the backup slide that answers each

| question | backup slide |
| --- | --- |
| What does a term mean? | 16. Terms we use. |
| Why gradient boosting and not another model? | 17. Other models give the same answer. |
| What could the analyst see in January, before the outcome? | 21. Taiwan, January 2025: what the analyst saw. |
| Why a fifth? What if the fall cutoff moves? | 18. A different cutoff, the same answer. |
| Why aren't the no-import rows at the top of the list? | 19. Below 60%, how far it fell matters little. |
| How do the model's picks differ from the biggest drops? | 20. Two ways to pick 7 of 36. |
| What if the analyst can check more, or fewer? | 22. Review these first: 82% stayed down. |
| How accurate is the model, and when does it start to work? | 23. By month 4, the forecast ranks them better. |
| What happens when the trade commission lifts the duty? | 24. Losses persist in cases that become orders. |
| How did you get from the notices to 502 cases? | 25. From 10,730 notices to 502 cases. |
| How exactly is the comparison built? | 26. How we measure it, product by product. |
| Do importers actually change suppliers? | 27. Buyers respond to duties, but slowly. |
| Did copper's total really come back? | 28. Copper's total imports came back. |
| How much of copper did the duty cover? | 29. But most copper was outside this duty. |
| What about inflation, and the other data checks? | 30. What the checks confirmed. |
| Presentation 1 feedback: the unusual-month score | 31. How we spot an unusual month. |
| Presentation 1 feedback: dollars against quantity | 32. Dollars alone can fool you. |
