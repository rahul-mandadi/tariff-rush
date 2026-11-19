# Presentation 2, spoken script

Generated from the speaker notes in `slides/Mandadi_Khalsa_Presentation2_v3.pptx`. Do not edit this
file: change the notes in `slides/build_deck2c.py`, rebuild, then run `python3 slides/write_script2.py`.

**1466 words.** At a careful 130 words a minute that is 11:17; at a normal 145, 10:07.
Rahul, slides 1 to 8: 839 words, about 5:47. Raunak, slides 9 to 13: 627 words, about 4:19.
Per-slide times below are at the normal pace. Rehearse once with a clock.

You do not have to say it word for word. Keep the numbers exact.

---

## Rahul

### Slide 1. Borrowed or Real

*about 0:12*

We're Rahul and Raunak. Our project asks a simple question: when the U.S. puts a duty on imports, does the business come back afterwards, or is it gone?

### Slide 2. What this project is about.

*about 0:44*

Here's the project in three lines.

The problem: when the U.S. puts a duty on a product from a country, that country's sales here often fall. Does that business come back once things settle, or is it gone for good?

Who needs to know: an analyst at a U.S. importer who keeps an eye on many product markets hit by duties. They can't dig into every decline, so they need to know which ones matter.

And the data science problem: using only public trade data, predict which declines will last, and put them in order so the analyst checks those first.

**If asked:**

- If asked what changed since Presentation 1: we asked three questions then: can we see a rush coming, what happens after the duty, and how long it lasts. Published data could not separate a rush from ordinary growth, so we focused on the last two, using antidumping cases, and added the forecast.

### Slide 3. Copper came back, but not the taxed part.

*about 0:53*

Our title asks whether the drop is borrowed, meaning buyers bought early and will come back, or real, meaning the business has gone elsewhere.

Copper in 2025 started us on this. Total copper imports fell when the 50% duty started in August, then came back, so it looked borrowed. But split by what the duty taxed: wire, tubes and sheets fell to about half and stayed there, about 49 thousand tonnes a month before and 27 after. Refined copper wasn't taxed, and that's what came back.

So the total hid what happened to the taxed products: we need to look at the products a duty names. But copper is one material, with no untaxed country to compare against, so we turn to hundreds of past duty cases.

**If asked:**

- If asked why copper, when the method uses antidumping cases: the 2025 copper duty taxed every country, so there is no untaxed supplier to compare with. Copper shows why we look at the products a duty names. The same reason keeps the 2025 tariffs out of the method.

### Slide 4. What we did, in four steps.

*about 0:41*

Here's everything we did, in four steps; the marker at the top of each slide shows where we are.

One, collect: we read every duty notice since 2015 and matched 502 cases to monthly Census import data. Two, measure: what happened to each named country against its rivals. Three, predict: four months after a duty, rank the declines by how likely they are to last. Four, test: score that ranking on 44 past monthly lists.

All four are done. One test is still running: a forecast we froze on November 15, which gets scored as Census publishes the data.

### Slide 5. We follow one product from one country.

*about 0:44*

Most tariffs in the news tax almost every country at once, so there's nobody untaxed to compare with. There's a narrower kind of duty, antidumping and countervailing duties, that names one product from one country: say, mattresses from Vietnam.

Other countries keep selling mattresses here, so we follow Vietnam's share month by month against its rivals. Anything that hits the whole product, like inflation, cancels out.

We read every duty notice in the Federal Register since 2015 and matched them to Census trade data: 502 cases. As a check, we rerun everything on a fake date two years earlier, before any of these cases.

**If asked:**

- antidumping duties answer sales below fair value; countervailing duties answer government subsidies.

### Slide 6. Where duties stayed: 31% below rivals.

*about 1:08*

Here's what happens after the duty. Zero is the named country's usual position against its rivals before the case. Where the duty became permanent, the country fell about 31 percent against its rivals on average over the 18 months after, and it was still falling at the end, about 37 percent down in months 13 to 18.

The grey line is the fake date: same cases, same method, moved two years earlier, before any case. It doesn't show the drop; if anything it drifts up, about 6 percent. So the decline isn't something the method produces by itself. It still doesn't prove the duty alone caused it: which suppliers face a petition, and other changes at the same time, could matter too.

There's also no clear surge before the duty, so there's little buying ahead to pay back. And where the trade commission found no injury and lifted the duty, there's no lasting fall (backup slide).

**If asked:**

- minus 0.37 log points, standard error 0.065; fake date plus 0.06, standard error 0.03, on the 283 cases with enough earlier data.
- If asked whether the country fell or its rivals grew: we measure its share against rivals, not its imports on their own. What we can add: the chance the product is traded at all falls 9 points, and quantity falls about as much as dollars. Where the trade went instead is a question we have not measured.
- If asked about goods rerouted through a third country: Census records the declared country of origin, so relabelled goods would count as the third country's. We can't separate that; it's a limit.

### Slide 7. More than half did not come back.

*about 0:52*

Now case by case. Here's what we mean by recovery. A country fell if its share dropped at least a fifth below where it was before the case. It came back if its share got back to that level and stayed there three months in a row, within 18 months.

