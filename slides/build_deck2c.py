"""Build Presentation 2, third version, as an editable .pptx.

A copy of slides/build_deck2b.py (the submitted v2, left unchanged) brought up to the current
report: the analyst framing, the corrected critical-circumstances numbers and the Taiwan example. Reworked after the
instructor's Presentation 1 notes: eleven main slides, one point each, talk-size figures from
slides/fig_talk.py, and the detail moved to backup slides.

Reads:  slides/fig/ (run slides/fig_talk.py first)
Writes: slides/Mandadi_Khalsa_Presentation2_v3.pptx
Run:    python3 slides/build_deck2c.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from PIL import Image
import os

INK = RGBColor(0x14, 0x16, 0x1A)
GREY = RGBColor(0x6E, 0x73, 0x7C)
RED = RGBColor(0xC8, 0x10, 0x2E)
W, H = 13.333, 7.5
FOOT = "RAHUL REDDY MANDADI   +   RAUNAKSINGH KHALSA"
FIG = "slides/fig"
FONT = "Avenir Next"
X0, CW = 0.75, 11.83
Y_FOOT, Y_RULE, Y_HEAD, Y_TAKE = 0.32, 0.74, 0.95, 6.45

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]


def txt(slide, text, x, y, w, h, size, bold=False, color=INK,
        align=PP_ALIGN.LEFT, font=FONT, italic=False, spacing=1.0):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        # **segments** render bold and in ink; everything else takes the passed colour. The
        # original deck only honoured a marker at the start of a line, which left the closing
        # asterisks printing as literal text.
        for j, seg in enumerate(line.split("**")):
            if not seg:
                continue
            r = p.add_run()
            r.text = seg
            r.font.size = Pt(size)
            r.font.bold = bold or (j % 2 == 1)
            r.font.italic = italic
            r.font.color.rgb = INK if (j % 2 == 1) else color
            r.font.name = font
    return tb


def chrome(s, names=True):
    if names:
        txt(s, FOOT, 6.00, Y_FOOT, 6.58, 0.30, 9, color=GREY, align=PP_ALIGN.RIGHT)
    ln = s.shapes.add_connector(1, Inches(X0), Inches(Y_RULE),
                                Inches(X0 + CW), Inches(Y_RULE))
    ln.line.color.rgb = GREY
    ln.line.width = Pt(0.75)


def add(headline, fig=None, caption=None, notes="", bullets=None, bullet_size=22,
        bullet_top=2.10, bullet_step=0.50, take_y=Y_TAKE, take_rule=False):
    if len(headline) > 46:
        raise SystemExit(
            f"headline is {len(headline)} characters: {headline!r}\n"
            "At 38pt bold it wraps to a second line and draws over the figure. Keep it to 46.")
    s = prs.slides.add_slide(BLANK)
    chrome(s)
    txt(s, headline, X0, Y_HEAD, CW, 0.80, 38, bold=True)
    if fig:
        p = f"{FIG}/{fig}"
        iw, ih = Image.open(p).size
        top = 2.05
        maxh = (Y_TAKE - 0.22) - top if caption else (H - 0.55) - top
        wid = min(CW, maxh * iw / ih)
        hei = wid * ih / iw
        s.shapes.add_picture(p, Inches((W - wid) / 2), Inches(top),
                             width=Inches(wid), height=Inches(hei))
    if caption:
        if take_rule:
            r = s.shapes.add_connector(1, Inches(X0), Inches(take_y - 0.14),
                                       Inches(X0 + CW), Inches(take_y - 0.14))
            r.line.color.rgb = GREY
            r.line.width = Pt(0.75)
        txt(s, caption, X0, take_y, CW, 0.75, 17, color=GREY, spacing=1.12)
    if bullets:
        y = bullet_top
        # A long bullet wraps, and the original step only accounted for explicit breaks, so a
        # wrapped line drew over the next bullet. Estimate the wrap from the character count.
        per_line = int(1600 / bullet_size)
        for b in bullets:
            txt(s, b, X0 + 0.15, y, CW - 0.5, 0.8, bullet_size,
                color=GREY, spacing=1.15)
            plain = b.replace("**", "")
            lines = sum(max(1, -(-len(seg) // per_line)) for seg in plain.split("\n"))
            y += bullet_step + 0.32 * (lines - 1)
        last = y - bullet_step
        floor = (take_y - 0.14) if take_rule else take_y
        if caption and last + bullet_size * 1.15 / 72 > floor:
            raise SystemExit(
                f"'{headline}': bullets run to {last:.2f}in and the takeaway band starts at "
                f"{floor:.2f}in. Lower bullet_top or bullet_step.")
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


# ================================================================ MAIN TALK (about ten minutes)
# Rahul: slides 1 to 6 (the question, copper, the design, what happens after a duty, the analyst's decision).
# Raunak: slides 7 to 11 (how the model ranks the list, Taiwan, the result, what it means).

# ---------------------------------------------------------------- M1 title
s = prs.slides.add_slide(BLANK)
chrome(s, names=False)
txt(s, "Borrowed or Real", X0, 2.05, CW, 1.05, 48, bold=True)
txt(s, "After a trade duty, does the business come back?", X0, 3.12, CW, 0.7, 26, color=RED)
txt(s, "Rahul Reddy Mandadi   +   Raunaksingh Khalsa", X0, 4.18, CW, 0.5, 20, bold=True)
txt(s, "DS 5500 Data Science Capstone   |   Presentation 2   |   November 2026",
    X0, 4.70, CW, 0.5, 15, color=GREY)
txt(s, "github.com/rahul-mandadi/tariff-rush", X0, Y_TAKE, CW, 0.4, 15, bold=True, color=RED)
s.notes_slide.notes_text_frame.text = (
    "TIMING: about ten minutes. Rahul, slides 1 to 6 (about 5 minutes). Raunak, slides 7 to 11 "
    "(about 5 minutes). Backup slides follow slide 11 for questions.\n\n"
    "RAHUL: We're Rahul and Raunak. Our project asks a simple question: when the U.S. puts a duty "
    "on imports, does the business come back afterwards, or is it gone?")

# ---------------------------------------------------------------- M2 copper, the starting example
add("Copper came back, but not the taxed part.", fig="t2_copper_split.png",
    caption="U.S. copper imports in tonnes, split by whether the 2025 duty taxed them. One example; "
            "next, 502 past duty cases.",
    notes="RAHUL: When a tariff is announced, buyers often rush to import before it starts, and "
          "then imports drop. Is that drop borrowed, meaning they bought early and will come back? "
          "Or is it real, meaning the business has gone somewhere else?\n\n"
          "Copper in 2025 started us on this. Total copper imports fell when the 50% duty started "
          "in August, then came back, so it looked borrowed. But split by what the duty taxed: "
          "wire, tubes and sheets fell to about half and stayed there, about 49 thousand tonnes a "
          "month before and 27 after. Refined copper wasn't taxed, and that's what came back.\n\n"
          "So the total hid what happened to the taxed products, and we need to look at the "
          "products a duty names. Copper is one material, though, with no untaxed country to "
          "compare against. To test the question properly, we turn to hundreds of past duty "
          "cases.")

# ---------------------------------------------------------------- M4 the design
add("We follow one product from one country.",
    bullets=[
        "**Some U.S. duties name one product from one country,** for example mattresses from "
        "Vietnam.",
        "**Other countries keep selling that product,** so we compare the named country with them, "
        "month by month.",
        "**502 such cases since 2015,** matched to monthly U.S. Census import records.",
    ],
    bullet_size=24, bullet_top=2.25, bullet_step=1.05,
    caption="Antidumping and countervailing duties, from Federal Register notices; Census trade "
            "records 2015 to 2026.",
    take_rule=True,
    notes="RAHUL: So we move from copper to the historical duty cases. Most tariffs in the news "
          "tax almost every country at once, so there's nobody "
          "untaxed to compare with. There's a narrower kind of duty, antidumping and "
          "countervailing duties, that names one product from one country: say, mattresses from "
          "Vietnam.\n\n"
          "Other countries keep selling mattresses to U.S. buyers, so we can follow Vietnam's "
          "share of those purchases month by month and compare it with its rivals. Anything that "
          "hits the whole product, like inflation or demand, cancels out.\n\n"
          "We read every duty notice in the Federal Register since 2015 and matched them to Census "
          "trade data: 502 cases, 275 of them during Trump's two terms. As a check, we rerun "
          "everything on a fake date two years earlier, before any of these cases.\n\n"
          "If asked: antidumping duties answer sales below fair value; countervailing duties "
          "answer government subsidies.")

# ---------------------------------------------------------------- M5 the aftermath
add("Where duties stayed: 31% below rivals.", fig="t4_aftermath.png",
    caption="Red: the 326 cases where the duty became permanent, against other countries selling "
            "the same product. Grey: the same calculation on a fake date two years earlier, before any case.",
    notes="RAHUL: Here's what happens after the duty. Zero is the named country's usual position "
          "against its rivals before the case. Where the duty became permanent, the country fell "
          "about 31 percent against its rivals on average over the 18 months after, and it was "
          "still falling at the end, about 37 percent down in months 13 to 18.\n\n"
          "The grey line is the fake date: same cases, same method, moved two years earlier, before "
          "any case. It doesn't show the drop; if anything it drifts up, about 6 percent. So the "
          "decline isn't something the method produces by itself. It still doesn't prove the duty "
          "alone caused it: which suppliers face a petition, and other changes at the same time, "
          "could matter too.\n\n"
          "There's also no clear surge before the duty, so there's little buying ahead to pay "
          "back. And where the trade commission found no injury and lifted the duty, there's no "
          "lasting fall (backup slide).\n\n"
          "If asked: minus 0.37 log points, standard error 0.065; fake date plus 0.06, standard "
          "error 0.03, on the 283 cases with enough earlier data.")

# ---------------------------------------------------------------- M6 outcomes and the meaning of recovery
add("More than half did not come back.", fig="t5_outcomes.png",
    caption="Fell: the country's share dropped at least a fifth below its pre-duty level within 6 "
            "months. Came back: back at that level for 3 months in a row by month 18. 380 cases.",
    notes="RAHUL: Now case by case. Here's what we mean by recovery. A country fell if its share "
          "dropped at least a fifth below where it was before the case. It came back if its share "
          "got back to that level and stayed there three months in a row, within 18 months.\n\n"
          "Across 380 cases: 26 percent never fell, 17 percent fell and came back, and 57 percent "
          "fell and did not come back. 16 percent had no imports at all a year later. On the fake "
          "date, only 21 percent fell without coming back.\n\n"
          "So for these duties, the answer to our title is closer to real than borrowed. But that's "
          "the average. Someone watching these markets needs to know which declines will last.")

# ---------------------------------------------------------------- M7 the analyst's decision
add("Which declines should an analyst check first?",
    bullets=[
        "**The analyst** works at a U.S. importer, watches many duty-hit products, and has time "
        "to check only some of them.",
        "**Four months after the duty,** Census has published about two months of trade. Some "
        "countries have visibly fallen.",
        "**The obvious rule: check the biggest drops first.** Anyone can do that from Census data, "
        "so a model has to beat it.",
    ],
    bullet_size=24, bullet_top=2.20, bullet_step=1.10,
    notes="RAUNAK: Picture an analyst at a U.S. importer. They watch many product markets hit by "
          "duties, and they can't look into every decline. Their question is: which ones first?\n\n"
          "On the day the duty starts, case details like the duty rate don't predict recovery "
          "better than past averages. We need some trade data first. Four months in, Census has "
          "usually published two months after the duty, and some declines are visible. Each "
          "month's list is every relationship that has fallen and not yet recovered.\n\n"
          "The simplest rule is to check the biggest drops first. That uses only "
          "public data and needs no model, so it's the bar our model has to clear.\n\n"
          "If asked: month 4 is a checkpoint we studied, not a business deadline.\n\n"
          "HANDOFF: Raunak will show how our model ranks that list, and whether it beats the "
          "biggest drops.")

# ---------------------------------------------------------------- M7b how the model ranks the list
add("How the model ranks each month's list.",
    bullets=[
        "**What it sees:** 23 inputs, all public on the decision date: the latest published share, "
        "how the fall has gone, the case's facts and the market before the case.",
        "**The model:** gradient boosting, many small decision trees, which scores each "
        "relationship's chance of not recovering by month 18.",
        "**How we tested it:** each prediction used only earlier cases whose outcomes were already "
        "public. Lists from 2020 to 2025.",
    ],
    bullet_size=24, bullet_top=2.15, bullet_step=1.05,
    caption="Also tried: logistic regression, elastic net and a random forest, with the same result "
            "(backup). The latest published share carries most of the signal.",
    take_rule=True,
    notes="RAUNAK: Thanks, Rahul. Here's how we get a ranking.\n\n"
          "For each relationship on the list, the model sees 23 inputs, all public on the decision "
          "date: the latest share Census has published, how the fall has gone so far, facts about "
          "the case like the duty rate and whether it's China, and what the market looked like "
          "before the case.\n\n"
          "The model is gradient boosting: many small decision trees, each correcting the last. "
          "It gives each relationship a chance of not recovering by month 18, and the list is "
          "sorted by that chance.\n\n"
          "The testing is time-based. Each prediction used only earlier cases whose outcomes were "
          "already public at the time, the way an analyst would have had to do it. Settings were "
          "tuned inside those earlier cases, keeping each investigation together.\n\n"
          "If asked: the most important input by far is the latest published share. Month 4 was "
          "chosen with the held-out accuracy in view, so months 6 and 8 are checks.")

# ---------------------------------------------------------------- M8 Taiwan: what was known
s = prs.slides.add_slide(BLANK)
chrome(s)
txt(s, "Taiwan, January 2025: what the analyst saw.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
p_ = f"{FIG}/t6_taiwan_known.png"
iw, ih = Image.open(p_).size
fh = 4.25
s.shapes.add_picture(p_, Inches(X0), Inches(2.05), width=Inches(fh * iw / ih), height=Inches(fh))
xr = X0 + fh * iw / ih + 0.45
txt(s, "January's list: **36** declines.\nThe analyst checks the first **7**.", xr, 2.25, W - xr - 0.5,
    1.2, 22, color=GREY, spacing=1.15)
txt(s, "Biggest drop first:\n**Taiwan is 20th.** Not checked.", xr, 3.55, W - xr - 0.5, 1.1, 22,
    color=GREY, spacing=1.15)
txt(s, "Model's order:\nTaiwan is 2nd. Checked.", xr, 4.75, W - xr - 0.5, 1.1, 22, bold=True,
    color=RED, spacing=1.15)
r = s.shapes.add_connector(1, Inches(X0), Inches(Y_TAKE - 0.14), Inches(X0 + CW), Inches(Y_TAKE - 0.14))
r.line.color.rgb = GREY
r.line.width = Pt(0.75)
txt(s, "Epoxy resins from Taiwan, under a duty from September 2024. 42% is 42% of Taiwan's own "
       "pre-duty share, not of U.S. imports.", X0, Y_TAKE, CW, 0.75, 17, color=GREY, spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "RAUNAK: Here's one real case from the January 2025 list. Epoxy resins from Taiwan came "
    "under a duty in September 2024. In January, Census had published trade through November.\n\n"
    "Taiwan's share had fallen to 42 percent of its own pre-duty share: 4.4 percent of these "
    "imports, against 10.3 percent before. That's 42 percent of its earlier share, not 42 percent "
    "of U.S. imports.\n\n"
    "That month, 36 relationships had fallen and not recovered. Checking a fifth of them means "
    "about seven. Ordered by the biggest drop, Taiwan was 20th, so it wouldn't be checked. Our "
    "model put it 2nd.\n\n"
    "At this point nobody knew how it would turn out. That's the next slide.\n\n"
    "Don't guess why the model ranked it second, and don't say a buyer should have switched; we "
    "didn't test either.")

# ---------------------------------------------------------------- M9 Taiwan: what happened later
add("Later: Taiwan had not recovered.", fig="t6_taiwan_later.png",
    caption="Red: published by January 2025. Grey: published afterwards. One case shows the two "
            "orders differ; it can't show which is better.",
    notes="RAUNAK: Here's what happened afterwards, which the analyst couldn't see in January. "
          "By month 18, March 2026, Taiwan's share was 26 percent of its earlier level. It never "
          "recovered.\n\n"
          "So in this case the model's order sent the analyst to a lasting decline that the "
          "biggest-drop rule would have skipped. But one case can't tell us which order is "
          "better. For that we need every month.")

# ---------------------------------------------------------------- M10 the result
add("The model's picks: 82% did not recover.", fig="t7_review_result.png",
    caption="44 monthly lists, 2020 to 2025; each prediction used only earlier cases whose outcomes "
            "were already public. At month 4 the analyst checks 1 in 5; we score them at month 18.",
    notes="RAUNAK: Now across all 44 monthly lists from 2020 to 2025. Every prediction used only "
          "earlier cases whose outcomes were already public. Each month the analyst checks a fifth of the list, about 187 checks in "
          "all. Then we look at month 18: had each checked relationship recovered or not?\n\n"
          "In the model's order, 82 percent of the checks went to relationships that had not "
          "recovered. With the biggest drop first, 70 percent. In random order, 62 percent, which "
          "is just the share of all relationships that didn't recover.\n\n"
          "So with the same 187 checks, the model finds about 22 more lasting declines than the "
          "biggest-drop rule. The difference is 12 points, with a 90 percent interval of 3.9 to "
          "15.7.\n\n"
          "If asked: it holds when the analyst checks 10 or 30 percent, at months 6 and 8 (88 "
          "against 76, 89 against 81), and without the largest case. A random forest and two "
          "linear models give 81 to 84 percent (backup).")

# ---------------------------------------------------------------- M11 what it means
add("What this means.",
    bullets=[
        "**Mostly real, not borrowed:** after these duties, most declines were still there at "
        "month 18.",
        "**At month 4, check the model's list first:** it found more lasting declines than the "
        "biggest drops.",
        "**Not yet tested with analysts:** checking 1 in 5 is our assumption.",
    ],
    bullet_size=24, bullet_top=2.25, bullet_step=1.05,
    caption="Next: on November 15 we froze a ranking of 197 open relationships. The 184 whose "
            "outcome months were still unpublished will be scored as Census releases them.",
    take_rule=True,
    notes="RAUNAK: Three things to take away.\n\n"
          "First, after these duties, the drop is mostly real. More than half of named countries "
          "fell and hadn't come back 18 months later.\n\n"
          "Second, if you're watching these markets, at month 4 the model's list finds more "
          "lasting declines than simply checking the biggest drops.\n\n"
          "Third, the limits. We haven't tested this with working analysts, and how many they "
          "can check is our assumption. The model predicts a country's recovery in a product, not "
          "whether one supplier survives.\n\n"
          "Next, on November 15 we froze a ranking of 197 relationships whose outcomes weren't "
          "known yet. One month's list, 13 relationships, already had its outcome month public, "
          "so the other 184 are the real test, scored as Census releases the data. Thank you.")

# ================================================================ BACKUP
s = prs.slides.add_slide(BLANK)
chrome(s, names=False)
txt(s, "Backup", X0, 2.9, CW, 1.0, 48, bold=True)
txt(s, "Details for questions.", X0, 3.95, CW, 0.6, 22, color=GREY)

add("Other models give the same answer.",
    bullets=[
        "**Gradient boosting (used):** 82.3%",
        "**Random forest:** 83.8%",
        "**Logistic regression:** 81.6%",
        "**Elastic net:** 80.9%",
        "**Biggest drop first:** 70.3%",
    ],
    bullet_size=24, bullet_top=2.15, bullet_step=0.70,
    caption="Share of checked relationships not recovered by month 18; month-4 lists, checking 1 in "
            "5. None differs from boosting beyond its 90% interval; the rule to keep boosting was "
            "set before this check.",
    take_rule=True,
    notes="Same inputs, training years and tuning for every model, scored on the same lists. All "
          "four beat the biggest-drop rule with 90 percent intervals above zero. Report Appendix K.")

# ---------------------------------------------------------------- 13 the review queue
add("Review these first: 82% stayed down.", fig="20_review_queue.png",
    caption="44 monthly lists, 2020 to 2025, about 187 review slots at 20%: forecast 12.0 points above the "
            "latest share (3.9 to 15.7), about 22 more lasting declines. Next: scoring a forecast frozen in November.",
    take_rule=True,
    notes="Backup for slide 10. An analyst at an importer can review only some "
          "of the tariff-hit product-country relationships and wants to start with those whose "
          "decline is likely to persist, reading our ranking next to the company's own supplier "
          "information. We predict the supplier country's recovery in a product, not one "
          "supplier's failure.\n\n"
          "Month 4 was chosen with the held-out accuracy in view, so months 6 and 8 are checks: 88% "
          "against 76%, and 89% against 81%. The review rules were fixed before we looked at the "
          "review results: only products already falling and not yet back; "
          "each calendar month its own queue, so no later case is ranked early; the held-out "
          "month-4 predictions; an assumed 20% of each queue reviewed, with 10% and 30% "
          "as checks; ties share the reviews; intervals resample investigation groups.\n\n"
          "Of 936 held-out relationships, 62% stayed down. At 20%, 82% of the forecast's picks "
          "stayed down, 70% of the latest share's, 62% of a random order, which is all the "
          "historical rate can give because it is the same for every product in a month. It holds "
          "at 10% and 30%, weighting each case once, and without the largest case. The historical "
          "rate stays as the benchmark: how many of a month's falling products usually stay down. "
          "The capacities are assumptions; any benefit to an importer is a proposed use until "
          "tested with users.\n\n"
          "If asked about other models: a random forest, plain logistic regression and an elastic "
          "net, on the same inputs and years, reach 81% to 84% at 20%; all beat the latest share and "
          "none differs from boosting by more than its interval. Most of the gain comes from the "
          "latest share itself.\n\n"
          "The frozen forecast: on November 15 we ranked 197 relationships in 12 monthly lists. The "
          "July 2025 list's outcome month was already public, so 184 relationships in 11 lists "
          "will be scored as Census releases the months.")
# ---------------------------------------------------------------- 12 next
add("By month 4, the forecast ranks them better.", fig="19_monthly_forecast.png",
    caption="Products already falling; each prediction used only earlier cases with public outcomes. Month 4: "
            "79.5% of pairs ranked correctly (AUC 0.795); the latest share alone gives about 70% of the gain.",
    notes="Within a few months the forecast ranks falling products better than history alone, and most "
          "of that comes from a number anyone can read off Census data: the latest share.\n\n"
          "Each month the model re-scores every product that has visibly fallen and is not yet "
          "back, using only trade data Census had published, notices published by then, and rivals "
          "not yet named in another case; it trains only on earlier cases whose outcomes were "
          "published. Month 4 was chosen with this held-out accuracy in view.\n\n"
          "Numbers if asked: day one, Brier 0.242 against 0.248 for history, a gain of 0.007 whose "
          "90% range (-0.001 to 0.013) includes zero, so case facts add nothing we can tell apart "
          "from history. By month 4, boosting ranks a product that came back above one that "
          "did not in 79.5% of pairs (AUC 0.795), 0.039 better than that month's historical rate (0.026 to 0.052); "
          "a model of the latest share alone gets about 70% of that gain (Brier 0.165 against 0.192; "
          "boosting 0.154). Boosting stays slightly ahead of the latest-share model in every month "
          "from 3 to 12, though no month clears a joint test. These are gains in probability "
          "accuracy, on products already falling, and the sample is 136 investigation groups, not "
          "the 16,781 product-month rows.")

# ---------------------------------------------------------------- 6 the aftermath (finding 2)
add("Losses persist in cases that become orders.", fig="12_order_vs_negative.png",
    caption="These duties tax one product from one named country. Where the duty became permanent "
            "(326 cases), that country's imports fell about 31% against rival suppliers over the 18 "
            "months we see. Where the trade commission found no injury (45 cases), no lasting fall.",
    notes="Define both on the way in: an antidumping duty answers a complaint that a foreign "
          "producer sells below its home price; a countervailing duty answers a complaint that it "
          "is subsidised. Both name one product and one country, and there are hundreds of them.\n\n"
          "How a case ends: a few months after the duty starts, the US International Trade "
          "Commission votes on whether the imports hurt US producers. Yes, and the duty becomes a "
          "permanent order; no, and it is lifted and the deposits are refunded.\n\n"
          "Reading the chart: zero is the country's position against rival suppliers a year and a "
          "half before the duty (the average of months 18 to 13 before). We find no clear average "
          "surge before the duty; individual cases may differ. The red line breaks at the duty and "
          "keeps falling; the shading is its 95% range.\n\n"
          "Numbers if asked: minus 0.37 log points (standard error 0.065), minus 0.46 in months 13 "
          "to 18; the chance the product is traded at all falls 9 points. All cases pooled: minus "
          "0.19 (standard error 0.11).\n\n"
          "Be careful with the black line: the commission's vote looks at the imports themselves, "
          "and that group is small and mostly the 2024 aluminum extrusions cases. It describes "
          "the two groups; it does not prove the duty caused the gap, and 18 months is not proof "
          "the business left for good.\n\n"
          "If asked what changed since last time: we rebuilt this estimate on a fixed set of "
          "products with zero months kept. The earlier '42% above its usual level' came from how "
          "the old comparison was set up, not from a surge before the case.")

# ---------------------------------------------------------------- the matching funnel
add("From 10,730 notices to 502 cases.",
    bullets=[
        "**10,730 notices** in the Federal Register, 2015 to 2026; **1,201** are preliminary "
        "decisions in new investigations, when duty collection starts.",
        "**718** give the case's opening date and a product code we can read. We read each one and "
        "drop **31** that start no new duty: **687** notices.",
        "**502 cases:** one country in one investigation, with companion notices merged; 204 "
        "investigation groups.",
        "**457** have earlier trade and a rival selling the product; **381** also have all 18 months "
        "after the duty.",
    ],
    bullet_size=20, bullet_top=2.00, bullet_step=0.74,
    caption="919 of the 935 product codes the kept notices name appear in the Census data. Every step, "
            "with what it drops: report Fig. 2.",
    take_rule=True,
    notes="Each bar is one step of the matching, and the grey line under it says what was dropped "
          "and why.\n\n"
          "Most notices drop out because they are not new investigations: yearly reviews of old "
          "duties, sunset reviews, court decisions. Among preliminary decisions we need the case's "
          "opening date and a product code we can read from the text. We then read every remaining "
          "notice and remove the 31 that do not start a new duty.\n\n"
          "Companion antidumping and countervailing notices are merged, so one country in one "
          "investigation is one case: 502 cases. 457 have enough earlier trade and a rival selling "
          "the same product; 381 also have all 18 months after the duty so far. 919 of the 935 "
          "product codes the kept notices name appear in the Census data.")

# ---------------------------------------------------------------- 5 the method
add("How we measure it, product by product.",
    bullets=[
        "**One product from one country, every month,** using the eight-digit product codes "
        "tariff orders are written in: 15.9 million rows of Census trade data, 2015 to 2026.",
        "**Compared with other countries selling the same product that month,** with months of "
        "no trade counted as zero. A change shared by all of them cancels out.",
        "**Checked against a fake date.** The same calculation on the same cases two years "
        "earlier, a falsification check: a pattern that also shows there is not the duty's.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.62,
    caption="687 preliminary notices (697 country decisions) form 502 country cases; 381 have a full 18 months, 283 a fake "
            "date. Values are nominal dollars (not inflation-adjusted); shared price changes cancel.",
    take_rule=True,
    notes="This is the method Kylie asked us to explain.\n\n"
          "Why compare countries within a product: 2020 to 2025 moved every trade series at once. "
          "A before-and-after on one country cannot tell that apart from the duty. Comparing with "
          "other suppliers of the same product in the same month removes what they share.\n\n"
          "Each case gets its own small panel: its products, the targeted country, and every "
          "country that sold those products before the case, for the 18 months before and after. "
          "Who is in the panel is fixed from before the case, and a month with no trade stays in "
          "as zero, so a supplier that stops selling is counted, not dropped. Rivals that face a "
          "case of their own on the product around the same time are left out of the comparison.\n\n"
          "We read every decision notice: 31 of 718 did not start a new duty (negative findings, "
          "side notices, reviews of old orders, circumvention findings on old orders) and are out. Uncertainty is computed over whole "
          "investigations, because one petition often names several countries.")

# ---------------------------------------------------------------- public evidence that the decision exists
add("Buyers respond to duties, but slowly.",
    bullets=[
        "**They switch.** In the trade commission's own surveys, 27 of 54 aluminum extrusion "
        "buyers and 23 of 45 steel nail buyers changed suppliers, mostly for other reasons.",
        "**It takes months.** Qualifying a new supplier took from days to 18 months; tin mill "
        "buyers averaged about seven.",
        "**Some move early.** Floor & Decor moved its Chinese tile sourcing to other countries "
        "after the 2019 preliminary duties.",
        "**Some duties are lifted.** Deposits are refunded if the trade commission finds no injury.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.66,
    caption="Sources: USITC final staff reports, Publications 5560, 5370 and 5492; Floor & Decor "
            "Form 10-K, February 2020.",
    take_rule=True,
    notes="Background on why importers watch these markets.\n\n"
          "The trade commission sends questionnaires to purchasers in every case. In the final "
          "staff reports for our own cases, about half of responding purchasers changed suppliers "
          "during the investigation period: aluminum extrusions 27 of 54, steel nails 23 of 45, "
          "PET resin 17 of 25. Not all of that switching was caused by the duty; shortages and "
          "COVID drove some of it, and the reports say so.\n\n"
          "Qualifying a new supplier is slow: purchasers reported anywhere from days to 18 months, "
          "and tin mill buyers averaged a little over seven. A trade association told the commission "
          "12 to 18 months for regulated products.\n\n"
          "Floor & Decor's 10-K says that after Commerce's 2019 preliminary duties on Chinese "
          "ceramic tile it sourced from alternative countries and believed it was no longer "
          "importing the covered tile from China. Mattress makers left Vietnam within weeks of the "
          "2020 preliminary rates, and our data show the same shift the trade press reported.\n\n"
          "So buyers do respond, and it takes months. This is context only: it does not show that "
          "our review list changes any decision, or what it would save. Only a few purchasers per report tie their switching to "
          "the case itself.")

# ---------------------------------------------------------------- copper total (from the main talk)
add("Copper's total imports came back.", fig="t1_copper_total.png",
    caption="U.S. copper imports, dollars a month. The total fell when the 50% duty started, then came "
            "back; the taxed products did not (slide 2).",
    notes="Backup for slide 2: the total that made copper look borrowed.")

# ---------------------------------------------------------------- 3 coverage (finding 1)
add("But most copper was outside this duty.", fig="09_sankey.png",
    caption="The 50% duty named wire, tubes and sheets: 29% of copper imports by value. Refined "
            "cathodes, copper sold as a raw input and 67% of the total, were outside it. Most of a "
            "category outside the tariff is typical: the median list names about 5 dollars in 100.",
    notes="Say this, it answers Kylie's note '1% coverage means ...': 1% coverage means the "
          "products a tariff names made up one dollar in every hundred that the category imported. "
          "The other ninety-nine were in products outside that tariff's list.\n\n"
          "A category here is a broad product group, what the customs schedule calls a chapter, "
          "like copper or pharmaceuticals.\n\n"
          "How it is built, Kylie's 'same for Fig 5': for each pairing of a tariff list with a "
          "category, add up imports of the products the list names, from all countries, and divide "
          "by the whole category. Across 1,350 pairings the median is 5.4%, and a third are under "
          "1%. We use 2017 trade, before the 2018 tariffs, so the shares are not already shaped by "
          "them. It does not hinge on the year: 5.4% with 2016, 5.4% with 2017, 6.7% with 2024.")

# ---------------------------------------------------------------- 11 what the checks confirmed
add("What the checks confirmed.",
    bullets=[
        "**Inflation and price.** Shared price changes cancel; in months with trade, tonnes fall about as much as dollars.",
        "**Every duty decision read.** 687 notices kept; 31 that did not start a new duty removed.",
        "**Finer product codes.** The data uses the eight-digit codes tariffs name.",
        "**The tariff list.** 120 tariff documents, each tagged with the law it rests on.",
        "**Unusual-month score.** One consistent scale; same top ten categories.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.58,
    caption="Each check runs from a script in the repository.",
    take_rule=True,
    notes="These answer Kylie's notes from Presentation 1.\n\n"
          "Say this about the list, since Kylie flagged it: last time we said 134. Fourteen of those "
          "were Labor Department notices about retraining for laid-off workers, not tariffs, so the "
          "list is 120.\n\n"
          "Inflation, two BLS price indexes: adjusting by all import prices keeps 8 of the top 10 "
          "categories (rank correlation 0.97); by non-fuel import prices, 9 of 10 (0.99). Neither "
          "touches the antidumping result, where a shared price change cancels, and the tonnes "
          "check points to lower volume rather than a price cut, though both ranges include zero.\n\n"
          "The 31 notices removed: 4 negative findings, 16 side notices about retroactive duties, "
          "8 reviews of orders that already existed, 3 circumvention findings on existing orders.")

# ---------------------------------------------------------------- 7 the transformation (Kylie's Fig 4)
add("How we spot an unusual month.", fig="04_normal.png",
    caption="Three steps. Draw an expected line from the category's past: recent trend plus usual "
            "seasonal pattern. Shade a normal range from how much it usually wobbles. Score each "
            "month of 2025 by its gap above the line as a share of the range: 1.0 reaches the top "
            "edge. The category keeps its highest month.",
    notes="This answers Kylie's note on Fig 4: explain the transformation and the choices.\n\n"
          "The choices: the trend uses the last three years, so the line reflects recent growth "
          "rather than the pre-2020 pace. The wobble is measured over the whole decade, which gives "
          "a wider, more cautious range; using only three years would flag 28 of 96 categories "
          "instead of 10. Gaps are on a log scale so a doubling counts the same for a small "
          "category as a large one. The range is 1.96 times the usual wobble. The window is January "
          "to August 2025, the one Presentation 1 used. It is a historical benchmark, not a tested "
          "forecast.\n\n"
          "Copper here went above its range in spring 2025, before the duty.")

# ---------------------------------------------------------------- 8 dollars vs quantity (finding 3)
add("Dollars alone can fool you.", fig="08_units.png",
    caption="One category per row, scored in dollars and in physical quantity. Cocoa looked unusual "
            "in dollars because its price per kilo roughly doubled. Pharmaceuticals barely moved in tonnes but "
            "jumped in dollars in March 2025, led by Swiss medicines at about $5,000 a kilo.",
    notes="The takeaway: a category's dollar total alone can mislead, in both directions.\n\n"
          "Cocoa's import value per kilo went from about $4 in 2022 to about $9 in 2025.\n\n"
          "Pharmaceuticals scores 2.26 on dollars (first of 63 categories) and minus 0.34 on tonnes "
          "(62nd). In the medicine line "
          "with the biggest March jump, Swiss shipments ran about $5,185 a kilo against $183 for "
          "Indian ones, so a shift toward Swiss product lifts dollars far more than tonnes.\n\n"
          "This check applies to the category rankings. The antidumping result points the same way in "
          "physical quantity: among months with trade, quantity and value estimates are similar (minus 0.313 "
          "and minus 0.307 log points). Both ranges include zero, so this is consistent with lower "
          "volume but does not rule out price changes.")


# file properties: the authors, not the library's template defaults
cp = prs.core_properties
cp.author = cp.last_modified_by = "Rahul Reddy Mandadi; Raunaksingh Khalsa"
cp.title, cp.comments = "Borrowed or Real: Presentation 2", ""
out = "slides/Mandadi_Khalsa_Presentation2_v3.pptx"
prs.save(out)
print(f"wrote {out}  ({len(prs.slides._sldIdLst)} slides, {os.path.getsize(out)/1000:.0f} KB)")
