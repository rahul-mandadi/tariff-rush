# Scope contract: Borrowed or Real

## The tariffs this project is about

Most U.S. tariffs that hit one product from one country come out of a complaint by a U.S. industry.
If the industry shows that a country's producers sell in the U.S. below a fair price, the government
adds an **antidumping duty**; if it shows they are propped up by their own government's subsidies, it
adds a **countervailing duty**. Each one names exact products and one country, for example mattresses
from Vietnam in 2020. The extra tax starts with a **preliminary decision** about six months after the
complaint, and a few months later the U.S. International Trade Commission (the **ITC**) votes on
whether the tax stays. The broad tariffs a president sets on whole countries or materials, such as
the 2025 tariffs, are a different kind and are not what this project studies (section 3).

## Words used here

| word | meaning |
|---|---|
| product | one line of the U.S. tariff schedule, at the 8-digit level the duties are written in (for example 9404.21.00, mattresses of cellular rubber or plastics) |
| case | one country hit by one complaint, with its antidumping and countervailing decisions counted together |
| investigation group | all the countries named by the same complaint; cases in one group are not independent, so uncertainty is measured over groups |
| relationship | one product from the targeted country in one case, for example cellular-rubber mattresses from Vietnam |
| share | the targeted country's share of U.S. imports of that product, averaged over three months |
| back / not back | whether that share returns to where it was before the case |
| Census data | the U.S. Census Bureau's monthly import records, published about five weeks after each month ends |
| Federal Register | the government's daily journal, where every duty decision is published |
| held out | tested only on years the model never saw while it was built |
| review list | one month's relationships ranked from most to least likely to stay down |
| capacity | the share of a month's list a team has time to look at (assumed, not measured) |
| baseline | a simple rule the model has to beat |

## 1. The core (fixed)

**Domain problem.** When the United States puts one of these duties on a product from one country,
the sourcing team of a company that buys many such products (a retailer or distributor) has to
decide where to commit to new suppliers and where to hold on, and needs to know which declines will
last. The forecast is for the supplier country's position in the product, a stand-in for the
company's own supplier.

**Analytical problem.** After such a duty, is the targeted country's lost trade temporary (borrowed:
it comes back) or permanent (real: it does not), and how early can anyone tell?

**Data science problem.** Four months after the duty starts, take the relationships that have
already visibly fallen and not come back. Predict which of them will still not be back 18 months
after the duty, using only information that was public by then. Rank them so a team with limited
time reviews the likeliest lasting declines first, and test that ranking on later years against
simple rules.

## 2. Fixed definitions

These are the exact rules the code uses. They are fixed so every result in the project means the
same thing.

| item | rule | where in the code |
|---|---|---|
| cases | 502 cases in 204 investigation groups, with preliminary duties from January 2015 to October 2026, read from 687 Federal Register notices | `adcvd_stacked.py` |
| share | the targeted country's share of the product's U.S. imports, among the countries that sold it before the case, as a 3-month average. Its "before" level is the average 18 to 13 months before the duty | `recovery_lib.py` |
| fall | within 6 months of the duty, the share drops below four-fifths of its before level | `recovery_lib.py` |
| back | between the fall and month 18, the share is at or above its before level for three months in a row. Otherwise not back, which is what the model predicts. Relationships without 18 months of data are left out | `recovery_lib.py` |
| month 4 | the decision point. Census data count if published by the end of month 4, which usually means data through month 2; duty notices and the ITC vote count only if published by the end of month 3 | `prediction_landmark.py` |
| who is ranked | at month 4, relationships whose fall is already visible and that are not yet back: 1,376 relationships in 315 cases over all years; 936 in 198 cases and 66 groups in the held-out years 2020 to 2025 | `prediction_landmark.py`, `review_queue.py` |
| no peeking | the model sees only Census months on their real release dates, notices only once published, and compares the targeted country only with countries not already hit by their own case at the start | `build_decision_stacks.py`, `tests/` |
| testing | each year is predicted by a model trained only on earlier cases whose 18 months had been published; a test checks this against real release dates; settings are chosen within the training cases only | `prediction_landmark.py`, `tests/` |
| models now | two standard ones: logistic regression and gradient boosting (many small decision trees added together), trained once across months 3 to 14, with each case counted once per month | `prediction_landmark.py` |
| baselines | (a) the latest published share, lowest first: what an analyst can read off Census data without a model; (b) the historical rate, how often similar past cases came back, which is the same for everyone in a month and so ranks no better than random | `review_queue.py` |
| main measure | of the relationships a team reviews when it looks at an assumed 20 percent of each month's list, the share that were really not back by month 18. Each month's list is ranked on its own; each relationship counts once; ties share reviews equally | `review_queue.py` |
| other measures | the share of all lasting declines the reviews reached; two standard scores of how good the predicted chances are (Brier score: lower is better; AUC: how often a lasting decline is ranked above one that comes back); 90 percent ranges, computed by re-sampling whole investigation groups | `review_queue.py`, `prediction_landmark.py` |
| how a model wins | it replaces the latest-share ranking only if it beats it on the main measure and the 90 percent range of the difference stays above zero | `review_queue.py` |