Across 380 cases: 26 percent never fell, 17 percent fell and came back, and 57 percent fell and did not come back. 16 percent had no imports at all a year later. On the fake date, only 21 percent fell without coming back.

So for these duties, the answer to our title is closer to real than borrowed. But that's the average. Someone watching these markets needs to know which declines will last.

### Slide 8. Which declines should an analyst check first?

*about 0:32*

Back to our analyst. They can't look into every decline, so their question is: which ones first?

Four months in, Census has usually published two months after the duty, and some declines are visible. Each month's list is every relationship that has fallen and not yet recovered.

The simplest rule is to check the biggest drops first. That uses only public data and needs no model, so it's the bar our model has to clear.

*Handoff:* Raunak will show how our model ranks that list, and whether it beats the biggest drops.

**If asked:**

- If asked what checking means: looking into that relationship with the company's own supplier information. What the analyst does next is not something we tested.
- month 4 is a checkpoint we studied, not a business deadline. On the day the duty starts, case details like the duty rate don't predict recovery better than past averages, so we wait for some trade data.

---

## Raunak

### Slide 9. How the model ranks each month's list.

*about 0:58*

Thanks, Rahul. Here's how we get a ranking.

For each relationship on the list, the model sees 23 inputs, all public on the decision date: the latest share Census has published, how the fall has gone so far, facts about the case like the duty rate, and what the market looked like before the case.

The model is gradient boosting: many small decision trees, each correcting the ones before. It gives each relationship a chance of not recovering by month 18, and the list is sorted by that chance. Each prediction used only earlier cases whose outcomes were already public, the way an analyst would have had to do it.

The chart shows what it leans on. Scramble one input and see how much worse the forecast gets. The latest share matters most, about five times the next input.

**If asked:**

- settings were tuned inside the earlier cases, keeping each investigation together. Month 4 was chosen with the held-out accuracy in view, so months 6 and 8 are checks. Share just before the duty is the share in the six months before it, against the pre-duty level; the report calls it the pre-case rush.

### Slide 10. What the model hands the analyst.

*about 0:46*

So what does the model actually give the analyst? This is its real output for January 2025. Thirty-six declines were on the list. The model sorts them by its chance that each one stays down, and the analyst checks the top seven.

Each row is a product from a country: how far its share has fallen, and the model's chance it stays down. The last column is where the biggest-drop rule would put it. Five of the model's top seven are 20th or lower on that rule, so the model isn't just picking the deepest falls.

Row two is epoxy resins from Taiwan. Let's follow it.

**If asked:**

- the chances run about 6 points high on average (report Appendix K), so the analyst uses the order, not the number. Brazil's ferrosilicon appears twice because it is two eight-digit product codes. Ten relationships had no imports at all, so they tie for first on the biggest drop.
- If asked why those 0% rows aren't all at the top: below about 60 percent of the pre-duty share, the model's chance of coming back is roughly flat, so other inputs set the order (backup).

### Slide 11. Later: Taiwan had not recovered.

*about 0:44*

Row two: epoxy resins from Taiwan, under a duty from September 2024. In red is what the analyst could see in January: Taiwan's share was down to 42 percent of its own pre-duty share. The biggest-drop rule had it 20th, so it wouldn't be checked; the model had it 2nd.

In grey is what came later. By month 18, March 2026, Taiwan's share was 26 percent of its earlier level. It never recovered. Of the model's top seven that month, six had not recovered.

But one month can't tell us which order is better. For that we need every month.

**If asked:**

- 42 percent is 4.4 percent of these imports, against 10.3 percent before; it is 42 percent of Taiwan's earlier share, not of U.S. imports.

### Slide 12. The model's picks: 82% did not recover.

*about 0:52*

Now across all 44 monthly lists from 2020 to 2025. Every prediction used only earlier cases whose outcomes were already public. Each month the analyst checks a fifth of the list, about 187 checks in all. Then we look at month 18: had each checked relationship recovered or not?

In the model's order, 82 percent of the checks went to relationships that had not recovered. With the biggest drop first, 70 percent. In random order, 62 percent, which is just the share of all relationships that didn't recover.

So with the same 187 checks, the model finds about 22 more lasting declines than the biggest-drop rule. The difference is 12 points, with a 90 percent interval of 3.9 to 15.7.

**If asked:**

- it holds when the analyst checks 10 or 30 percent, at months 6 and 8 (88 against 76, 89 against 81), and without the largest case. A random forest and two linear models give 81 to 84 percent (backup).

### Slide 13. What this means.

*about 0:59*

Three things to take away.

First, after these duties, the drop is mostly real. More than half of named countries fell and hadn't come back 18 months later.

Second, if you're watching these markets, at month 4 the model's list finds more lasting declines than simply checking the biggest drops.

Third, the limits. We haven't tested this with working analysts, and how many they can check is our assumption. The model predicts a country's recovery in a product, not whether one supplier survives.

Next, on November 15 we froze a ranking of 197 relationships whose outcomes weren't known yet. One month's list, 13 relationships, already had its outcome month public, so the other 184 are the real test, scored as Census releases the data: the first list in December, the last in early 2028. Thank you.

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
