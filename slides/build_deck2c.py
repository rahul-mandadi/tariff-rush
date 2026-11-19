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


# ================================================================ MAIN TALK (about ten minutes)
# Rahul: slides 1 to 8 (the project, copper, the four steps, the design, what happens after a duty,
#        the analyst's decision).
# Raunak: slides 9 to 13 (how the model ranks the list, its output for one month, Taiwan, the result,
#        what it means).

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
    "TIMING: about ten minutes. Rahul, slides 1 to 8 (about 5 minutes). Raunak, slides 9 to 13 "
    "(about 5 minutes). Backup slides follow slide 13 for questions, starting with a glossary.\n\n"
    "RAHUL: We're Rahul and Raunak. Our project asks a simple question: when the U.S. puts a duty "
    "on imports, does the business come back afterwards, or is it gone?")

# ---------------------------------------------------------------- M1b what the project is about
add("What this project is about.",
    bullets=[
        "**The problem:** after a U.S. duty, imports from the named country often fall. Do they "
        "come back?",
        "**Who needs the answer:** an analyst at a U.S. importer. They watch many products hit by "
        "duties, but can only look into a few.",
        "**The data science problem:** use public trade data to predict which declines will last, "
        "and put those first on the list.",
    ],
    bullet_size=24, bullet_top=2.25, bullet_step=1.05,
    notes="RAHUL: Here's the project in three parts.\n\n"
          "The problem. When the U.S. puts a duty on a product from one country, imports from that "
          "country often fall. We want to know if they come back.\n\n"
          "Who cares. Picture an analyst at a U.S. company that imports goods. They track many "
          "products hit by duties. They can't look into every decline, so they need to know which "
          "ones matter.\n\n"
          "The data science problem. Using only public trade data, we predict which declines will "
          "last. Then we put those first on the list.\n\n"
          "If asked what changed since Presentation 1: last time we asked three questions. Can we "
          "see a rush coming? What happens after the duty? How long does it last? Public data "
          "couldn't tell a rush apart from normal growth. So we focused on the last two, using "
          "antidumping cases, and added the forecast.")

# ---------------------------------------------------------------- M2 copper, the starting example
add("Copper came back, but not the taxed part.", fig="t2_copper_split.png",
    caption="U.S. copper imports, tonnes a month. Red: taxed by the 2025 duty. Grey: not taxed.",
    notes="RAHUL: Our title asks if the drop is borrowed or real. Borrowed means buyers bought early "
          "and will come back. Real means the business has moved somewhere else.\n\n"
          "Copper got us started. In August 2025 the U.S. put a 50% duty on some copper products. "
          "Total copper imports fell, then came back. So it looked borrowed.\n\n"
          "But look at what the duty actually taxed. Wire, tubes and sheets fell from about 49 "
          "thousand tonnes a month to 27, and stayed there. Refined copper wasn't taxed, and that's "
          "what came back.\n\n"
          "So the total hid the real story. We have to look at the exact products a duty names. But "
          "copper is one example, and every country paid the duty, so there's no one to compare "
          "with. That's why we turned to hundreds of past duty cases.\n\n"
          "If asked why copper, when the method uses antidumping cases: copper shows why we look at "
          "the exact products. Its duty taxed every country, so there's no untaxed country to "
          "compare with. That's also why the 2025 tariffs are not in the method.")

