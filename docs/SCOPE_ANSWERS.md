# Answers to the challenge questions

Drafted 2026-11-09 against `docs/SCOPE.md` (the contract) and `docs/SCOPE_CHALLENGES.md` (the 26
questions), in dependency order. Each answer is marked:

- **A** answered by the repository, with its source
- **B** answered by a check run today on existing data (exploratory, point estimates)
- **C** a true limit we cannot fix with our data: it goes in the report, the contract stands
- **D** the answer shows a core sentence is wrong: the contract changes under its section 4
- **choice** a decision for Rahul and Raunak; the evidence is laid out, not decided

Only D changes the contract. If a contract change is made, re-answer only the questions whose
answers cite the changed clause, then do one consistency read and stop.

## Step 1. The root question

### Q3. Who actually has more duty-hit relationships than they can review? **D, option 1 agreed (2026-11-10)**

What the data says:
- [A] A month's queue across all U.S. imports has a median of 8 relationships (44 months, 6 with a
  single one; `review_queue.py` log). One importer sees only the products it buys, so its own queue
  is usually a few relationships or none.
- [A] Across 2016 to 2025, the targeted relationships carried about 20 billion dollars of imports a
  year in the 12 months before their duty, 0.71 percent of U.S. imports (check run today).
- [C] We have no data on how many cases one firm faces. The ITC surveys count purchasers per case
  (54 for aluminum extrusions), not cases per purchaser.

The options, and which other questions each one settles:

| option | the user | fits the country-share target (Q1)? | fits the month-4 timing (Q2, Q7)? | queue real (Q3)? | evidence |
|---|---|---|---|---|---|
| **1. keep, scoped** | a large importer or distributor buying many duty-hit lines (a home-improvement or furniture retailer) | as a proxy: the country's supply, not its own supplier | yes for the later, slower step (committing volume, keeping the old supplier qualified) | small: a handful of relationships | Floor & Decor's 10-K; ITC purchaser surveys; no interviews |
| **2. change** | someone watching all U.S. imports: a trade-credit insurer, a supply-risk data vendor, a trade analyst | yes: their exposure is by country and product | yes: they reassess monthly, no supplier switch to make | yes: the national queue is theirs | none collected; reopens the earlier decision to drop lenders |

Option 2 is a one-sentence change to the domain problem; the analytical and data science problems
stay as written. Neither option has been validated with a user.

**Agreed: option 1.** The project's evidence (ITC purchaser surveys, Floor & Decor, the mattress
moves) is all about importers, and an importer is the user an audience connects a tariff to. The
contract's domain problem now names that user and says the forecast is for the supplier country
(SCOPE.md section 4, agreed by both on 2026-11-10). What option 1 does not answer becomes stated limits:
the country stands in for one supplier (Q1), and one company's queue is a handful of relationships,
not the national queue (Q3).

## Step 2. The other load-bearing questions

### Q1. The list predicts the country's share; I care about my own supplier. **C under option 1**
Under option 1: **C**. The target is the country's supply of the product, a proxy for one supplier;
duty rates are set company by company and we use the country-wide "all others" rate
(`FINAL_REPORT.md` section 2.1); in the 2018 low-melt polyester fiber case most nonsubject imports
came from a Korean producer excluded from the case, a switch country-level data cannot see (`evidence/USE_EVIDENCE.md`). The report already says the odds are for a supplier country, not one
importer's supplier. Under option 2: **A**, the country and product are the user's unit.

### Q2. By month 4 I may already have signed with a new supplier. What decision is open? **A, partly C**
[A] Some firms act at the preliminary duty (Floor & Decor; mattress makers moving out of Vietnam, Thailand
and Cambodia within weeks of the 2020 preliminaries, `evidence/USE_EVIDENCE.md`), but qualifying a new supplier takes
from days to 18 months, about seven on average for tin mill products (ITC staff reports, report
section 1). The decision is staged: what is open at month 4 is how much volume to commit and whether
to keep the old supplier qualified. [C] We have no direct evidence of how many importers are still
undecided at month 4.

### Q4. If most never come back, what does a ranking add over "assume they all stay down"? **B**
Assume-all-stay-down is wrong for 38 percent of the month-4 queue. The ranking finds them: in the
bottom fifth of each month's list, where the forecast expects recovery, 71 percent came back, against
38 percent for a random fifth and 69 percent for the latest share alone (check run today). At the top,
82 percent of the forecast's picks stayed down, against 62 at random. So the decision the do-nothing
rule gets wrong is abandoning a relationship that comes back; at the bottom of the list the forecast
and the latest share are about equally good, and the forecast's edge is at the top.