**Where it stands now (held-out years).** Reviewing 20 percent of each month's list, the boosting
model's picks were not back 82 percent of the time, against 70 percent ranking by the latest share
and 62 percent in a random order: 11.5 points ahead of the latest share (90 percent range 3.9 to
15.7). For the predicted chances themselves, the latest share alone does about 70 percent of the
work (Brier 0.165, against 0.192 for the historical rate and 0.153 for boosting). On the day the duty
starts, the case's own facts add almost nothing to the historical rate.

## 3. Out of scope

- Whether importers rush to buy before broad, president-set tariffs (on steel, on all Chinese goods,
  on whole countries in 2025): too few such tariffs to learn from, several of the source documents
  were wrong, and when every country is taxed there is no untaxed supplier to compare with.
- Where the lost trade goes, and which backup country gets hit next.
- Ports and shipping companies as the user; dashboards or live tools.
- New data, a new definition of "back", a different unit than the relationship, or a different
  decision month as the main one.

A limit to state in the report: a duty's written scope, not its tariff codes, decides what it covers,
and some code lines include goods outside the order (for example mattress covers).

The 2018 tariffs on Chinese goods stay only as an existing check that the model works on another kind
of tariff. The finding that a tariff list names about 5 percent of its product category, and the
copper example, stay as background.

## 4. Change rule

The core and the rules above change only if a test of them fails: a data error, information leaking
in from the future, or a rule that cannot be computed. A better-sounding idea is not a reason. Any
change is written here, dated and agreed by both of us, with its reason.

This contract, including the two changes below, was agreed by Rahul and Raunak on November 10, 2026.

| date | change | reason | agreed by |
|---|---|---|---|
| 2026-11-09 | the domain problem names the user as a company buying many duty-hit products, and says the forecast is for the supplier country | challenge questions 3 (who has a review list) and 1 (country or own supplier); option 1 in `SCOPE_ANSWERS.md`, chosen because the project's evidence is about importers and the importer story is the one people connect a tariff to | Rahul, Raunak (2026-11-10) |
| 2026-11-09 (study plan, not the core) | methodology item 1 gains steps (d) other countries' pickup and (e) whether they already face a duty; new item 6, months 6 and 8 as a secondary check | an outside review of data sources found these signals in data we already have; the mattress cases show buyers moving to countries hit in the next round | Rahul, Raunak (2026-11-10) |

## 5. Methodology study (inside the core)

One question: **when a team can review only part of the month-4 list, does the model know more than
the latest published share, where does any gain come from, and where does it go wrong?**

| # | work | what it answers | output |
|---|---|---|---|
| 1 | Add information in steps and score each step at month 4, trained exactly as now: (a) facts about the case known by the decision date: the country's share and trend before the case, how much it sold, how concentrated the market is, how many other suppliers, the duty rate (and whether it is missing), retroactive duties, whether both kinds of duty apply, whether the country is China; (b) plus the latest share; (c) plus how the fall has gone: when it started, how long ago, how deep, the recent direction, months with no imports, any rush before the case, the change in price per unit; (d) plus how much of the lost volume other countries picked up by the decision date; (e) plus whether those other countries already face their own duty on the same product. Steps (d) and (e) use only data we already have: all countries' imports of the product (including countries left out of the comparison group because they were already under a duty) and notices published by the end of month 3 | where the predictive information comes from, whether the model beats one number, and whether signs of buyers switching to other countries help | the main measure, Brier and AUC for each step, with 90 percent ranges |
| 2 | Explain the model: which inputs matter most (permutation importance) and how the predicted chance moves with each one (partial dependence), both in scikit-learn; SHAP values too if the `shap` package is added | why a relationship is flagged, and whether that matches common sense about tariffs (a deeper fall, a higher duty) | 2 figures, 1 paragraph |
| 3 | Check where to trust it: whether a predicted 70 percent really happens about 70 percent of the time (a reliability plot), errors by kind of product and by how much the country sold, and results with and without the largest case (aluminum extrusions in 2024, nearly half the list) | when to trust the ranking | 1 figure, 1 table |
| 4 | Show the main measure at every capacity from 5 to 50 percent, not just 20 | whether the result depends on the assumed 20 percent | 1 figure |
| 5 (optional) | One extra model: the same boosting model, forced to never predict a lower chance of coming back when the latest share is higher | whether building in common sense helps on a small sample | one row in item 1's table |
| 6 | Repeat the main measure at months 6 and 8, on the same rules, as a secondary check; month 4 stays the main decision point | how much a team gains by waiting two or four more months | 1 small table |