# ---------------------------------------------------------------- M3b what we did, in four steps
s = prs.slides.add_slide(BLANK)
chrome(s)
txt(s, "What we did, in four steps.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
BOX = [("Collect", "Read 10,730 duty notices. Found 502 cases and matched them to monthly U.S. import data."),
       ("Measure", "Compared each named country with other countries selling the same product."),
       ("Predict", "Four months after a duty, ranked the declines by how likely they are to last."),
       ("Test", "Checked the ranking on 44 past months against biggest drop first.")]
bw, gap, by, bh = 2.55, 0.543, 2.15, 3.45
for n, (name, body) in enumerate(BOX):
    bx = X0 + n * (bw + gap)
    box = s.shapes.add_shape(1, Inches(bx), Inches(by), Inches(bw), Inches(bh))
    box.fill.solid()
    box.fill.fore_color.rgb = RGBColor(0xF3, 0xF4, 0xF6)
    box.line.fill.background()
    box.shadow.inherit = False
    txt(s, str(n + 1), bx + 0.22, by + 0.15, 1.0, 0.6, 30, bold=True, color=RED)
    txt(s, name, bx + 0.22, by + 0.80, bw - 0.4, 0.5, 22, bold=True)
    txt(s, body, bx + 0.22, by + 1.35, bw - 0.4, 1.6, 15, color=GREY, spacing=1.12)
    if n < 3:
        txt(s, "\u2192", bx + bw, by + bh / 2 - 0.35, gap, 0.6, 26, color=GREY, align=PP_ALIGN.CENTER)
r = s.shapes.add_connector(1, Inches(X0), Inches(Y_TAKE - 0.14), Inches(X0 + CW), Inches(Y_TAKE - 0.14))
r.line.color.rgb = GREY
r.line.width = Pt(0.75)
txt(s, "**Done:** all four steps.   **Still running:** a forecast we froze on November 15, scored as new "
       "data comes out.", X0, Y_TAKE, CW, 0.75, 17, color=GREY, spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "RAHUL: Here's what we did, in four steps. The marker at the top of each slide shows which step "
    "we're on.\n\n"
    "One, collect. We read every duty notice since 2015, found 502 cases, and matched them to "
    "monthly import data.\n\n"
    "Two, measure. For each case, we compared the named country with other countries selling the "
    "same product.\n\n"
    "Three, predict. Four months after a duty, we rank the declines by how likely they are to "
    "last.\n\n"
    "Four, test. We checked that ranking on 44 past months.\n\n"
    "All four are done. One test is still running: a forecast we froze on November 15. We'll score "
    "it as new data comes out.")

# ---------------------------------------------------------------- M4 the design
add("We follow one product from one country.",
    bullets=[
        "**Antidumping and countervailing duties** tax one product from one country, for example "
        "mattresses from Vietnam.",
        "**Other countries keep selling it.** So we compare Vietnam's share of U.S. mattress "
        "imports with theirs, month by month.",
        "**502 cases since 2015,** matched to monthly U.S. import data.",
    ],
    bullet_size=24, bullet_top=2.25, bullet_step=1.05,
    caption="Antidumping: a duty on goods sold below fair value. Countervailing: a duty on goods "
            "helped by government subsidies.",
    take_rule=True, step=1,
    notes="RAHUL: Most tariffs in the news tax almost every country at once. That leaves nobody "
          "untaxed to compare with.\n\n"
          "There's a narrower kind of duty, called antidumping and countervailing duties. Each one "
          "names one product from one country. For example, mattresses from Vietnam.\n\n"
          "Other countries keep selling mattresses here. So we follow Vietnam's share, month by "
          "month, next to theirs. Anything that hits all mattresses, like inflation, hits them all "
          "and cancels out.\n\n"
          "We read every duty notice since 2015 and matched them to import data: 502 cases. As a "
          "check, we also run everything on a fake date, two years before each case.\n\n"
          "If asked: antidumping duties answer goods sold below fair value. Countervailing duties "
          "answer government subsidies.")

# ---------------------------------------------------------------- M5 the aftermath
add("Where duties stayed: 31% below rivals.", fig="t4_aftermath.png", step=2,
    caption="Red: the 326 cases where the duty became permanent. Grey: the same cases on a fake date, "
            "two years earlier.",
    notes="RAHUL: Here's what happens after the duty. Zero is where the country stood against its "
          "rivals before the case.\n\n"
          "The red line is the 326 cases where the trade commission kept the duty, so it became "
          "permanent. On average, the country fell about 31 percent against its rivals over the "
          "next 18 months. It was still falling at the end: about 37 percent down in months 13 to "
          "18.\n\n"
          "The grey line is the fake date. Same cases, same method, two years earlier. It shows no "
          "drop. If anything, it drifts up about 6 percent. So the drop isn't something our method "
          "creates.\n\n"
          "That still doesn't prove the duty alone caused it. Other things could matter, like "
          "which companies get named in a case.\n\n"
          "Two more things. There's no clear rush of buying before the duty. And where the duty "
          "was lifted, there's no lasting fall (backup).\n\n"
          "If asked for the exact numbers: minus 0.37 log points, standard error 0.065. The fake "
          "date is plus 0.06, standard error 0.03, on the 283 cases with enough earlier data.\n\n"
          "If asked whether the country fell or its rivals grew: we measure its share against its "
          "rivals, not its imports alone. Two things we can add. The chance the product is traded "
          "at all falls 9 points. And quantity falls about as much as dollars. Where the trade went "
          "instead, we have not measured.\n\n"
          "If asked about goods rerouted through another country: Census records the declared "
          "country of origin. Relabelled goods would count as the other country's. We can't "
          "separate that. It's a limit.")

# ---------------------------------------------------------------- M6 outcomes and the meaning of recovery
add("More than half did not come back.", fig="t5_outcomes.png", step=2,
    caption="Fell: share dropped at least a fifth within 6 months. Came back: back to its old level "
            "for 3 months in a row by month 18. 380 cases.",
    notes="RAHUL: Now case by case. First, what we mean by recovery.\n\n"
          "A country fell if its share dropped at least a fifth below its level before the case. It "
          "came back if its share returned to that level and stayed there three months in a row, "
          "within 18 months.\n\n"
          "Across 380 cases, 26 percent never fell. 17 percent fell and came back. 57 percent fell "
          "and did not come back. That includes 16 percent where the country had stopped selling "
          "the product completely a year later.\n\n"
          "On the fake date, only 21 percent fell without coming back.\n\n"
          "So for these duties, the answer is closer to real than borrowed. But that's an average. "
          "An analyst needs to know which declines will last.")

# ---------------------------------------------------------------- M7 the analyst's decision
add("Which declines should an analyst check first?",
    bullets=[
        "**Four months after the duty,** Census has published about two months of new trade data. "
        "Some countries have clearly fallen.",
        "**The analyst can only check some of them.** So each month's list needs an order.",
        "**The obvious rule: biggest drop first.** Anyone can do that with public data. Our model "
        "has to beat it.",
    ],
    bullet_size=24, bullet_top=2.20, bullet_step=1.10, step=3,
    notes="RAHUL: Back to our analyst. They can't look into every decline. So the question is: "
          "which ones first?\n\n"
          "Four months after a duty, Census has usually published two months of data since it "
          "started. By then, some declines are visible. Each month's list holds every product from "
          "a country that has fallen and not yet recovered.\n\n"
          "The simplest rule is to check the biggest drops first. It needs no model, and anyone can "
          "do it with public data. That's the bar our model has to clear.\n\n"
          "If asked what checking means: looking into that decline with the company's own supplier "
          "information. What the analyst does next, we did not test.\n\n"
          "If asked why month 4: it's a checkpoint we studied, not a business deadline. On the day "
          "a duty starts, facts like the duty rate don't predict recovery any better than past "
          "averages. So we wait for some trade data.\n\n"
          "HANDOFF: Raunak will show how our model orders that list, and whether it beats the "
          "biggest drops.")

# ---------------------------------------------------------------- M7b how the model ranks the list
s = prs.slides.add_slide(BLANK)
chrome(s, step=3)
txt(s, "How the model ranks each month's list.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
for y, b_ in [(2.05, "**What it sees:** 23 inputs, all public on the decision date: the latest share, "
                     "how the fall has gone, the case itself and the market before."),
              (3.40, "**The model:** gradient boosting, many small decision trees that each fix the "
                     "mistakes of the ones before. It gives each decline a chance of not recovering "
                     "by month 18."),
              (4.90, "**How we tested it:** each prediction only used older cases whose outcomes "
                     "were already known.")]:
    txt(s, b_, X0 + 0.15, y, 6.05, 1.3, 18, color=GREY, spacing=1.12)
# permutation importance on the held-out years (forecast/model_explain.py, report Appendix K),
# indexed so the latest share is 100
imp = pd.read_csv("results/model_importance.csv").set_index("feature").brier_increase
TOP = [("latest", "latest share"), ("rush", "share just before the duty"),
       ("log_pre_value", "imports before the case"), ("hhi", "market concentration"),
       ("log_rate", "duty rate"), ("slope", "recent direction")]
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
txt(s, "We also tried three other models. They gave the same result (backup).", X0, Y_TAKE, CW, 0.75, 17, color=GREY, spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "RAUNAK: Thanks, Rahul. Here's how the model orders the list.\n\n"
    "For each decline, the model looks at 23 inputs that were public on the decision date. The "
    "latest share Census has published. How the fall has gone so far. Facts about the case, like "
    "the duty rate. And what the market looked like before.\n\n"
    "The model is gradient boosting. It's many small decision trees, each fixing the mistakes of "
    "the ones before. It gives each decline a chance of not recovering by month 18. The list is "
    "sorted by that chance.\n\n"
    "We tested it the way an analyst would have used it. Each prediction only used older cases "
    "whose outcomes were already known.\n\n"
    "The chart shows what the model relies on. We scramble one input and see how much worse the "
    "forecast gets. The latest share matters most, about five times more than the next one.\n\n"
    "If asked how it was tuned: the settings were tuned on the older cases only, keeping each "
    "investigation together.\n\n"
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
HEAD = ["Model's\nrank", "Product", "Country", "Share now, % of\nits pre-duty share",
        "Model's chance it\nstays down", "Rank by\nbiggest drop"]
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
txt(s, "Share now: the last three months Census has published, compared with before the duty. The "
       "model's chances run a bit high; the order is what counts.", X0, Y_TAKE, CW, 0.75, 17, color=GREY,
    spacing=1.12)
s.notes_slide.notes_text_frame.text = (
    "RAUNAK: So what does the model actually give the analyst? This is its real output for January "
    "2025.\n\n"
    "That month, 36 declines were on the list. The model sorted them, and the analyst checks the "
    "top seven.\n\n"
    "Each row is one product from one country. You see how far its share has fallen, and the "
    "model's chance it stays down. The last column is where the biggest-drop rule would put it.\n\n"
    "Five of the model's top seven are 20th or lower on that rule. So the model isn't just picking "
    "the deepest falls.\n\n"
    "Row two is epoxy resins from Taiwan. Let's follow it.\n\n"
    "If asked about the chances: they run about 6 points high on average (report Appendix K). So "
    "the analyst uses the order, not the exact number.\n\n"
    "If asked why Brazil's ferrosilicon appears twice: it is listed under two product codes.\n\n"
    "If asked why the 0% rows aren't all at the top: ten declines had no imports at all, so they "
    "tie for first on biggest drop. But below about 60 percent of the old share, the model treats "
    "them all about the same. Other inputs decide the order (backup).")

# ---------------------------------------------------------------- M9 Taiwan: what happened later
add("Later: Taiwan had not recovered.", fig="t6_taiwan_later.png", step=4,
    caption="Epoxy resins from Taiwan. Red: what the analyst could see in January 2025. Grey: what "
            "happened next.",
    notes="RAUNAK: This is row two, epoxy resins from Taiwan. The duty started in September "
          "2024.\n\n"
          "The red line is what the analyst could see in January. Taiwan's share had dropped to 42 "
          "percent of where it was before the duty. The biggest-drop rule ranked it 20th, so it "
          "wouldn't get checked. The model ranked it 2nd.\n\n"
          "The grey line is what happened next. By month 18, March 2026, Taiwan was at 26 percent. "
          "It never recovered. And of the model's top seven that month, six never recovered.\n\n"
          "But one month doesn't prove the model is better. For that, we need every month.\n\n"
          "If asked what 42 percent means: Taiwan went from 10.3 percent of these imports to 4.4 "
          "percent. That's 42 percent of its old share, not 42 percent of all U.S. imports.")

# ---------------------------------------------------------------- M10 the result
add("The model's picks: 82% did not recover.", fig="t7_review_result.png", step=4,
    caption="44 past months, 2020 to 2025. Each month the analyst checks the top fifth of the list. "
            "We count how many had not recovered by month 18.",
    notes="RAUNAK: Now every month, not just one. We ran this on 44 monthly lists, from 2020 to "
          "2025. Each prediction only used older cases whose outcomes were already known.\n\n"
          "Each month, the analyst checks the top fifth of the list. That's about 187 checks in "
          "total. Then we wait until month 18 and ask: did each checked decline recover?\n\n"
          "With the model's order, 82 percent of the checks found declines that never recovered. "
          "With biggest drop first, 70 percent. With a random order, 62 percent, which is just the "
          "overall rate.\n\n"
          "So with the same 187 checks, the model finds about 22 more lasting declines. The gap is "
          "12 points. Our 90 percent range for it runs from 3.9 to 15.7, so it is clearly above "
          "zero.\n\n"
          "If asked whether it holds up: yes, if the analyst checks 10 or 30 percent instead. Yes at "
          "months 6 and 8: 88 against 76, and 89 against 81. Yes without the biggest case. And "
          "three other models score 81 to 84 percent (backup).")

# ---------------------------------------------------------------- M11 what it means
add("What this means.",
    bullets=[
        "**Mostly real, not borrowed:** after these duties, most declines were still there at "
        "month 18.",
        "**At month 4, use the model's list:** it found more lasting declines than biggest drop "
        "first.",
        "**Not yet tested with real analysts:** checking 1 in 5 is our assumption.",
    ],
    bullet_size=24, bullet_top=2.25, bullet_step=1.05,
    caption="Next: on November 15 we froze a forecast of 197 declines. We'll score it as new data "
            "comes out, from December 2026 to early 2028.",
    take_rule=True,
    notes="RAUNAK: Three things to take away.\n\n"
          "First, after these duties, the drop is mostly real. More than half of the named "
          "countries fell and still hadn't come back 18 months later.\n\n"
          "Second, at month 4, the model's list finds more lasting declines than just checking the "
          "biggest drops.\n\n"
          "Third, the limits. We haven't tested this with real analysts. How many they can check "
          "is our assumption. And we predict a country's recovery in a product, not whether one "
          "company survives.\n\n"
          "What's next. On November 15 we froze a forecast of 197 declines whose outcomes aren't "
          "known yet. For one month's list, 13 declines, the outcome was already public. So the "
          "other 184 are the real test. We'll score them as Census publishes the data, starting in "
          "December and finishing in early 2028. Thank you.")

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
    ("Relationship", "one product from one country: what the list ranks."),
    ("Check", "the analyst looks into a relationship with the company's own supplier information. "
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
    "Backup for slide 10, if asked why the ten relationships with no imports aren't all at the top. "
    "The model's chance of coming back is roughly flat, about 18 to 29 percent, anywhere below "
    "about 60 percent of the pre-duty share, then climbs steeply. So among the deep falls, how "
    "deep matters little, and inputs like the share just before the duty and the size of the market "
    "set the order. This is from one model fit on all cases, for explanation; the test results use "
    "the held-out predictions.")

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
    "didn't test either.\n\n"
    "Backup for slides 10 and 11: the January view on its own, if asked what the analyst could see.")

# ---------------------------------------------------------------- 13 the review queue
add("Review these first: 82% stayed down.", fig="20_review_queue.png",
    caption="44 monthly lists, 2020 to 2025, about 187 review slots at 20%: forecast 12.0 points above the "
            "latest share (3.9 to 15.7), about 22 more lasting declines. Next: scoring a forecast frozen in November.",
    take_rule=True,
    notes="Backup for slide 12. An analyst at an importer can review only some "
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
