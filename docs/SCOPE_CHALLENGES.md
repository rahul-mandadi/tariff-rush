# Questions that stab at the core

Drafted 2026-11-09 to test `docs/SCOPE.md` before we agree on it. They target what we solve and who we
solve it for, not the methods. Sources: Raunak's question; Kylie's Presentation 1 comments
("analytic problem is given but lacks clarity"; "need better and in-depth reasoning/justification
for methods"); the stakeholder skill's three tests (which decision changes, what the user already
knows, the one assumption everything rests on); and an independent reviewer given only the three
problem statements and no access to the repository.

Where a fact from our own results bears on a question, it is in brackets. A question we cannot
answer either changes the contract (SCOPE.md section 4) or becomes a stated limit in the report.

## The five that most threaten the core

1. **Our list tells me whether Vietnam's share of all U.S. mattress imports stays down. I care
   whether my own Vietnamese supplier can still sell to me at a workable landed cost. Why are those
   the same thing?** Breaks the link between the data science problem and the domain problem.
   [Duty rates are set company by company; we use the country-wide rate and the country's share.]
2. **By month 4 I have already collected quotes and may have signed with a new supplier. What
   decision is still open when your list arrives?** (Raunak's question, sharpened.) If the commitment
   comes first, the named user has nothing left to decide. [Some firms act at the preliminary duty,
   our month 0; qualifying a new supplier takes days to 18 months.]
3. **Who actually has more duty-hit relationships than they can review?** The capacity limit is the
   only reason a ranking exists. [Across all U.S. imports a month's queue has a median of 8
   relationships; one importer may face one or none.] If the answer is not a sourcing team, who is it:
   a trade-credit insurer, a supply-risk data vendor, a trade lawyer, a policy analyst, the domestic
   producer that filed the petition?
4. **If most targeted products never come back, what does a ranking give me that "assume they all
   stay down" does not?** [62 percent of the month-4 queue stays down; the forecast's top 20 percent
   stays down 82 percent of the time.] The answer has to name a decision that the do-nothing rule
   gets wrong.
5. **When a targeted country "recovers," is that my old supplier becoming competitive again, or the
   same goods coming in through a third country?** If recovery can be evasion, "will it stay down" is
   not clearly good or bad news for anyone. [We do not separate transshipment.]

## The domain problem: who, which decision, when

6. Name the decision: keep the old supplier qualified, drop it, sign a long contract with the new
   one? Which job title signs off on it? ("Review" is an activity, not a decision.)
7. When is that decision made compared with month 4? Is the list early enough to be used, or only
   early enough to be right?
8. I already know the duty is in place, its rate, what my supplier tells me, and that most of these
   stay down. What is left that only you can tell me?
9. I see my own shipments every week, about five weeks before Census publishes the month. What do
   you know that my own orders do not?
10. Whether I go back depends on later rate reviews and on whether my product falls inside the
    order. What does your list know that my customs broker or trade lawyer does not?
11. If my team reviews the top ten each month and ignores the rest, what goes wrong with the ones
    we ignored, and who notices?
12. Can you say in one sentence what someone does differently next week because of this project?
    (Kylie's "lacks clarity", as a test.)

## The analytical problem: what borrowed and real mean

13. Borrowed from whom, paid back how? Why is 18 months the line between temporary and permanent,
    and is that a number that matters to a buyer or one that fits the data?
14. The domain problem is about one team's review, the analytical problem about one country's trade,
    the data science problem about that country's national share. Where do we show these are the
    same question?
15. If the title's answer is already "mostly real", what is left for the prediction to do?
16. If a country's share comes back, did the duty fail, was it evaded, or did the market adjust?
    Can a reader of the list tell which?
17. Why predict whether the trade comes back rather than where it went? For a buyer's next contract,
    the replacement country may matter more.

## The data science problem: the target and the narrowing

18. Why is the targeted country's share of imports the thing to predict, rather than the importer's
    cost, its delivery delays, or whether its own supplier survives?
19. The list covers only relationships that fell and have not come back by month 4. What about the
    ones that fall later, recover early, or never fall? Does the user ever hear about them?
20. Why month 4? [The ITC vote, the strongest public signal, is never out by month 4; would a user
    simply wait two months for it?]
21. "Back" is a relative share. When the comparison countries get their own duties, does "back"
    still mean what a buyer means? [For 34 percent of the month-4 queue, a comparison country was
    named on the same product within 18 months.]

## Why it matters at all

22. These duties cover a small slice of U.S. imports. Why should anyone outside the trade-remedy
    world care whether a few product-country pairs bounce back? And why this narrow case when the
    tariffs firms worried about in 2025 and 2026 were broad?
23. Who loses money when the list is wrong, and roughly how much?
24. The domestic producers, the foreign exporters and the U.S. importers each want a different
    answer. Whose interests does this serve?
25. The list is built from public records anyone can read. What advantage is left for whoever uses
    it?
26. If the usual answer is "it stays down", the duty did what it was built to do. Where is the news?

## What to do with these

Questions 1 to 4 decide whether the domain problem and its user are right, and they need a decision
from both of us, not more analysis. The rest either follow from that decision or go in the report as
stated limits.
