# Presentation 2, spoken script

Generated from the speaker notes in `slides/Mandadi_Khalsa_Presentation2_v3.pptx`. Do not edit this
file: change the notes in `slides/build_deck2c.py`, rebuild, then run `python3 slides/write_script2.py`.

**1305 words.** At a careful 130 words a minute that is 10:02; at a normal 145, 9:00.
Rahul, slides 1 to 6: 722 words, about 4:59. Raunak, slides 7 to 11: 583 words, about 4:01.
Per-slide times below are at the normal pace. Rehearse once with a clock.

You do not have to say it word for word. Keep the numbers exact.

---

## Rahul

### Slide 1. Borrowed or Real

*about 0:12*

We're Rahul and Raunak. Our project asks a simple question: when the U.S. puts a duty on imports, does the business come back afterwards, or is it gone?

### Slide 2. Copper came back, but not the taxed part.

*about 1:02*

When a tariff is announced, buyers often rush to import before it starts, and then imports drop. Is that drop borrowed, meaning they bought early and will come back? Or is it real, meaning the business has gone somewhere else?

Copper in 2025 started us on this. Total copper imports fell when the 50% duty started in August, then came back, so it looked borrowed. But split by what the duty taxed: wire, tubes and sheets fell to about half and stayed there, about 49 thousand tonnes a month before and 27 after. Refined copper wasn't taxed, and that's what came back.

So the total hid what happened to the taxed products, and we need to look at the products a duty names. Copper is one material, though, with no untaxed country to compare against. To test the question properly, we turn to hundreds of past duty cases.

### Slide 3. We follow one product from one country.

*about 0:57*

So we move from copper to the historical duty cases. Most tariffs in the news tax almost every country at once, so there's nobody untaxed to compare with. There's a narrower kind of duty, antidumping and countervailing duties, that names one product from one country: say, mattresses from Vietnam.

Other countries keep selling mattresses to U.S. buyers, so we can follow Vietnam's share of those purchases month by month and compare it with its rivals. Anything that hits the whole product, like inflation or demand, cancels out.

We read every duty notice in the Federal Register since 2015 and matched them to Census trade data: 502 cases, 275 of them during Trump's two terms. As a check, we rerun everything on a fake date two years earlier, before any of these cases.

**If asked:**

- antidumping duties answer sales below fair value; countervailing duties answer government subsidies.

### Slide 4. Where duties stayed: 31% below rivals.

*about 1:08*

Here's what happens after the duty. Zero is the named country's usual position against its rivals before the case. Where the duty became permanent, the country fell about 31 percent against its rivals on average over the 18 months after, and it was still falling at the end, about 37 percent down in months 13 to 18.

The grey line is the fake date: same cases, same method, moved two years earlier, before any case. It doesn't show the drop; if anything it drifts up, about 6 percent. So the decline isn't something the method produces by itself. It still doesn't prove the duty alone caused it: which suppliers face a petition, and other changes at the same time, could matter too.

There's also no clear surge before the duty, so there's little buying ahead to pay back. And where the trade commission found no injury and lifted the duty, there's no lasting fall (backup slide).

**If asked:**

- minus 0.37 log points, standard error 0.065; fake date plus 0.06, standard error 0.03, on the 283 cases with enough earlier data.

### Slide 5. More than half did not come back.

*about 0:52*

Now case by case. Here's what we mean by recovery. A country fell if its share dropped at least a fifth below where it was before the case. It came back if its share got back to that level and stayed there three months in a row, within 18 months.

Across 380 cases: 26 percent never fell, 17 percent fell and came back, and 57 percent fell and did not come back. 16 percent had no imports at all a year later. On the fake date, only 21 percent fell without coming back.

So for these duties, the answer to our title is closer to real than borrowed. But that's the average. Someone watching these markets needs to know which declines will last.

### Slide 6. Which declines should an analyst check first?

*about 0:48*

Picture an analyst at a U.S. importer. They watch many product markets hit by duties, and they can't look into every decline. Their question is: which ones first?

On the day the duty starts, case details like the duty rate don't predict recovery better than past averages. We need some trade data first. Four months in, Census has usually published two months after the duty, and some declines are visible. Each month's list is every relationship that has fallen and not yet recovered.

The simplest rule is to check the biggest drops first. That uses only public data and needs no model, so it's the bar our model has to clear.

*Handoff:* Raunak will show how our model ranks that list, and whether it beats the biggest drops.

**If asked:**

- month 4 is a checkpoint we studied, not a business deadline.

---

