"""Build presentation 2 as an editable .pptx.

Presentation 1 was scoped to the data and what it could support, and said so on slide 4:
"Results come next." This is that deck. It carries the three results from Report 1 and is
built to answer the four things Kylie Bemis flagged on Presentation 1:

  1. "Analytic problem is given but lacks clarity."
     -> slide 3 states input, output and what counts as success, nothing else.
  2. "Fig 4 is nice, but consider adding additional slide explaining the transformation
     and some of the choices. Same for Fig 5."
     -> slide 6 explains the transformation before slide 7 shows the figure.
  3. "Maybe a simple sentence '1% coverage means ...'"
     -> that sentence is on slide 4, close to literally.
  4. "Need better and in-depth reasoning/justification for methods is needed."
     -> slide 8 is what we retired and why, which is the justification made visible.

Every number here is from REPORT1.md, which is the version that went through ten review
passes, so the corrections hold: the sample is antidumping AND countervailing, the 26 percent
is a fall in relative position rather than a level comparison, and question one is unanswered.

Style is lifted from build_deck.py unchanged so the two decks are visibly one series.

Usage:  python3 slides/build_deck2.py      # from the repo root
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
        per_line = int(1700 / bullet_size)
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


# ---------------------------------------------------------------- 1 title
s = prs.slides.add_slide(BLANK)
chrome(s, names=False)
txt(s, "Borrowed or Real", X0, 2.05, CW, 1.05, 48, bold=True)
txt(s, "Measuring import surges around U.S. tariffs", X0, 3.12, CW, 0.7, 25, color=RED)
txt(s, "Rahul Reddy Mandadi   +   Raunaksingh Khalsa", X0, 4.18, CW, 0.5, 18, bold=True)
txt(s, "DS 5500 Data Science Capstone   |   Presentation 2   |   November 2026",
    X0, 4.66, CW, 0.5, 13, color=GREY)
txt(s, "Presentation 1 covered the data and what it could support. This one has the results.",
    X0, 5.52, CW, 0.9, 13, color=GREY)
txt(s, "github.com/rahul-mandadi/tariff-rush", X0, Y_TAKE, CW, 0.4, 13, bold=True, color=RED)
s.notes_slide.notes_text_frame.text = (
    "Note the subtitle change: 'Forecasting' became 'Measuring'. That is deliberate and it is\n"
    "the honest description of what the project can do. Slide 9 says why.\n\n"
    "SPEAKER SPLIT: suggest Rahul 1-4, Raunak 5-9. Both must speak for the rubric.\n"
    "Target is under 10 minutes.")

# ---------------------------------------------------------------- 2 recap
add("Three results, and one retirement.",
    bullets=[
        "**Presentation 1 said the category is the wrong unit.**",
        "We had not proved it. We built the eight-digit panel, 15.9 million rows, and measured "
        "the dilution directly.",
        "**Three results now survive a placebo test.**",
        "One question still does not. The rush rests on 21 usable events, so we do not report "
        "it as answered.",
        "**We retired the forecasting goal, on evidence. Slide 9.**",
    ],
    bullet_size=21, bullet_top=2.20, bullet_step=0.56,
    caption="Report 1 is submitted. Everything on the next five slides is in it, with the "
            "script that produces each number.",
    take_rule=True,
    notes="Thirty seconds. Do not linger. The point is only: last time we had data, this time "
          "we have results, and we also cut something.")

# ---------------------------------------------------------------- 3 the problem, precisely
# Bemis: "Analytic problem is given but lacks clarity." This slide exists to fix that.
add("The problem, precisely.",
    bullets=[
        "**Input**   one eight-digit product from one country, monthly customs value,\n"
        "eighteen months either side of a trade action.",
        "**Output**   that country's monthly position against every other country\n"
        "supplying the same product, as a percentage.",
        "**Success**   the path has to separate from the same calculation run on the\n"
        "same events shifted back twenty-four months, where nothing happened.",
    ],
    bullet_size=21, bullet_top=2.15, bullet_step=1.30,
    caption="One product from one country in one month is a cell. The panel holds 15.9 million "
            "of them across 140 months.",
    take_rule=True,
    notes="This is the slide Bemis asked for. Read the three lines almost as written. Do not "
          "add the three research questions here, they are on the next slides where the results "
          "are. Input, output, how we know it worked.")

# ---------------------------------------------------------------- 4 result 1, coverage
add("A tariff names 5% of its category.", fig="09_sankey.png",
    caption="Copper, 2025. The 50% duty named semi-finished products and derivatives, 29% of "
            "chapter 74. Refined copper and cathodes, 67% on their own, were treated as inputs "
            "and left untaxed. Median across all 1,350 action-and-category pairs is 5.4%, and "
            "32.4% of pairs name under 1%.",
    notes="The number to say out loud: 1% coverage means the action touches one dollar in every "
          "hundred of that category. So a category-level average is 99 percent untreated trade, "
          "and any real effect is averaged away. That is why we work at eight digits.\n\n"
          "Copper is the example because the answer is counter-intuitive: the headline said "
          "'50% tariff on copper' and two thirds of copper was never tariffed.")

# ---------------------------------------------------------------- 5 result 2, units
add("Dollars and quantity disagree.", fig="08_units.png",
    caption="Chapter-level anomaly scores on value against quantity, for the 63 categories "
            "rankable on both. Cocoa is a false positive in dollars: prices roughly tripled "
            "after poor West African harvests. Pharmaceuticals is a false negative in quantity: "
            "tonnage tracked trend while value rose 57% above it.",
    notes="The point is that neither measure is safe at category level, for the same reason as "
          "the last slide. A chapter mixes products with different treatment and different units "
          "of measure. 56 of 98 chapters report kilograms for under seventy percent of their "
          "value, with apparel in dozens and footwear in pairs.")

# ---------------------------------------------------------------- 6 the transformation
# Bemis: "consider adding additional slide explaining the transformation and some of the choices"
add("How the next figure is built.",
    bullets=[
        "**Compare within a product, across countries, in the same month.**",
        "A price shock or a demand swing hits every supplier at once and cancels out. "
        "A duty moves one supplier against the rest.",
        "**Hold the product's own monthly swings and each country's usual level fixed.**",
        "So a point is a position against rival suppliers, not a dollar amount.",
        "**Then run the identical calculation 24 months earlier and plot both.**",
        "If the two paths look the same, we have measured nothing.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.60,
    caption="The controls are not clean: a supplier absorbing displaced volume is itself in the "
            "control group. So this measures relative standing, not one country's loss in isolation.",
    take_rule=True,
    notes="Bemis asked for this slide by name after Presentation 1. Take your time here, it is "
          "the methods justification and it is worth more than another result.\n\n"
          "If asked why not a simple before-and-after: because 2020 to 2025 moved every trade "
          "series at once, and a before-and-after cannot tell that apart from the duty.")

# ---------------------------------------------------------------- 7 result 3, the aftermath
add("The named country does not come back.", fig="10_event.png",
    caption="673 events. The named country runs 42% above its own pre-case baseline before "
            "collection and 6% above it after, a fall of about 26% that has not reversed "
            "eighteen months later. The placebo rises over the same event time. Post-period "
            "difference separates at p < 0.0001.",
    notes="Say clearly that this is antidumping AND countervailing duties: 338 and 169 of the "
          "508 episodes. Not tariffs. These are the cases where we have enough events.\n\n"
          "The 26 percent is a fall in RELATIVE POSITION, from 42 above baseline to 6 above. It "
          "is not a claim that the country sells 26 percent less than its rivals. Be precise, "
          "this is the sentence most likely to be challenged.\n\n"
          "Also note what is NOT here: there is no rush before the duty starts. Front-loading "
          "predicts one and we do not detect one.")

# ---------------------------------------------------------------- 8 what we retired
# Bemis: "Need better and in-depth reasoning/justification for methods is needed."
add("What we retired, and why.",
    bullets=[
        "**The 79/21 absorption split.** Confounded with market share. A supplier holding a "
        "fifth of a product can stop entirely and the arithmetic still says four fifths absorbed.",
        "**Category-level treatment flags.** The dilution on slide 4 drives any estimate toward "
        "zero. Detectable at p = 0.0075 and economically negligible.",
        "**Forecasting, as a goal.** Three prediction attempts, all negative out-of-sample "
        "R-squared, including against the training mean. Year alone explains 0.366 of the "
        "variance; eleven structural features explain 0.142 in sample.",
    ],
    bullet_size=19, bullet_top=2.15, bullet_step=1.15,
    caption="Every estimate we report is paired with a placebo. Three candidate estimators did "
            "not survive it, including one of our own earlier conclusions.",
    take_rule=True,
    notes="This is the most important slide for the Methods and Results score. The message is "
          "that the discipline has teeth: it killed our own findings, including one we had "
          "already presented.\n\n"
          "The last bullet is the big one. Period effects dominate the level of trade, which is "
          "exactly why the within-product design works: it differences them out.")

# ---------------------------------------------------------------- 9 where we are
add("Identifiable, but not forecastable.",
    bullets=[
        "**What we can say.** What a duty does to a targeted origin, with a placebo behind it, "
        "and that the category is the wrong unit to say it at.",
        "**What we cannot.** How much volume a given product keeps. That depends mostly on what "
        "the following year looks like for trade as a whole.",
        "**Next.** Fit the duration model on 508 antidumping and countervailing episodes with "
        "right-censoring, after balancing the cohort across the event window.",
        "**Open.** Only month zero survives a Bonferroni correction across 31 coefficients.",
    ],
    bullet_size=19, bullet_top=2.15, bullet_step=0.95,
    caption="Deliverable by December: outcome distributions and time-to-recovery for an "
            "antidumping case on your product from your supplier, rather than a forecast "
            "nobody should trust.",
    take_rule=True,
    notes="Close on the honest framing. 'Identifiable but not forecastable' is the line to "
          "leave them with, and it is a result rather than an apology: three failed prediction "
          "models are why we trust the measurement.\n\n"
          "If asked 'so did you answer your question?': question two is partly answered, the "
          "fall is established but we cannot separate volume lost from volume relocated. "
          "Question one is not answered. Question three is next.")

out = "slides/Mandadi_Khalsa_Presentation2.pptx"
prs.save(out)
print(f"wrote {out}  ({len(prs.slides._sldIdLst)} slides, {os.path.getsize(out)/1000:.0f} KB)")