The ITC vote is not one of the steps in item 1 because it is never public by month 4 (for none of
the 936 held-out relationships); the model still uses it at later months.

**Rules for the study.**
- The held-out years have been looked at before, so every new result is labeled exploratory: a
  finding to confirm, not a pre-planned test.
- Every model and every step is reported, whatever it shows. The main measure, the 20 percent
  capacity, who is ranked and how a model wins do not change after seeing results.
- The no-peeking and testing rules in section 2 do not change.
- Steps (d) and (e) and item 6 were added before any of them was run (2026-11-09).
- Proposed owner: Raunak (items 1 to 4 and 6), which also settles the statement of who did what.

## 6. Related work to add (each checked to exist and to say this)

- Prusa (2001), *Canadian Journal of Economics* 34(3): these duties cut imports from the named country
  by 30 to 50 percent, and imports fall even when the complaint is rejected. Our -31 percent for
  duties that stayed is in that range; where the ITC lifted the duty we see no lasting fall, a
  contrast to state carefully.
- Besedeš and Prusa (2017), "The Hazardous Effects of Antidumping," *Economic Inquiry* 55(1): these
  duties raise the chance that a country stops selling a product to the U.S. by more than half,
  mostly during the investigation and right after the preliminary decision. Consistent with our
  products that fell and had no imports a year later.
- Staiger and Wolak (1994), *Brookings Papers on Economic Activity: Microeconomics*: imports fall
  while a complaint is being investigated, even before or without a duty.
- Bown and Crowley (2007), *Journal of International Economics* 72: a U.S. duty pushes the named
  country's exports to other markets. Background for "where the trade goes", which is out of scope.

What we add to these: predicting and ranking at the moment a decision is made, from public
information only. Any benefit to a company's operations remains a proposed use until tested with
people who make these decisions.

## 7. Plan

The final presentation is December 11, 2026 according to our own decks; the report deadline and the
page and time limits are not confirmed. Confirm both on Canvas before agreeing to this.

| week | work |
|---|---|
| Nov 10 to 16 | agreed on November 10; Rahul shares the data files below; Raunak reruns `prediction_landmark.py` and `review_queue.py` and gets the numbers in section 2 |
| Nov 17 to 23 | items 1, 4 and 6 |
| Nov 24 to 30 | items 2 and 3 (Thanksgiving week) |
| Dec 1 to 7 | add to the report and final deck; related-work paragraph |
| Dec 8 to 11 | rehearse and submit |

**Data Raunak needs.** These files are too large for GitHub, about 800 MB in all: `panel/hs8/`
(264 MB, the import records), `events/raw/` (515 MB, the text of every notice and ITC page),
`panel/adcvd_stacks_decision.parquet` (12 MB) and `events/adcvd_index.json` (13 MB). Rebuilding
them instead needs a Census API key and several hours.

## 8. How this was checked (2026-11-09)

- Every rule in section 2 was read in the code it points to.
- The numbers in section 2 come from the committed result files.
- Starting from a clean copy of the pushed code (commit `a21581d`) plus the four data files above,
  the month-4 model and the review list rebuild exactly, file for file, in about 80 seconds.
- At month 4 the ITC vote was public for none of the 936 held-out relationships.
- The four papers in section 6 were checked against their publishers' or RePEc listings.
- Installed: scikit-learn 1.4.2, which covers items 2, 4 and 5. Not installed: `shap`.