## Raunak

### Slide 7. How the model ranks each month's list.

*about 0:55*

Thanks, Rahul. Here's how we get a ranking.

For each relationship on the list, the model sees 23 inputs, all public on the decision date: the latest share Census has published, how the fall has gone so far, facts about the case like the duty rate and whether it's China, and what the market looked like before the case.

The model is gradient boosting: many small decision trees, each correcting the last. It gives each relationship a chance of not recovering by month 18, and the list is sorted by that chance.

The testing is time-based. Each prediction used only earlier cases whose outcomes were already public at the time, the way an analyst would have had to do it. Settings were tuned inside those earlier cases, keeping each investigation together.

**If asked:**

- the most important input by far is the latest published share. Month 4 was chosen with the held-out accuracy in view, so months 6 and 8 are checks.

### Slide 8. Taiwan, January 2025: what the analyst saw.

*about 0:50*

Here's one real case from the January 2025 list. Epoxy resins from Taiwan came under a duty in September 2024. In January, Census had published trade through November.

Taiwan's share had fallen to 42 percent of its own pre-duty share: 4.4 percent of these imports, against 10.3 percent before. That's 42 percent of its earlier share, not 42 percent of U.S. imports.

That month, 36 relationships had fallen and not recovered. Checking a fifth of them means about seven. Ordered by the biggest drop, Taiwan was 20th, so it wouldn't be checked. Our model put it 2nd.

At this point nobody knew how it would turn out. That's the next slide.

**If asked:**

- Don't guess why the model ranked it second, and don't say a buyer should have switched; we didn't test either.

### Slide 9. Later: Taiwan had not recovered.

*about 0:29*

Here's what happened afterwards, which the analyst couldn't see in January. By month 18, March 2026, Taiwan's share was 26 percent of its earlier level. It never recovered.

So in this case the model's order sent the analyst to a lasting decline that the biggest-drop rule would have skipped. But one case can't tell us which order is better. For that we need every month.

### Slide 10. The model's picks: 82% did not recover.

*about 0:52*

Now across all 44 monthly lists from 2020 to 2025. Every prediction used only earlier cases whose outcomes were already public. Each month the analyst checks a fifth of the list, about 187 checks in all. Then we look at month 18: had each checked relationship recovered or not?

In the model's order, 82 percent of the checks went to relationships that had not recovered. With the biggest drop first, 70 percent. In random order, 62 percent, which is just the share of all relationships that didn't recover.

So with the same 187 checks, the model finds about 22 more lasting declines than the biggest-drop rule. The difference is 12 points, with a 90 percent interval of 3.9 to 15.7.

**If asked:**

- it holds when the analyst checks 10 or 30 percent, at months 6 and 8 (88 against 76, 89 against 81), and without the largest case. A random forest and two linear models give 81 to 84 percent (backup).

### Slide 11. What this means.

*about 0:55*

Three things to take away.

First, after these duties, the drop is mostly real. More than half of named countries fell and hadn't come back 18 months later.

Second, if you're watching these markets, at month 4 the model's list finds more lasting declines than simply checking the biggest drops.

Third, the limits. We haven't tested this with working analysts, and how many they can check is our assumption. The model predicts a country's recovery in a product, not whether one supplier survives.

Next, on November 15 we froze a ranking of 197 relationships whose outcomes weren't known yet. One month's list, 13 relationships, already had its outcome month public, so the other 184 are the real test, scored as Census releases the data. Thank you.

---

## Questions, and the backup slide that answers each

| question | backup slide |
| --- | --- |
| Why gradient boosting and not another model? | 13. Other models give the same answer. |
| What if the analyst can check more, or fewer? | 14. Review these first: 82% stayed down. |
| How accurate is the model, and when does it start to work? | 15. By month 4, the forecast ranks them better. |
| What happens when the trade commission lifts the duty? | 16. Losses persist in cases that become orders. |
| How did you get from the notices to 502 cases? | 17. From 10,730 notices to 502 cases. |
| How exactly is the comparison built? | 18. How we measure it, product by product. |
| Do importers actually change suppliers? | 19. Buyers respond to duties, but slowly. |
| Did copper's total really come back? | 20. Copper's total imports came back. |
| How much of copper did the duty cover? | 21. But most copper was outside this duty. |
| What about inflation, and the other data checks? | 22. What the checks confirmed. |
| Presentation 1 feedback: the unusual-month score | 23. How we spot an unusual month. |
| Presentation 1 feedback: dollars against quantity | 24. Dollars alone can fool you. |
