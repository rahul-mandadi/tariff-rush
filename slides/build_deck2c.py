"""Build Presentation 2, third version, as an editable .pptx.

A copy of slides/build_deck2b.py (the submitted v2, left unchanged) brought up to the current
report: the analyst framing, the corrected critical-circumstances numbers and the Taiwan example. Reworked after the
instructor's Presentation 1 notes: one point a slide, talk-size figures from slides/fig_talk.py, and the
detail moved to backup slides. Revised after Raunak's review (2026-11-19): a four-step map of the
project with a step marker on each slide, the model's real output for one month as a table, a chart
of the inputs the model leans on, and a glossary.

Reads:  slides/fig/ (run slides/fig_talk.py first), results/review_queue_watchlist.csv,
        results/model_importance.csv
Writes: slides/Mandadi_Khalsa_Presentation2_v3.pptx
Run:    python3 slides/build_deck2c.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from PIL import Image
import os
import pandas as pd

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


STEPS = ["COLLECT", "MEASURE", "PREDICT", "TEST"]


def chrome(s, names=True, step=None):
    # step marker, top left: where this slide sits in the four steps of slide 4
    if step:
        tb = s.shapes.add_textbox(Inches(X0), Inches(Y_FOOT), Inches(5.2), Inches(0.30))
        p = tb.text_frame.paragraphs[0]
        for n, name in enumerate(STEPS, 1):
            r = p.add_run()
            r.text = f"{n} {name}" + ("      " if n < len(STEPS) else "")
            r.font.size, r.font.name = Pt(10), FONT
            r.font.bold = n == step
            r.font.color.rgb = RED if n == step else GREY
    if names:
        txt(s, FOOT, 6.00, Y_FOOT, 6.58, 0.30, 9, color=GREY, align=PP_ALIGN.RIGHT)
    ln = s.shapes.add_connector(1, Inches(X0), Inches(Y_RULE),
                                Inches(X0 + CW), Inches(Y_RULE))
    ln.line.color.rgb = GREY
    ln.line.width = Pt(0.75)


def add(headline, fig=None, caption=None, notes="", bullets=None, bullet_size=22,
        bullet_top=2.10, bullet_step=0.50, take_y=Y_TAKE, take_rule=False, step=None):
    if len(headline) > 46:
        raise SystemExit(
            f"headline is {len(headline)} characters: {headline!r}\n"
            "At 38pt bold it wraps to a second line and draws over the figure. Keep it to 46.")
    s = prs.slides.add_slide(BLANK)
    chrome(s, step=step)
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


def side(headline, fig, bullets, notes, step=None, caption=None, size=19, tops=(2.1, 3.4, 4.7), fig_w=5.3):
    """Bullets on the left, a figure on the right."""
    s = prs.slides.add_slide(BLANK)
    chrome(s, step=step)
    txt(s, headline, X0, Y_HEAD, CW, 0.80, 38, bold=True)
    for y, b in zip(tops, bullets):
        txt(s, b, X0 + 0.15, y, CW - fig_w - 0.55, 1.3, size, color=GREY, spacing=1.12)
    p = f"{FIG}/{fig}"
    iw, ih = Image.open(p).size
    maxh = (Y_TAKE - 0.30 if caption else H - 0.55) - 2.0
    wid = min(fig_w, maxh * iw / ih)
    s.shapes.add_picture(p, Inches(X0 + CW - wid), Inches(2.0), width=Inches(wid), height=Inches(wid * ih / iw))
    if caption:
        r = s.shapes.add_connector(1, Inches(X0), Inches(Y_TAKE - 0.14), Inches(X0 + CW), Inches(Y_TAKE - 0.14))
        r.line.color.rgb = GREY
        r.line.width = Pt(0.75)
        txt(s, caption, X0, Y_TAKE, CW, 0.75, 17, color=GREY, spacing=1.12)
    s.notes_slide.notes_text_frame.text = notes
    return s


# ================================================================ MAIN TALK (about ten minutes)
# Rahul: slides 1 to 8 (the project, copper, the four steps, the design, what happens after a duty,
#        the analyst's decision).
# Raunak: slides 9 to 14 (how the model ranks the list, four models and where the gain comes from, its
#        output for one month, Taiwan, the result, what it means).

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
    "TIMING: about 15 minutes at a normal pace. Rahul, slides 1 to 8 (about 8 minutes). Raunak, slides 9 "
    "to 14 (about 7 minutes). Backup slides follow slide 14 for questions, starting with a glossary.\n\nRAHUL: Hi everyone. We're Rahul and Raunak. Our project is called Borrowed "
    "or Real.\n\nThe question is simple. After a trade duty, does the business come "
    "back?\n\nSpoiler: more than half the time, it doesn't. The rest of this talk is how we "
    "know, and how to tell which ones.")

# ---------------------------------------------------------------- M1b what the project is about
# the stakes: imports from the named country in the named products, 12 months before each duty,
# 2016 to 2025, an upper bound (measure/stakes_check.py); the 2024 aluminum cases are left out of the
# yearly figure because their 96 catch-all codes alone add about 70 billion
st_ = pd.read_csv("results/stakes_by_year.csv")
sc_ = pd.read_csv("results/stakes_cases.csv").query("2016 <= year <= 2025")
assert round((st_.pre12_bn - st_.aluminum_2024_bn).mean()) == 17 and round(st_.pre12_bn.mean()) == 24
assert round(sc_.pre12.median() / 1e6, -1) == 90 and round(sc_[sc_.aluminum_2024].pre12.sum() / 1e9) == 70
add("What this project is about.",
    bullets=[
        "**The problem:** after a U.S. duty, imports from the named country often fall. Do they come back?",
        "**Who needs it:** an analyst at a U.S. importer, who can check only a few declines. A lasting one "
        "may mean a new supplier.",
        "**The data science problem:** predict which declines will last, from public trade data.",
    ],
    bullet_size=24, bullet_top=2.10, bullet_step=1.12,
    caption="Borrowed: buyers bought early and will come back. Real: the business has moved somewhere else.",
    take_rule=True,
    notes=(
          "RAHUL: So what is this project about? Three parts.\n\nThe problem. After a U.S. duty, "
          "imports from the named country, the one the duty names, often fall. That part is "
          "expected. The real question is: do they come back?\n\nThat's our title. Borrowed: buyers "
          "bought early, or just paused, and will come back. Real: the business has moved somewhere "
          "else.\n\nWho needs it. Picture an analyst at a U.S. importer. They watch many products hit "
          "by duties, and they can check only a few declines. If a drop will pass, they can wait. A "
          "lasting one may mean a new supplier, and qualifying one can take up to a year and a half. So "
          "knowing early matters.\n\nAnd the stakes are real. Each year, these duties hit up to about 17 "
          "billion dollars of imports. A typical case, about 90 million.\n\nThe same list also fits anyone watching all U.S. imports, like a "
          "trade-credit insurer or a supply-risk service. For them, the whole monthly list is "
          "theirs.\n\nThe data science problem. Predict which declines "
          "will last, from public trade data, and put those first on the analyst's list.\n\nHere's "
          "where the idea started.\n\nIf asked where the 17 billion comes from: imports from the named "
          "country in the named products, in the 12 months before each duty, 2016 to 2025. It's an "
          "upper bound, because notices list catch-all product codes. It leaves out the 2024 aluminum "
          "case, whose 96 codes alone would add about 70 billion. With it, 24 billion a year, under 1 "
          "percent of U.S. imports.\n\nIf asked whether an analyst could just check everything: for one "
          "importer, maybe; its own list is a handful. The order matters most when the list is long "
          "and time is short, like for someone watching all U.S. imports. And our first finding, that "
          "most declines last, holds either way.\n\nIf asked whether buyers really bought early: in copper, yes. In "
          "the duty cases we study, we found no clear rush. So for us, borrowed simply means the "
          "drop passes.\n\nIf asked what changed since Presentation 1: last time we asked three "
          "questions. Can we see a rush coming? What happens after the duty? How long does it last? "
          "Public data couldn't tell a rush apart from normal growth. So we focused on the last "
          "two, using antidumping cases, and added the forecast."))

# ---------------------------------------------------------------- M2 copper, the starting example
add("Copper came back, but not the taxed part.", fig="t2_copper_split.png",
    caption="U.S. copper imports, tonnes a month. Red: taxed by the 2025 duty. Grey: not taxed.",
    notes=(
          "RAHUL: Copper came back, but not the taxed part. Copper is what got us started.\n\nIn "
          "August 2025 the U.S. put a 50% tariff on some copper products. Total copper imports "
          "fell, then came back. So it looked borrowed.\n\nBut look at what the tariff actually "
          "taxed. In red, the taxed products, like wire, tubes and sheets. They fell from about 49 "
          "thousand tonnes a month to 27, and stayed there.\n\nIn grey, not taxed: refined copper. "
          "That's what came back.\n\nSo the total hid the real story. You have to look at the exact "
          "products a duty names. And one example proves very little, so we turned to hundreds of "
          "past duty cases.\n\nIf asked what the red line covers: the semi-finished copper the tariff "
          "named, like bars, wire, sheets, foil, tubes and fittings. Refined copper wasn't "
          "named.\n\nIf asked about the jump in refined copper just before the tariff: buyers brought "
          "copper in ahead of it. That's a different kind of tariff from the ones we study. In "
          "antidumping cases we find no clear rush.\n\nIf asked why copper, when the method uses "
          "antidumping cases: copper shows why we look at the exact products. Its tariff taxed "
          "every country, so there's no untaxed country to compare with. That's also why the 2025 "
          "tariffs are not in the method."))

# ---------------------------------------------------------------- M3b what we did, in four steps
s = prs.slides.add_slide(BLANK)
chrome(s)
txt(s, "What we did, in four steps.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
# counts: 502 cases and 381 with 18 months (FINAL_REPORT.md section 2.1; slides/fig_funnel.py asserts
# both); the scored lists from the review files; the trade data's span from the panel itself
ep_ = pd.read_csv("results/adcvd_episodes_collapsed.csv")
wl_ = pd.read_csv("results/review_queue_watchlist.csv")
cap_ = pd.read_csv("results/review_queue_capacity.csv").query("capacity == 0.2 and ranking == 'forecast (boosting)'")
months_ = sorted(f[:7] for f in os.listdir("panel/hs8") if f.endswith(".parquet"))
assert len(ep_) == 502 and wl_.decision_month.nunique() == 44
assert (wl_.decision_month.min()[:4], wl_.decision_month.max()[:4]) == ("2020", "2025")
assert (int(cap_.relationships.iloc[0]), int(cap_.cases.iloc[0])) == (936, 198)
assert (months_[0], months_[-1], len(months_)) == ("2015-01", "2026-08", 140)
BOX = [("Collect", "10,730 duty notices. 502 cases, matched to U.S. imports."),
       ("Measure", "The named country against its rivals, for 18 months."),
       ("Predict", "At month 4: each decline's chance of not coming back by month 18."),
       ("Test", "Each month's list, against biggest drop first.")]
bw, gap, by, bh = 2.55, 0.543, 1.95, 2.85
for n, (name, body) in enumerate(BOX):
    bx = X0 + n * (bw + gap)
    box = s.shapes.add_shape(1, Inches(bx), Inches(by), Inches(bw), Inches(bh))
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor(0xF3, 0xF4, 0xF6)
    box.line.fill.background()
    box.shadow.inherit = False
    txt(s, str(n + 1), bx + 0.22, by + 0.10, 1.0, 0.6, 30, bold=True, color=RED)
    txt(s, name, bx + 0.22, by + 0.62, bw - 0.4, 0.5, 22, bold=True)
    txt(s, body, bx + 0.22, by + 1.15, bw - 0.4, 1.6, 17, color=GREY, spacing=1.12)
    if n < 3:
        txt(s, "\u2192", bx + bw, by + bh / 2 - 0.35, gap, 0.6, 26, color=GREY, align=PP_ALIGN.CENTER)
r = s.shapes.add_connector(1, Inches(X0), Inches(Y_TAKE - 0.14), Inches(X0 + CW), Inches(Y_TAKE - 0.14))
r.line.color.rgb = GREY
r.line.width = Pt(0.75)
# the years: one bar for the trade data, one for the test lists, on a shared month scale
NM = len(months_)                                       # 140 months, January 2015 to August 2026
lm_ = sorted(wl_.decision_month.unique())               # list months, June 2020 to June 2025
T0 = (int(lm_[0][:4]) - 2015) * 12 + int(lm_[0][5:]) - 1
T1 = (int(lm_[-1][:4]) - 2015) * 12 + int(lm_[-1][5:])
assert (lm_[0], lm_[-1], T0, T1) == ("2020-06", "2025-06", 65, 126)
def xm(m):                                              # m = months since January 2015
    return X0 + CW * m / NM
for y_, m0, m1, col, lab in [(5.02, 0, NM, GREY, "Monthly U.S. imports, January 2015 to August 2026"),
                             (5.45, T0, T1, RED, "Test: 44 monthly lists, 2020 to 2025")]:
    bar = s.shapes.add_shape(1, Inches(xm(m0)), Inches(y_), Inches(xm(m1) - xm(m0)), Inches(0.36))
    bar.fill.solid()
    bar.fill.fore_color.rgb = col
    bar.line.fill.background()
    bar.shadow.inherit = False
    txt(s, lab, xm(m0) + 0.12, y_ + 0.02, xm(m1) - xm(m0) - 0.2, 0.34, 14, bold=True,
        color=RGBColor(0xFF, 0xFF, 0xFF))
for yr in range(2015, 2027):
    txt(s, str(yr), xm((yr - 2015) * 12) - 0.3, 5.84, 0.6, 0.3, 12, color=GREY, align=PP_ALIGN.CENTER)
txt(s, "**A fair test:** each year's lists are ranked by a model trained only on cases already finished, "
       "using data out by month 4.", X0, Y_TAKE, CW, 0.75, 17, color=GREY, spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "RAHUL: Here's what we did, in four steps. The small marker at the top of every slide "
    "tells you which step we're on.\n\nOne, collect. 10,730 duty notices since 2015. Most are "
    "about old cases, like yearly reviews. What's left is 502 cases, each matched to U.S. "
    "imports.\n\nTwo, measure. The named country against its rivals, for 18 months after the "
    "duty. We use the cases with all 18 months of data.\n\nThree, predict. At month 4: each "
    "decline's chance of not coming back by month 18. It's a yes or no, because the analyst's "
    "choice is yes or no too: check it, or don't.\n\nFour, test. Each month's list, against a "
    "simple rule: check the biggest drops first. Our score: of the declines the analyst "
    "checks, how many really did not come back.\n\nThe bars show the years. Monthly U.S. "
    "imports, January 2015 to August 2026. In red, the test: 44 monthly lists, 2020 to "
    "2025.\n\nAnd a fair test: each year's lists are ranked by a model trained only on cases "
    "already finished, using data out by month 4. So the model never sees the answers before "
    "the exam.\n\nIf asked what \"out by month 4\" means: Census runs about two months behind. So "
    "at month 4 we use trade data through month 2, and notices published by the end of month "
    "3.\n\nIf asked how many were scored: 198 cases, 936 product and country pairs.\n\nIf asked "
    "why 2015: the project started with the 2018 tariffs, and our first method needed three "
    "normal years before them. The data window stayed when we moved to antidumping cases.\n\nIf "
    "asked why 18 months: by then, the ones coming back have mostly come back. Of the "
    "countries that fell, 23 percent were back by month 12 and 25 percent by month 18. And "
    "the trade commission's final decision is public at about month 6, so month 18 is a year "
    "after the duty's fate is known.")

# ---------------------------------------------------------------- M4 the design
add("We follow one product from one country.",
    bullets=[
        "**Antidumping and countervailing duties:** one product from one country, like mattresses "
        "from Vietnam.",
        "**Rivals keep selling it:** we compare Vietnam's share of U.S. mattress imports with theirs.",
        "**A check:** the same method on a fake date, two years earlier.",
    ],
    bullet_size=24, bullet_top=2.25, bullet_step=1.05,
    caption="Antidumping: a duty on goods sold below fair value. Countervailing: a duty on goods "
            "helped by government subsidies.",
    take_rule=True, step=2,
    notes=(
          "RAHUL: Step two, measure. We follow one product from one country.\n\nWhy? Many tariffs in "
          "the news tax almost every country at once. That leaves nobody untaxed to compare "
          "with.\n\nAntidumping and countervailing duties are narrower: one product from one country, "
          "like mattresses from Vietnam. "
          "Antidumping answers goods sold below fair value. Countervailing answers goods helped by "
          "government subsidies.\n\nRivals keep selling it. Other countries keep selling mattresses "
          "here. So we compare Vietnam's share of U.S. mattress imports with theirs, month by "
          "month. Anything that hits all mattresses, like inflation, cancels out.\n\nA check: the "
          "same method on a fake date, two years earlier. There was no duty yet, so nothing should "
          "happen. If our method still finds a drop there, the method is making it up."))

# ---------------------------------------------------------------- M5 the aftermath
add("Where duties stayed: 31% below rivals.", fig="t4_aftermath.png", step=2,
    caption="Red: the 326 cases where the trade commission kept the duty, so it became permanent. Shading: "
            "where the true value likely falls (95% range). Grey: the same cases on a fake date.",
    notes=(
          "RAHUL: So what happens? Where duties stayed, the named country averaged 31 percent below "
          "its rivals over the 18 months after. Put simply: if its rivals sold the same as before, "
          "the named country sold about 31 percent less.\n\nZero on this chart is where it stood "
          "against its rivals a year and a half before the duty.\n\nThe red line is the 326 cases "
          "where the trade commission, the U.S. agency that votes on whether a duty stays, kept it. "
          "So it became permanent. By the last six months, it was about 37 percent below, and still "
          "falling. The shading is where the true value likely falls, a 95 percent range.\n\nThe grey "
          "line is the fake date: the same method, two years earlier, on the 283 cases with enough "
          "earlier data. No drop. If anything, it drifts up about 6 percent. So the drop isn't "
          "something our method creates.\n\nOne honest caveat: that still doesn't prove the duty "
          "alone caused it. Other things could matter, like which companies get named in a "
          "case.\n\nIf asked about a rush of buying before the duty: the red line sits a little above "
          "zero before, but there's no clear rush.\n\nIf asked what happens when the duty is lifted: "
          "no lasting fall. That group is small, 45 cases and mostly one aluminum investigation, so "
          "we don't lean on it. Backup slide 21.\n\nIf asked for the exact numbers: minus 0.37 log "
          "points, standard error 0.065. The fake date is plus 0.06, standard error 0.03, on the "
          "283 cases with enough earlier data.\n\nIf asked whether the country fell or its rivals "
          "grew: we measure its share against its rivals, not its imports alone. Two things we can "
          "add. The chance the product is traded at all falls 9 points. And quantity falls about as "
          "much as dollars. Where the trade went instead, we have not measured.\n\nIf asked about "
          "goods rerouted through another country: Census records the declared country of origin. "
          "Relabeled goods would count as the other country's. We can't separate that. It's a "
          "limit."))

# ---------------------------------------------------------------- M6 outcomes and the meaning of recovery
add("More than half did not come back.", fig="t5_outcomes.png", step=2,
    caption="Fell: within 6 months, share at least a fifth below its level a year and a half before the "
            "duty. Came back: back to that level 3 months in a row by month 18. 380 cases.",
    notes=(
          "RAHUL: That was the average. Now case by case: more than half did not come back.\n\nFirst, "
          "what we mean. A country fell if, within six months, its share dropped at least a fifth "
          "below its level before the case. It came back if its share returned to that level and "
          "stayed there three months in a row, by month 18. One good month doesn't count.\n\nThese "
          "are the 380 cases with a full 18 months of data so far. 26 percent did not fall. 17 "
          "percent fell and came back. 57 percent fell and did not come back. That includes 16 "
          "percent where the country sold none of it at all in the last six months.\n\nOn the fake "
          "date, only 21 percent fell without coming back.\n\nSo for these duties, the answer is "
          "closer to real than borrowed. But an analyst doesn't act on averages. They need to know "
          "which declines will last.\n\nIf asked why 42 and 16 make 58: rounding. Unrounded, it's "
          "57.3 percent."))

# ---------------------------------------------------------------- M7 the analyst's decision
s = prs.slides.add_slide(BLANK)
chrome(s, step=3)
txt(s, "Which declines should an analyst check first?", X0, Y_HEAD, CW, 0.80, 38, bold=True)
# one real month, as a timeline: Taiwan's duty started September 2024, so January 2025 is its month 4.
# How that list turned out (forecast/review_queue.py writes the watchlist; remained_down = not back by month 18)
JAN = pd.read_csv("results/review_queue_watchlist.csv").query("decision_month == '2025-01'")
assert len(JAN) == 36
JAN_HIT = int(JAN.sort_values("rank").head(7).remained_down.sum())
JAN_RAND = round(7 * JAN.remained_down.mean())
ZERO = JAN[JAN.latest_vs_pre == 0]                     # biggest drops: tied at no imports at all
assert (JAN_HIT, JAN_RAND, len(ZERO), int(ZERO.remained_down.sum())) == (6, 4, 10, 8)
EVENTS = [("Sep 2024", "Duties start", "New duties, including one on epoxy resins from Taiwan.", GREY),
          ("Oct 2024 on", "Data arrives", "Census runs about two months behind.", GREY),
          ("Jan 2025 (month 4)", "The list", "36 declines, fallen and not back yet. The analyst can check about 7.",
           GREY),
          ("Jan 2025", "Model ranks it", "Most likely to last go first. The analyst checks the top 7.", RED),
          ("Mar 2026 (month 18)", "The answer", f"{JAN_HIT} of the 7 picks had not come back. 7 random "
                                                f"picks: about {JAN_RAND}.", INK)]
LINE_Y, SLOT = 3.35, CW / len(EVENTS)
ln = s.shapes.add_connector(1, Inches(X0 + SLOT / 2), Inches(LINE_Y), Inches(X0 + CW - SLOT / 2), Inches(LINE_Y))
ln.line.color.rgb = GREY
ln.line.width = Pt(2)
for i_, (date, title, body, col) in enumerate(EVENTS):
    cx_ = X0 + (i_ + 0.5) * SLOT
    d_ = 0.34 if col == RED else 0.26
    dot = s.shapes.add_shape(9, Inches(cx_ - d_ / 2), Inches(LINE_Y - d_ / 2), Inches(d_), Inches(d_))
    dot.fill.solid()
    dot.fill.fore_color.rgb = col
    dot.line.fill.background()
    dot.shadow.inherit = False
    txt(s, date, cx_ - SLOT / 2 + 0.02, LINE_Y - 0.70, SLOT - 0.04, 0.4, 14, bold=True,
        color=RED if col == RED else GREY, align=PP_ALIGN.CENTER)
    txt(s, title, cx_ - SLOT / 2 + 0.05, LINE_Y + 0.30, SLOT - 0.1, 0.4, 17, bold=True,
        color=RED if col == RED else INK, align=PP_ALIGN.CENTER)
    txt(s, body, cx_ - SLOT / 2 + 0.12, LINE_Y + 0.80, SLOT - 0.24, 1.6, 15, color=GREY,
        align=PP_ALIGN.CENTER, spacing=1.1)
r = s.shapes.add_connector(1, Inches(X0), Inches(Y_TAKE - 0.14), Inches(X0 + CW), Inches(Y_TAKE - 0.14))
r.line.color.rgb = GREY
r.line.width = Pt(0.75)
txt(s, "**The obvious rule: check the biggest drops first.** Anyone can do that with public data. Our model "
       "has to beat it.", X0, Y_TAKE, CW, 0.75, 17, color=GREY, spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "RAHUL: So which declines should an analyst check first? Here's one real month.\n\nDuties "
    "start. September 2024: new duties, including one on epoxy resins from Taiwan.\n\nData "
    "arrives, but Census runs about two months behind. So by January 2025, month 4, the "
    "analyst can see the first three months after the duty.\n\nThe list: 36 declines, fallen "
    "and not back yet. The analyst has time to check about seven. So, which seven?\n\nThat's "
    "where our model comes in. The model ranks it: the most likely to last go first. The "
    "analyst checks the top seven.\n\nThe answer comes at month 18, in March 2026. Six of the "
    "seven picks had not come back. That's our score for this month: six out of seven. Seven "
    "random picks would have found about four.\n\nBut random is a low bar. The obvious rule: "
    "check the biggest drops first. Anyone can do that with public data. Our model has to "
    "beat it.\n\nIf asked whether the biggest-drop rule did as well this month: about as well. "
    "Ten declines were tied at no imports at all, and 8 of those 10 had not come back. The "
    "model's edge shows across all 44 lists, which Raunak covers.\n\nIf asked whether one "
    "importer would see 36 declines: no. This is the list across all U.S. imports, and "
    "January 2025 was a big month; a typical month has about 8. One importer sees only its "
    "own products, a handful at most. Someone watching all U.S. imports, like a "
    "trade-credit insurer, sees the whole list.\n\nIf asked what checking means: "
    "looking into that decline with the company's own supplier information. What the analyst "
    "does next, we did not test.\n\nIf asked why month 4: it's the first month the model ranks "
    "well, an AUC of 0.73 at month 3 and 0.795 at month 4. It comes before the trade "
    "commission's vote, which is never public by month 4. And the decision is still open: "
    "qualifying a new supplier can take up to 18 months. We picked month 4 with the accuracy "
    "in view, so months 6 and 8 are our checks.\n\nHANDOFF: Raunak will show how our model "
    "orders that list, and whether it beats the biggest drops.")

# ---------------------------------------------------------------- M7b how the model ranks the list
s = prs.slides.add_slide(BLANK)
chrome(s, step=3)
txt(s, "How the model ranks each month's list.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
for y, b_ in [(2.10, "**23 public inputs:** the market before, the case, the fall so far, the month."),
              (3.45, "**Gradient boosting:** gives each decline a chance of not coming back by month 18."),
              (4.65, "**No automatic selection:** inputs set before the list test, never changed.")]:
    txt(s, b_, X0 + 0.15, y, 6.05, 1.2, 20, color=GREY, spacing=1.12)
# permutation importance on the held-out years (forecast/model_explain.py, report Appendix K),
# indexed so the latest share is 100
imp = pd.read_csv("results/model_importance.csv").set_index("feature").brier_increase
TOP = [("latest", "latest share"), ("rush", "share just before the duty"),
       ("log_pre_value", "imports before the case"), ("hhi", "market concentration"),
       ("log_rate", "duty rate"), ("slope", "last three months' trend")]
assert list(imp.sort_values(ascending=False).index[:6]) == [k for k, _ in TOP]
rel_ = [round(100 * imp[k] / imp["latest"]) for k, _ in TOP]
assert rel_ == [100, 19, 13, 11, 7, 5], rel_
cx = X0 + 6.55
txt(s, "Which inputs matter most", cx, 2.0, CW - 6.55, 0.4, 17, bold=True)
txt(s, "If we scramble one input, how much worse does the forecast get? Latest share = 100.", cx, 2.38,
    CW - 6.55, 0.6, 13, color=GREY, spacing=1.05)
cd = CategoryChartData()
cd.categories = [lab for _, lab in TOP][::-1]  # a bar chart draws its first category at the bottom
cd.add_series("importance", rel_[::-1])
ch = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(cx - 0.1), Inches(2.95),
                        Inches(CW - 6.45), Inches(3.25), cd).chart
ch.has_legend = ch.has_title = False
ch.font.name, ch.font.size = FONT, Pt(14)
ch.font.color.rgb = INK
pl = ch.plots[0]
pl.gap_width = 55
pl.has_data_labels = True
pl.data_labels.number_format, pl.data_labels.number_format_is_linked = "0", False
pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl.data_labels.font.size, pl.data_labels.font.bold = Pt(14), True
for i_ in range(len(TOP)):
    pt = pl.series[0].points[i_]
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = RED if i_ == len(TOP) - 1 else RGBColor(0xA9, 0xAD, 0xB3)
va = ch.value_axis
va.visible, va.has_major_gridlines = False, False
va.minimum_scale, va.maximum_scale = 0, 118
ch.category_axis.format.line.fill.background()
ch.category_axis.has_major_gridlines = False
r = s.shapes.add_connector(1, Inches(X0), Inches(Y_TAKE - 0.14), Inches(X0 + CW), Inches(Y_TAKE - 0.14))
r.line.color.rgb = GREY
r.line.width = Pt(0.75)
txt(s, "Each prediction used only data out by month 4, and only older cases whose outcomes were "
       "known.", X0, Y_TAKE, CW, 0.75, 17, color=GREY, spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "RAUNAK: Thanks, Rahul. How the model ranks each month's list, in three lines.\n\n"
    "First, 23 public inputs, in four groups. The market before, like how concentrated it was. "
    "The case, like the duty rate. The fall so far, like the latest share Census has published. "
    "And the month, with the trade commission's vote once it is public.\n\n"
    "Second, gradient boosting. It's many small decision trees, each fixing the mistakes of the "
    "ones before. It gives each decline a chance of not coming back by month 18, and the list is "
    "sorted by that chance. Why boosting? We started with logistic regression, the simple "
    "standard. Boosting can learn a cutoff by itself, like the one on the next slide, and it "
    "ranked better than logistic regression on held-out years, so we kept it.\n\n"
    "Third, no automatic selection. The inputs were set before the list test and never "
    "changed.\n\n"
    "Which inputs matter most? The chart shows what the model leans on. We scramble one input and "
    "see how much worse the forecast gets. The latest share matters most, about five times more "
    "than the next one.\n\n"
    "And each prediction used only data out by month 4, and only older cases whose outcomes were "
    "known.\n\n"
    "If asked how it was tuned: the number of trees was tuned on the older cases only, keeping "
    "each investigation together. The other settings were fixed by hand.\n\n"
    "If asked about the trade commission's vote: it's an input, but at month 4 it isn't public "
    "yet in any case. It only matters at later months.\n\n"
    "If asked why month 4: we chose it after seeing the test accuracy, so months 6 and 8 are our "
    "checks.\n\n"
    "If asked what share just before the duty means: the share in the six months before the duty, "
    "compared with its earlier level. The report calls it the pre-case rush.")

# ---------------------------------------------------------------- M8 the model's output for one month
w_ = pd.read_csv("results/review_queue_watchlist.csv", dtype={"hs8": str})
jan = w_[w_.decision_month == "2025-01"].reset_index(drop=True)
jan["drop_rank"] = jan.latest_vs_pre.rank(method="min").astype(int)
top = jan.sort_values("rank").head(7)
NAME = {"Ferrosilicon": "Ferrosilicon", "Epoxy Resins": "Epoxy resins",
        "2,4-Dichlorophenoxyacetic Acid": "2,4-D weed killer", "Ceramic Tile": "Ceramic tile"}
assert len(jan) == 36 and list(top["rank"]) == list(range(1, 8))
assert list(top.drop_rank) == [1, 20, 21, 25, 26, 23, 11] and (jan.latest_vs_pre == 0).sum() == 10
assert list(top.remained_down) == [1, 1, 1, 1, 0, 1, 1] and jan.remained_down.sum() == 20
s = prs.slides.add_slide(BLANK)
chrome(s, step=3)
txt(s, "What the model hands the analyst.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
txt(s, "January 2025: 36 declines, sorted by the model. The analyst checks the top 7.",
    X0, 1.85, CW, 0.5, 20, color=GREY)
HEAD = ["Model's\nrank", "Product", "Country", "Share now, % of\nits earlier level",
        "Model's chance it\ndoesn't come back", "Rank by\nbiggest drop"]
CWID = [1.25, 3.10, 1.95, 2.10, 2.03, 1.40]
tb = s.shapes.add_table(len(top) + 1, len(HEAD), Inches(X0), Inches(2.45), Inches(sum(CWID)),
                        Inches(0.62 + 0.42 * len(top))).table
tb.first_row = tb.horz_banding = False
for j_, wd in enumerate(CWID):
    tb.columns[j_].width = Inches(wd)
tb.rows[0].height = Inches(0.62)
rows = [HEAD] + [[str(r_["rank"]), NAME[r_["product"]], r_.country, f"{100 * r_.latest_vs_pre:.0f}%",
                  f"{100 * r_.p_not_recovered:.0f}%", "1 (tied)" if r_.drop_rank == 1 else str(r_.drop_rank)]
                 for _, r_ in top.iterrows()]
for i_, row in enumerate(rows):
    if i_:
        tb.rows[i_].height = Inches(0.42)
    taiwan_row = i_ and row[2] == "Taiwan"
    for j_, val in enumerate(row):
        cell = tb.cell(i_, j_)
        cell.fill.solid()
        cell.fill.fore_color.rgb = (RGBColor(0xF3, 0xF4, 0xF6) if i_ == 0 else
                                    RGBColor(0xFB, 0xE7, 0xEA) if taiwan_row else RGBColor(0xFF, 0xFF, 0xFF))
        cell.margin_top = cell.margin_bottom = Inches(0.03)
        tf = cell.text_frame
        tf.text = ""
        for k_, line in enumerate(val.split("\n")):
            p = tf.paragraphs[0] if k_ == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.LEFT if j_ in (1, 2) else PP_ALIGN.CENTER
            rr = p.add_run()
            rr.text = line
            rr.font.name = FONT
            rr.font.size = Pt(13 if i_ == 0 else 17)
            rr.font.bold = i_ == 0 or bool(taiwan_row)
            rr.font.color.rgb = GREY if i_ == 0 else RED if taiwan_row else INK
r = s.shapes.add_connector(1, Inches(X0), Inches(Y_TAKE - 0.14), Inches(X0 + CW), Inches(Y_TAKE - 0.14))
r.line.color.rgb = GREY
r.line.width = Pt(0.75)
txt(s, "Share now: the last three months Census has published, against the level a year and a half "
       "before the duty. The model's chances run a bit high; the order is what counts.", X0, Y_TAKE, CW, 0.75, 17, color=GREY,
    spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "RAUNAK: What the model hands the analyst: its real output for January 2025.\n\n"
    "That month, 36 declines were on the list. The model sorted them, and the analyst checks the "
    "top fifth, about seven.\n\n"
    "Each row is one product from one country. You see how far its share has fallen, and the "
    "model's chance it doesn't come back. The last column is where the biggest-drop rule would put "
    "it. Brazil's ferrosilicon is on twice because it is two product codes.\n\n"
    "Five of the model's top seven are 20th or lower on that rule. Why, if the latest share matters "
    "most? Once a share is below about 60 percent of its earlier level, falling further barely "
    "changes the model's answer. Then the case and the market decide the order.\n\n"
    "Row two is epoxy resins from Taiwan. Let's follow it.\n\n"
    "If asked about the chances: they run about 6 points high on average (report Appendix K). So "
    "the analyst uses the order, not the exact number.\n\n"
    "If asked about the 0% rows: ten declines had no imports in the latest three months, so they "
    "tie for first on biggest drop.")

# ---------------------------------------------------------------- M9 Taiwan: what happened later
add("Later: Taiwan had not come back.", fig="t6_taiwan_later.png", step=4,
    caption="Epoxy resins from Taiwan. Red: what the analyst could see in January 2025, data through "
            "November (month 2). Grey: what happened next.",
    notes="RAUNAK: This is row two, epoxy resins from Taiwan. The duty started in September "
          "2024.\n\n"
          "The red line is what the analyst could see in January. Census runs two months behind, so "
          "the data stops at month 2. Taiwan's share had been sliding even before the duty. By "
          "then it was 42 percent of its level a year and a half before. The biggest-drop rule "
          "ranked it 20th, so it wouldn't get checked. The model ranked it 2nd.\n\n"
          "The grey line is what happened next. By month 18, March 2026, Taiwan was at 26 percent. "
          "It had not come back, like five others in the model's top seven that month.\n\n"
          "But one month doesn't prove the model is better. For that, we need every month.\n\n"
          "If asked what 42 percent means: Taiwan went from 10.3 percent of these imports to 4.4 "
          "percent. That's 42 percent of its old share, not 42 percent of all U.S. imports.")

# ---------------------------------------------------------------- M10 the result
add("The model's picks: 82% did not come back.", fig="t7_review_result.png", step=4,
    caption="Precision: the share of checks that found a decline that did not come back. 44 monthly lists, "
            "2020 to 2025. At each share, taken one at a time, the 90% range of the gap stays above zero.",
    notes="RAUNAK: Now every month, not just one. We ran this on 44 monthly lists, from 2020 to "
          "2025.\n\n"
          "Each month, the analyst checks the top fifth of the list. That's about 187 checks in "
          "total. Then we wait until month 18 and ask: did each checked decline come back?\n\n"
          "This is precision. We score the top of the list, because that's all the analyst acts "
          "on.\n\n"
          "With the model's order, 82 percent of the checks found declines that had not come back "
          "by month 18. "
          "With biggest drop first, 70 percent. With a random order, 62 percent, the rate for all the "
          "declines on these lists.\n\n"
          "The line shows the same at every share the analyst might check, from 5 percent of the "
          "list to half of it.\n\n"
          "So with the same 187 checks, the model finds about 22 more lasting declines. The gap is "
          "12 points. Our 90 percent range for it runs from 3.9 to 15.7, so it is clearly above "
          "zero. It also holds at months 6 and 8, and without the biggest investigation.\n\n"
          "If asked for those numbers: month 6, 88 against 76. Month 8, 89 against 81. Without "
          "aluminum extrusions in 2024, 14 countries and nearly half the pairs, 89 against 77. We "
          "added that last check after seeing the first results.\n\n"
          "If asked whether you chose things with the test years in view: yes. Month 4 and boosting "
          "were picked with these years' accuracy in view. That's why the frozen forecast on the last "
          "slide matters. It's the first test on outcomes nobody has seen yet.\n\n"
          "If asked whether the fall cutoff matters: with a cutoff of 10 or 30 percent instead of 20, "
          "the outcome shares barely "
          "move (backup). We did not rerun the lists with other cutoffs.\n\n"
          "If asked why 62 here and 57 on slide 7: different groups. 57 is all 380 cases, including "
          "ones that never fell. 62 is the declines on the 2020 to 2025 lists, counted one product "
          "at a time.")

# ---------------------------------------------------------------- M7c four models, and where the gain comes from
# precision at 20% (share of checks that found a decline that did not come back), each pair counted once:
# model families from forecast/model_family_check.py, the input steps from forecast/feature_ladder.py
# (exploratory, run after the model was fixed), random order from forecast/review_queue.py
fam = pd.read_csv("results/model_family_check.csv").query("capacity == 0.2").set_index("model")
lad = pd.read_csv("results/feature_ladder.csv").query("model == 'boosting'").set_index("step")
rand_ = float(pd.read_csv("results/review_queue_capacity.csv").query("capacity == 0.2").not_back.iloc[0])
MODELS = [("Gradient boosting (ours)", fam.precision["boosting"]), ("Random forest", fam.precision["random forest"]),
          ("Logistic regression", fam.precision["logistic"]), ("Elastic net", fam.precision["elastic net"]),
          ("Biggest drop first, no model", fam.precision["latest share"]), ("Random order", rand_)]
LADDER = [("market before and the case", lad.precision20["a case facts"]),
          ("+ latest share", lad.precision20["b + latest share"]),
          ("+ rest of the fall so far (ours)", lad.precision20["c + how the fall has gone"])]
assert [round(100 * v) for _, v in MODELS] == [82, 84, 82, 81, 70, 62]
assert [round(100 * v) for _, v in LADDER] == [71, 83, 82]
assert abs(LADDER[2][1] - MODELS[0][1]) < 1e-9          # the last step is the reported model
OTHER_ = fam.loc[["random forest", "logistic", "elastic net"]]   # each one's gap to boosting, 90% range
assert (OTHER_.minus_boosting_lo < 0).all() and (OTHER_.minus_boosting_hi > 0).all()
s = prs.slides.add_slide(BLANK)
chrome(s, step=4)
txt(s, "Four models, one answer.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
txt(s, "Checking the top fifth of each list", X0, 2.0, 5.6, 0.4, 17, bold=True)
txt(s, "Share of checks that found a decline that did not come back", X0, 2.38, 5.6, 0.4, 13, color=GREY)
tb = s.shapes.add_table(len(MODELS), 2, Inches(X0), Inches(2.85), Inches(5.6), Inches(0.5 * len(MODELS))).table
tb.first_row = tb.horz_banding = False
tb.columns[0].width, tb.columns[1].width = Inches(4.3), Inches(1.3)
for i_, (lab, v) in enumerate(MODELS):
    tb.rows[i_].height = Inches(0.5)
    ours, rule = i_ == 0, i_ >= 4
    for j_, val in enumerate([lab, f"{100 * v:.0f}%"]):
        cell = tb.cell(i_, j_)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0xFB, 0xE7, 0xEA) if ours else RGBColor(0xF3, 0xF4, 0xF6) if rule \
            else RGBColor(0xFF, 0xFF, 0xFF)
        cell.margin_top = cell.margin_bottom = Inches(0.03)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if j_ == 0 else PP_ALIGN.CENTER
        rr = p.add_run()
        rr.text = val
        rr.font.name, rr.font.size = FONT, Pt(17)
        rr.font.bold = ours or j_ == 1
        rr.font.color.rgb = RED if ours else GREY if rule else INK
cx = X0 + 6.35
txt(s, "Where the gain comes from", cx, 2.0, CW - 6.35, 0.4, 17, bold=True)
txt(s, "Our model, adding one group of inputs at a time", cx, 2.38, CW - 6.35, 0.4, 13, color=GREY)
cd = CategoryChartData()
cd.categories = [lab for lab, _ in LADDER][::-1]
cd.add_series("precision", [round(100 * v) for _, v in LADDER][::-1])
ch = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(cx - 0.1), Inches(2.85),
                        Inches(CW - 6.25), Inches(3.0), cd).chart
ch.has_legend = ch.has_title = False
ch.font.name, ch.font.size = FONT, Pt(14)
ch.font.color.rgb = INK
pl = ch.plots[0]
pl.gap_width = 55
pl.has_data_labels = True
pl.data_labels.number_format, pl.data_labels.number_format_is_linked = '0"%"', False
pl.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
pl.data_labels.font.size, pl.data_labels.font.bold = Pt(14), True
for i_ in range(len(LADDER)):                           # the categories run bottom to top
    pt = pl.series[0].points[i_]
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = RED if i_ == 1 else RGBColor(0xA9, 0xAD, 0xB3)
va = ch.value_axis
va.visible, va.has_major_gridlines = False, False
va.minimum_scale, va.maximum_scale = 0, 100
ch.category_axis.format.line.fill.background()
ch.category_axis.has_major_gridlines = False
r = s.shapes.add_connector(1, Inches(X0), Inches(Y_TAKE - 0.14), Inches(X0 + CW), Inches(Y_TAKE - 0.14))
r.line.color.rgb = GREY
r.line.width = Pt(0.75)
txt(s, "No other model differs from boosting beyond its 90% range. In our model, the jump comes from "
       "adding the latest share to the case and the market.", X0, Y_TAKE, CW, 0.75, 17, color=GREY, spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "RAUNAK: Four models, one answer. So is it the model? We tried four, on the same inputs and "
    "the same years.\n\n"
    "Same score as before: checking the top fifth of each list, how many had not come back. "
    "Gradient boosting gets 82 percent. A random forest, 84. Two kinds of regression, 82 and 81. "
    "None differs from boosting beyond its 90 percent range. Why boosting, when the forest scored a "
    "bit higher? We fixed boosting before the list test, from its accuracy on held-out years, and "
    "the 1.4-point gap is inside the uncertainty.\n\n"
    "Where the gain comes from: on the right, our model, adding one group of inputs at a "
    "time. The market before and the case alone get 71, about the same as biggest drop first. Add "
    "the latest share, and it jumps to 83. Adding the rest of the fall so far, which is our full "
    "model, gives 82. No better.\n\n"
    "So in our model, the jump comes from adding the latest share to the case and the market. "
    "Either one alone only matches the simple rule.\n\n"
    "So the choice of model doesn't change what the analyst gets. The inputs do.\n\n"
    "If asked for AUC: 0.795 for boosting, 0.791 for the random forest, 0.75 for the two "
    "regressions.\n\n"
    "If asked whether the split holds for every model: no. A logistic regression gets 79 from the "
    "case and the market alone. How the gain splits depends on the model. What holds for all four "
    "is that they beat the rule.\n\n"
    "If asked why the share just before the duty ranks second on slide 9 but its group adds "
    "nothing here: they answer different questions. Scrambling one input shows what the model uses. "
    "Adding a group shows what it adds beyond the others, and that group overlaps with them.\n\n"
    "If asked why keep all 23 inputs: we fixed them before testing. This breakdown came afterwards, "
    "as a check. Dropping inputs after seeing it would be tuning to the answer.\n\n"
    "If asked whether the latest share alone is a model: it's the biggest-drop rule, sorting by the "
    "latest share. A model given only the latest share and the month sorts each list the same "
    "way.")

# ---------------------------------------------------------------- M11 what it means
add("What this means.",
    bullets=[
        "**Mostly real, not borrowed:** 57% of cases fell and had not come back by month 18.",
        "**At month 4, use the model's list:** 82% of its picks had not come back, against 70% for "
        "biggest drop first.",
        "**Not yet tested with analysts:** we assumed 1 in 5 checked; the model's lead holds from 5% to 50%.",
    ],
    bullet_size=24, bullet_top=2.25, bullet_step=1.05,
    caption="Next: on November 15 we froze a forecast of 197 declines. We'll score it as new data "
            "comes out, from December 2026 to early 2028.",
    take_rule=True,
    notes="RAUNAK: What this means. Three things.\n\n"
          "First, mostly real, not borrowed. 57 percent of cases fell and had not come back by "
          "month 18.\n\n"
          "Second, at month 4, use the model's list. 82 percent of its picks had not come back, "
          "against 70 percent for biggest drop first. That's about 4 in 5 of its picks, against 7 in 10.\n\n"
          "Third, not yet tested with analysts. We assumed 1 in 5 checked, and the model's lead holds "
          "from 5 to 50 percent. And we predict a country's recovery in a product, not whether one company "
          "survives. The list fits an importer's analyst, and anyone watching all U.S. imports. Neither "
          "has tried it yet.\n\n"
          "Next: on November 15 we froze a forecast of 197 declines whose outcomes aren't known yet. "
          "We'll score it as new data comes out, from December 2026 to early 2028. Thank you.\n\n"
          "We'd be glad to take your questions. And one for you: who would you hand this list "
          "to?\n\n"
          "If asked how many get scored: 184. One month's list, 13 declines, already had its "
          "outcome public when we froze it.")

# ================================================================ BACKUP
s = prs.slides.add_slide(BLANK)
chrome(s, names=False)
txt(s, "Backup", X0, 2.9, CW, 1.0, 48, bold=True)
txt(s, "Details for questions.", X0, 3.95, CW, 0.6, 22, color=GREY)

# ---------------------------------------------------------------- glossary
TERMS = [
    ("Antidumping duty", "a tax on one product from one country, found selling here below fair value."),
    ("Countervailing duty", "the same, for a product helped by its government's subsidies."),
    ("Permanent order", "the trade commission found U.S. producers were hurt, so the duty stays. "
                        "If not, it is lifted and deposits are refunded."),
    ("Share", "the named country's part of U.S. imports of that product in a month."),
    ("Decline", "one product from one country whose share fell and has not come back yet: what the "
                "list ranks."),
    ("Check", "the analyst looks into a decline with the company's own supplier information. "
              "What happens next is not tested."),
    ("Fell, came back", "share at least a fifth below its pre-duty level within 6 months; back at "
                        "that level 3 months in a row by month 18."),
    ("Month 4", "four months after the duty starts, when Census has published about two months "
                "of trade since."),
    ("Biggest drop first", "the rule with no model: check the largest falls in share first."),
    ("Gradient boosting", "many small decision trees, each fixing the errors of the ones before."),
    ("Fake date", "the same calculation two years before the case. A drop there would come from "
                  "the method, not the duty."),
]
s = prs.slides.add_slide(BLANK)
chrome(s)
txt(s, "Terms we use.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
ys = [1.95, 1.95]
for n, (term, meaning) in enumerate(TERMS):
    col = 0 if n < 6 else 1
    txt(s, f"**{term}:** {meaning}", X0 + col * 6.05, ys[col], 5.75, 0.85, 15, color=GREY, spacing=1.05)
    lines = -(-len(f"{term}: {meaning}") // 62)  # about 62 characters a line at 15pt in this width
    ys[col] += 0.27 * lines + 0.30

# ---------------------------------------------------------------- the fall threshold (report Table K3)
k3 = {}
for line in open("FINAL_REPORT.md"):
    if line.startswith("| below ") and "percent" in line:
        c_ = [x.strip() for x in line.strip().strip("|").split("|")]
        k3[c_[0].replace(" (reported)", "")] = c_[1:3]
assert k3 == {"below 90 percent": ["60%", "23%"], "below 80 percent": ["57%", "21%"],
              "below 70 percent": ["54%", "18%"]}, k3
s = prs.slides.add_slide(BLANK)
chrome(s)
txt(s, "A different cutoff, the same answer.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
txt(s, "We call it a fall when the share drops below 80% of its pre-duty level. Moving that line:",
    X0, 1.95, CW, 0.5, 20, color=GREY)
rows = [["A fall is a share below", "Fell and did not come back", "On the fake date"]] + \
       [[k.replace("below ", "").replace(" percent", "%") + (" (used)" if "80" in k else ""), *v]
        for k, v in k3.items()]
tb = s.shapes.add_table(4, 3, Inches(X0 + 1.2), Inches(2.65), Inches(9.4), Inches(2.3)).table
tb.first_row = tb.horz_banding = False
for j_, wd in enumerate([3.4, 3.2, 2.8]):
    tb.columns[j_].width = Inches(wd)
for i_, row in enumerate(rows):
    tb.rows[i_].height = Inches(0.62 if i_ == 0 else 0.56)
    used = "used" in row[0]
    for j_, val in enumerate(row):
        cell = tb.cell(i_, j_)
        cell.fill.solid()
        cell.fill.fore_color.rgb = (RGBColor(0xF3, 0xF4, 0xF6) if i_ == 0 else
                                    RGBColor(0xFB, 0xE7, 0xEA) if used else RGBColor(0xFF, 0xFF, 0xFF))
        tf = cell.text_frame
        tf.text = ""
        rr = tf.paragraphs[0].add_run()
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        rr.text = val
        rr.font.name, rr.font.size = FONT, Pt(15 if i_ == 0 else 22)
        rr.font.bold = i_ == 0 or used
        rr.font.color.rgb = GREY if i_ == 0 else RED if used else INK
r = s.shapes.add_connector(1, Inches(X0), Inches(Y_TAKE - 0.14), Inches(X0 + CW), Inches(Y_TAKE - 0.14))
r.line.color.rgb = GREY
r.line.width = Pt(0.75)
txt(s, "Only the cutoff changes. The review lists were not rerun with the other cutoffs. From report "
       "Table K3.", X0, Y_TAKE, CW, 0.75, 17, color=GREY,
    spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "If asked why a fifth: it's a choice, so we moved it. At 90 or 70 percent, between 54 and 60 "
    "percent of cases fell and did not come back, against 18 to 23 percent on the fake date. The "
    "answer doesn't hinge on the cutoff. The review lists were not rerun under the other cutoffs.")

# ---------------------------------------------------------------- how the model reads the latest share
pdp = pd.read_csv("results/model_partial_dependence.csv")
pdp = pdp[pdp.feature == "latest"]
lo = pdp[pdp.x <= 0.6].chance_back
assert len(pdp) == 20 and lo.min() > 0.18 and lo.max() < 0.30 and pdp.chance_back.max() > 0.8
s = prs.slides.add_slide(BLANK)
chrome(s)
txt(s, "Below 60%, how far it fell matters little.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
from pptx.chart.data import XyChartData  # noqa: E402
xy = XyChartData()
ser_ = xy.add_series("chance of coming back")
for x_, y_ in zip(pdp.x, pdp.chance_back):
    ser_.add_data_point(round(100 * x_, 1), round(100 * y_, 1))
ch = s.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS, Inches(X0 + 0.3), Inches(1.95),
                        Inches(CW - 0.6), Inches(4.25), xy).chart
ch.has_legend = ch.has_title = False
ch.font.name, ch.font.size = FONT, Pt(15)
ch.font.color.rgb = INK
ln_ = ch.plots[0].series[0].format.line
ln_.color.rgb, ln_.width = RED, Pt(3.5)
ch.plots[0].series[0].smooth = False
va, ca = ch.value_axis, ch.category_axis
va.minimum_scale, va.maximum_scale, va.major_unit = 0, 100, 25
ca.minimum_scale, ca.maximum_scale, ca.major_unit = 0, 130, 20
va.major_gridlines.format.line.color.rgb = RGBColor(0xE3, 0xE5, 0xE8)
ca.has_major_gridlines = False
for ax_, title in [(va, "model's chance of coming back by month 18, %"),
                   (ca, "latest share, % of the country's pre-duty share")]:
    ax_.has_title = True
    ax_.axis_title.text_frame.text = title
    tr = ax_.axis_title.text_frame.paragraphs[0].runs[0]
    tr.font.size, tr.font.bold, tr.font.name = Pt(15), False, FONT
    tr.font.color.rgb = GREY
    ax_.format.line.color.rgb = GREY
r = s.shapes.add_connector(1, Inches(X0), Inches(Y_TAKE - 0.14), Inches(X0 + CW), Inches(Y_TAKE - 0.14))
r.line.color.rgb = GREY
r.line.width = Pt(0.75)
txt(s, "From one model fit on all cases. Below about 60% of the old share, the chance of coming back "
       "stays between 18 and 29%. So other inputs decide the order.", X0, Y_TAKE, CW, 0.75, 17,
    color=GREY, spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "Backup for slide 10, if asked why the ten declines with no imports aren't all at the top. "
    "The model's chance of coming back is roughly flat, about 18 to 29 percent, anywhere below "
    "about 60 percent of the pre-duty share, then climbs steeply. So among the deep falls, how "
    "deep matters little, and inputs like the share just before the duty and the size of the market "
    "set the order. This is from one model fit on all cases, for explanation; the test results use "
    "the held-out predictions.")

# ---------------------------------------------------------------- two ways to pick 7 of 36
add("Two ways to pick 7 of 36.", fig="t9_two_orders.png",
    caption="January 2025, one dot per decline. Filled: had not come back by month 18. Hollow: came back. "
            "Biggest drop first picks from the left; the model picks from the top.",
    notes="Backup for slides 10 and 11, if asked how the model's picks differ from the biggest drops. "
          "Each dot is one decline on January 2025's list. Left to right is how far its share has "
          "fallen. Up and down is the model's chance it doesn't come back. Biggest drop first takes the "
          "ten at 0% first. The model takes the top seven, ringed in red, and five of them are 20th "
          "or lower by drop. Six of those seven had not come back by month 18.")

# ---------------------------------------------------------------- 12 next
add("By month 4, the forecast ranks them better.", fig="19_monthly_forecast.png",
    caption="Declines already visible; each prediction used only earlier cases with known outcomes. Month 4: "
            "given one decline that came back and one that did not, the model puts them in the right order "
            "79.5% of the time (AUC 0.795). A model of the latest share alone gets about 70% of the gain "
            "over history (Brier score).",
    notes="Within a few months the forecast ranks declines better than history alone, and most "
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
          "accuracy, on declines already visible, and the sample is 136 investigation groups, not "
          "the 16,781 product-month rows.")

# ---------------------------------------------------------------- 6 the aftermath (finding 2)
add("Where duties were lifted, no lasting fall.", fig="12_order_vs_negative.png",
    caption="These duties tax one product from one named country. Where the duty became permanent "
            "(326 cases), that country averaged about 31% below its rivals over the 18 months after. "
            "Where the trade commission found no injury and lifted it (45 cases), no lasting fall.",
    notes="Backup for slide 6, if asked what happens when the trade commission lifts the duty. The black line is the 45 cases where it found no injury.\n\n"
          "An antidumping duty answers a complaint that a foreign "
          "producer sells below its home price; a countervailing duty answers a complaint that it "
          "is subsidized. Both name one product and one country, and there are hundreds of them.\n\n"
          "How a case ends: a few months after the duty starts, the U.S. International Trade "
          "Commission votes on whether the imports hurt U.S. producers. Yes, and the duty becomes a "
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
    notes="Each line is one step of the matching. Report Fig. 2 draws every step with what it "
          "drops and why.\n\n"
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
        "earlier, a falsification check: a drop that also shows up there is not the duty's.",
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
            "back; the taxed products did not (slide 3).",
    notes="Backup for slide 3: the total that made copper look borrowed.")

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
