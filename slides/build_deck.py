"""Build presentation 1 as an editable .pptx.

Follows the course report structure as its spine (problem, data, methods, results, discussion)
and the house style from the team pitch deck: one declarative sentence per slide, the figure
does the work, both names in the footer. Speaker notes carry what to say, including the
suggested split so both of us talk.

Keeping it as .pptx rather than generating a PDF directly means the deck stays editable and
Raunak can change his own slides. Export to PDF from PowerPoint or Keynote for the Canvas
submission.

Usage:  python3 slides/build_deck.py      # from the repo root
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from PIL import Image
import os

# geometry, palette and type lifted from Mandadi_Khalsa_Team_Pitch.pptx so this deck
# is visibly the same series: names top right with a rule under them, 38pt bold headline
# at the same coordinates, and a 17pt grey takeaway line along the bottom.
INK = RGBColor(0x14, 0x16, 0x1A)
GREY = RGBColor(0x6E, 0x73, 0x7C)
RED = RGBColor(0xC8, 0x10, 0x2E)
PANEL = RGBColor(0xEE, 0xEF, 0xF2)
ACC, WARN = RED, RED
W, H = 13.333, 7.5
FOOT = "RAHUL REDDY MANDADI   +   RAUNAKSINGH KHALSA"
FIG = "slides/fig"
FONT = "Avenir Next"
# template coordinates
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
        p.text = line
        p.alignment = align
        p.line_spacing = spacing
        for r in p.runs:
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = italic
            r.font.color.rgb = color
            r.font.name = font
    return tb


def chrome(s):
    """Names top right, hairline rule under them. Same on every slide."""
    txt(s, FOOT, 6.00, Y_FOOT, 6.58, 0.30, 9, color=GREY, align=PP_ALIGN.RIGHT)
    ln = s.shapes.add_connector(1, Inches(X0), Inches(Y_RULE),
                                Inches(X0 + CW), Inches(Y_RULE))
    ln.line.color.rgb = GREY
    ln.line.width = Pt(0.75)


def add(headline, fig=None, caption=None, notes="", bullets=None, bullet_size=22):
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
        txt(s, caption, X0, Y_TAKE, CW, 0.75, 17, color=GREY, spacing=1.12)
    if bullets:
        y = 2.10
        for b in bullets:
            bold = b.startswith("**")
            body = b.strip("*")
            txt(s, body, X0 + 0.15, y, CW - 0.5, 0.8, bullet_size,
                bold=bold, color=INK if bold else GREY, spacing=1.15)
            y += 0.50 + 0.32 * body.count("\n")
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


# ---------------------------------------------------------------- 1 title
s = prs.slides.add_slide(BLANK)
chrome(s)
txt(s, "Borrowed or Real", X0, 2.05, CW, 1.05, 48, bold=True)
txt(s, "Forecasting import surges around U.S. tariffs", X0, 3.12, CW, 0.7, 25, color=RED)
txt(s, "Rahul Reddy Mandadi   +   Raunaksingh Khalsa", X0, 4.18, CW, 0.5, 18, bold=True)
txt(s, "DS 5500 Data Science Capstone   |   Presentation 1   |   October 2026",
    X0, 4.66, CW, 0.5, 13, color=GREY)
txt(s, "Stakeholders: importers re-sourcing suppliers, lenders with exposure to a single\n"
       "origin, carriers serving an affected trade lane",
    X0, 5.52, CW, 0.9, 13, color=GREY)
txt(s, "github.com/rahul-mandadi/tariff-rush", X0, Y_TAKE, CW, 0.4, 13, bold=True, color=RED)
s.notes_slide.notes_text_frame.text = (
    "SPEAKER SPLIT: slides 1-4 one of us, 5-8 the other. Both must speak.\n"
    "Eight slides for 10-15 minutes. Slides 2, 3 and 8 need the most time; 4 and 5 the least.\n"
    "Slides 9 and 10 are backup for questions, not part of the talk.\n\n"
    "Do not read the stakeholder line aloud. It is there for the rubric and the PDF.")

# ---------------------------------------------------------------- 2 context
add("Every tariff comes with a date.",
    fig="01_context.png",
    caption="A duty is announced, then starts later. That gap is a window to import before it applies.",
    notes="LAYMAN CONTEXT. Assume nobody knows what a tariff is.\n\n"
          "A tariff is a tax on imports. The government announces it, and it starts on a named "
          "date weeks or months later.\n\n"
          "That gap creates an obvious incentive: get your goods in before the tax starts. "
          "Importers rush, and you can see it in the copper line climbing before the date.\n\n"
          "Afterwards imports usually fall below normal, because buyers already stocked up.\n\n"
          "This behaviour is called front-loading. That is the whole subject of the project.")

# ---------------------------------------------------------------- 3 problem
add("The decision comes before the data.",
    fig="02_timeline.png",
    caption="Census publishes monthly trade about five weeks after the month closes.",
    notes="THE DOMAIN PROBLEM. This slide says why anyone should care.\n\n"
          "Somebody has to act on announcement day. An importer with a supplier in the tariffed "
          "country has to decide whether to wait it out or qualify a new supplier somewhere "
          "else, and requalifying runs months and costs real money. A lender behind either side "
          "holds the same question as credit risk. A carrier running that origin's service has "
          "to decide whether to keep it.\n\n"
          "And you cannot just wait and watch, because the data is late. By the time two bad "
          "months show up, the duty has been in force for a quarter.\n\n"
          "So the decision is made before the answer is knowable. That is the gap we are "
          "trying to close.")

# ---------------------------------------------------------------- 4 questions
add("So we ask three questions.",
    bullets=["**1.  Will there be a rush, and how big?**",
             "Before the duty starts, do imports jump, and by how much?",
             "**2.  What happens after the duty starts?**",
             "Is the drop volume borrowed from later months, a real fall in demand,\nor trade moving to another country?",
             "**3.  How long does it last?**",
             "Months, or permanently?"],
    bullet_size=20,
    caption="This presentation is about the data and what it can support. Results come next.",
    notes="THE ANALYTIC PROBLEM. Short, it is a signpost.\n\n"
          "Question 1 is the rush. Question 2 is what the drop afterwards actually means, which "
          "is the hard one. Question 3 is duration.\n\n"
          "Say plainly that this presentation is the data and its limits, not answers yet.")

# ---------------------------------------------------------------- 5 what we have
s5 = prs.slides.add_slide(BLANK)
chrome(s5)
txt(s5, "What we have.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
from PIL import Image as _I
_p = f"{FIG}/03_panel.png"
_iw, _ih = _I.open(_p).size
_w = 6.55
s5.shapes.add_picture(_p, Inches(X0), Inches(2.25), width=Inches(_w),
                      height=Inches(_w * _ih / _iw))
rows5 = [("74", "CHILE", "719,291,110", "74,332,392"),
         ("74", "CANADA", "288,797,724", "29,299,850"),
         ("74", "GERMANY", "177,404,661", "15,671,176"),
         ("74", "MEXICO", "98,936,124", "10,906,662"),
         ("74", "PERU", "91,039,306", "9,003,463")]
hdr5 = ("product", "country", "value, $", "kg")
wid5 = [max(len(hdr5[i]), max(len(r[i]) for r in rows5)) for i in range(4)]
f5 = lambda r: "  ".join((str(v).ljust(wid5[i]) if i < 2 else str(v).rjust(wid5[i]))
                         for i, v in enumerate(r))
tbl5 = "\n".join([f5(hdr5), "-" * (sum(wid5) + 6)] + [f5(r) for r in rows5])
txt(s5, "One row is one product, one country, one month.", 7.70, 2.22, 4.88, 0.4, 14,
    bold=True)
txt(s5, "Copper, March 2025, biggest suppliers", 7.70, 2.60, 4.88, 0.4, 12, color=GREY)
txt(s5, tbl5, 7.70, 3.00, 4.88, 1.9, 10, font="Courier New", spacing=1.35)
txt(s5, "140 months, Jan 2015 to Aug 2026\n15.9 million product-country-month records\n"
        "Pulled at 10 digits, the level tariff orders are written at",
    7.70, 4.72, 4.88, 1.2, 12, color=GREY, spacing=1.25)
txt(s5, "2017 adds up to 2,340 billion dollars against a published 2.34 trillion, and all 140 "
        "months\nreconcile against a separate total the API returns on its own.",
    X0, Y_TAKE, CW, 0.9, 17, color=GREY, spacing=1.12)
s5.notes_slide.notes_text_frame.text = (
    "THE DATA. Two things on this slide, go left then right.\n\n"
    "Left: monthly US imports from the Census Bureau, free and public, 140 months.\n\n"
    "Right: what a row actually is. One product, one country, one month. Value is always "
    "reported. Weight in kilograms is reported for about 91% of rows and is the better measure, "
    "because it does not move when prices move, and it counts goods arriving by truck and rail "
    "which the shipping-weight columns miss entirely.\n\n"
    "The important choice: we pull at 10 digits. Tariff orders are written at 8, and 10 nests "
    "inside 8, so we can match a tariff to exactly the products it names instead of guessing. "
    "Say this slowly, it matters for slide 8.\n\n"
    "Why trust it: read the takeaway line.\n\n"
    "Then mention the tariff side in one sentence: we also searched the Federal Register, "
    "2,792 documents, and classified 134 of them as real tariff actions, in two waves, 2018-19 "
    "and a bigger one in 2025. Backup slide 9 has the chart if anyone asks.")

# ---------------------------------------------------------------- 6 caveat
add("Unusual is not the same as tariffed.",
    fig="05_chapters.png",
    caption="Each chapter measured against its own normal range, built only from data before 2025.",
    notes="METHOD AND ITS LIMIT. This is the slide that shows judgement, do not skip it.\n\n"
          "First explain the x-axis in one sentence: for each product we built what it would "
          "have done anyway from earlier years, drew a band for ordinary month-to-month wobble, "
          "and this is how far outside that band 2025 went. Backup slide 10 shows the band on "
          "copper if anyone wants to see it.\n\n"
          "Some of these are plausible tariff stories: organic chemicals and pharmaceuticals "
          "were under open tariff threat in 2025, and gold moved into US vaults ahead of "
          "expected duties.\n\n"
          "Some are not. Silk is a 60-million-dollar chapter, so almost any month looks extreme "
          "next to its own history. Works of art and clocks are small and lumpy.\n\n"
          "Cocoa is the one to dwell on. It sits high because cocoa prices roughly tripled after "
          "bad West African harvests. We measure in dollars, so a price spike reads as a volume "
          "surge.\n\n"
          "So the detector finds unusual months. It does not know why. Something has to connect "
          "an unusual month to an actual tariff, and that is the next slide.")

# ---------------------------------------------------------------- 7 finding
add("And this is where it nearly came apart.",
    fig="07_coverage.png",
    caption="The typical tariff action covers about 5% of its chapter's value. A third cover under 1%.",
    notes="THE KEY SLIDE. If time runs short, this is the one that must survive.\n\n"
          "A tariff order does not say 'chapter 74, copper'. It points at a list of 8-digit "
          "product codes, usually published in a separate legal notice. Until you read those "
          "lists, the only thing you can do is treat a whole chapter as tariffed whenever an "
          "action touches anything inside it.\n\n"
          "We read them: 9,083 distinct 8-digit codes across 162 actions.\n\n"
          "The typical action covers about 5% of its chapter's value. A third cover under 1%.\n\n"
          "So chapter-level treatment means roughly 95% of what you are measuring is trade the "
          "tariff never touched. Any real reaction in the 5% gets averaged away by the 95% that "
          "did nothing.\n\n"
          "That is exactly what happened to us. Our first attempt to measure an effect found "
          "nothing, and this is why. The null was our ruler, not the world.\n\n"
          "The fix is to work at the 8-digit level, where a tariff either names a product or it "
          "does not. Everything after this is built that way.")

# ---------------------------------------------------------------- 8 status
add("Where we are.",
    bullets=["**Built and checked**",
             "140 months of imports at the exact level tariffs are written, reconciled\nagainst published totals.",
             "**A detector, and its limits**",
             "We can find months that are unusual for a product, and we know it cannot\ntell a tariff from a price shock on its own.",
             "**134 tariff actions, with the products behind each one**",
             "Corrected announcement and effective dates, and the 8-digit product lists.",
             "**Next**",
             "Measure the rush and what follows it, at product level, using untreated\ncountries as the comparison."],
    bullet_size=17,
    notes="DISCUSSION AND NEXT STEPS.\n\n"
          "Be straight that this is data and limits, not results. Results come next.\n\n"
          "The one thing to claim as a finding: we measured why the obvious approach fails, and "
          "the number is 5%.\n\n"
          "If asked 'so is there a rush?': we now have the data and the product-level matching "
          "to answer it, and the chapter-level version of the question was unanswerable for the "
          "reason on the previous slide.\n\n"
          "If asked 'who exactly is the customer?': the decision is where to source next and "
          "when, and it sits with whoever is exposed to a particular country rather than to "
          "total volume. Say we are still testing which of those the data best serves. True, "
          "and better than naming one confidently.")

# ------------------------------------------------- 9 and 10, backup for questions
add("Backup: the tariff actions we found.",
    fig="06_events.png",
    caption="2,792 Federal Register documents reviewed, 134 are real tariff actions. Median gap from announcement to start date is 8 days.",
    notes="BACKUP, not part of the talk. Use if asked where the tariff dates come from or how "
          "many actions there are.\n\n"
          "Two waves: 2018-19, and a much bigger one in 2025. The legal authority turns out to "
          "matter, which is why they are split out here.")

add("Backup: what a normal range looks like.",
    fig="04_normal.png",
    caption="Copper against its own expected range. The expected line uses only data from before the tariff.",
    notes="BACKUP, not part of the talk. Use if asked how the normal range on slide 6 is built.\n\n"
          "Copper peaks 89% above normal against a band of 50%, so it clears.\n\n"
          "Aluminium does NOT clear: it peaks at 26% against a band of 100%, because its own "
          "history is volatile. Same tariff year, and the test says no. A test that can say no "
          "is the only kind worth having.")

out = "slides/Mandadi_Khalsa_Presentation1.pptx"
prs.save(out)
import os
print(f"wrote {out}  ({len(prs.slides._sldIdLst)} slides, {os.path.getsize(out)/1000:.0f} KB)")