## Step 3. The rest

| # | answer | mark |
|---|---|---|
| 5 | "Recovery" can include goods routed through a third country; circumvention is real (three circumvention findings are among the notices we removed) but we do not separate it. | C |
| 6 | Keep the old supplier qualified, or commit volume to the new one; a sourcing or category manager makes it. | A under option 1 |
| 7 | Month 4 arrives after the first move and before the volume commitment for slow qualifications (Q2). | A, partly C |
| 8 | What is left is which of the falling relationships will come back: the bottom of the list came back 71 percent of the time against 38 at random (Q4). | B |
| 9 | An importer's own shipments run about five weeks ahead of Census. We cannot test whether our forecast adds to its own data. | C |
| 10 | The model does not use administrative reviews or scope rulings, the legal events a broker or lawyer tracks. | C |
| 11 | At 20 percent capacity the reviews reach 26 percent of all persistent declines; the ignored 80 percent hold the rest, and the bottom of the list is mostly relationships that come back. | A |
| 12 | "Each month, commit first to new suppliers where we expect the old country's supply to stay down, and do not give up yet on the ones we expect back." | A under option 1 |
| 13 | "Borrowed" means bought ahead or lost for a while and then regained; "real" means not regained. 18 months: recovery after a fall flattens by then (25 percent back by month 18, 23 by month 12, Kaplan-Meier, `recovery_benchmark_fall20.csv`), and the ITC's final outcome is public at a median of month 6 (interquartile range 6 to 8, 458 cases), so 18 months is a year after the duty's fate is known. It is also the window the data allows for most cases. | A, partly C |
| 14 | The three statements share one object: the targeted country's position in one product. The domain problem reviews it, the analytical problem asks whether it returns, the data science problem predicts that. The report should say this link in one sentence. | A (wording) |
| 15 | "Mostly real" is the average; 38 percent of the month-4 queue does come back, and the prediction says which (Q4). | A |
| 16 | We cannot tell failure, evasion and adjustment apart from customs data; the ITC split shows where the duty was lifted, the trade came back, which is the "duty failed to stick" case. | C |
| 17 | Where the trade goes was tested and is not predictable from the tariff (`archive/README.md`, `docs/history/PHASE2_RESULTS.md`). | A |
| 18 | Cost, delays and one supplier's fate are not in public data; the country's share is the closest public measure of whether its supply returned. | A, partly C |
| 19 | Never fell (26 percent) and fell and came back early leave nothing to review; the user sees them in the historical rates (Table 2), which are the benchmark. Products that fall after month 4 enter later monthly checkpoints, not the month-4 queue. | A |
| 20 | Month 4 is the first checkpoint where the forecast ranks well (AUC 0.73 at month 3, 0.80 at month 4) and is two months before the vote, which is never public by month 4. Month 4 was the reported checkpoint before the review queue was defined, so the choice was not blind. | A, partly C |
| 21 | 34 percent of the queue had a comparison country named within 18 months. Leaving those out, the forecast's top fifth still stayed down 80 percent of the time, against 68 for the latest share and 59 at random (check run today). | B |
| 22 | About 20 billion dollars of imports a year, under 1 percent of U.S. imports, led by machinery, electrical equipment and vehicle parts (HS chapters 84, 85 and 87, 44 percent together), then furniture, steel articles, wood and aluminum. The broad tariffs were ruled out for reasons in the contract (section 3); the 5 percent coverage result shows why broad-tariff studies mostly watch untaxed trade. | B, A |
| 23 | No dollar loss was measured (`FINAL_REPORT.md` limitations; decision value is under assumed costs). | C |
| 24 | U.S. companies that buy from the targeted country; not the petitioners or the foreign exporters. | A under option 1 |
| 25 | The data is public; the work is in reading 718 notices, dating every release, and building comparisons that use only what was published. The advantage is the processing, as with any public-data product. | A |
| 26 | The news is not "it stays down" but which ones do not, and how early that is visible: day one adds little to history, month 4 ranks well. | A |

## Where this leaves the contract

- **D, agreed:** Q3 resolved as option 1; the domain problem names the user and the stand-in
  (SCOPE.md section 4, agreed by both on 2026-11-10). Q6, Q12 and Q24 follow from it; Q1 becomes a stated limit.
- **No other D.** The analytical and data science problems survived every question.
- **C, goes into the report as stated limits:** Q1, Q5, Q9, Q10, Q16, Q23, one company's small queue
  (Q3), and the unanswered parts of Q2, Q13, Q18 and Q20.
- **B, run today:** Q4, Q8, Q21, Q22. If any of them goes into the report, it is computed by a
  committed script first.
