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


def chrome(s, names=True):
    """Names top right, hairline rule under them. Same on every slide.

    The title slide carries both names at 18pt already, so it passes names=False
    rather than printing them twice.
    """
    if names:
        txt(s, FOOT, 6.00, Y_FOOT, 6.58, 0.30, 9, color=GREY, align=PP_ALIGN.RIGHT)
    ln = s.shapes.add_connector(1, Inches(X0), Inches(Y_RULE),
                                Inches(X0 + CW), Inches(Y_RULE))
    ln.line.color.rgb = GREY
    ln.line.width = Pt(0.75)


def add(headline, fig=None, caption=None, notes="", bullets=None, bullet_size=22,
        bullet_top=2.10, bullet_step=0.50, take_y=Y_TAKE, take_rule=False):
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
        # a text-only slide has no figure to separate the bullets from the takeaway, so it
        # gets the same hairline the header uses
        if take_rule:
            r = s.shapes.add_connector(1, Inches(X0), Inches(take_y - 0.14),
                                       Inches(X0 + CW), Inches(take_y - 0.14))
            r.line.color.rgb = GREY
            r.line.width = Pt(0.75)
        txt(s, caption, X0, take_y, CW, 0.75, 17, color=GREY, spacing=1.12)
    if bullets:
        y = bullet_top
        for b in bullets:
            bold = b.startswith("**")
            body = b.strip("*")
            txt(s, body, X0 + 0.15, y, CW - 0.5, 0.8, bullet_size,
                bold=bold, color=INK if bold else GREY, spacing=1.15)
            y += bullet_step + 0.32 * body.count("\n")
        # the last line must clear the takeaway band, or the two draw on top of each other
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
txt(s, "Forecasting import surges around U.S. tariffs", X0, 3.12, CW, 0.7, 25, color=RED)
txt(s, "Rahul Reddy Mandadi   +   Raunaksingh Khalsa", X0, 4.18, CW, 0.5, 18, bold=True)
txt(s, "DS 5500 Data Science Capstone   |   Presentation 1   |   October 2026",
    X0, 4.66, CW, 0.5, 13, color=GREY)
txt(s, "Stakeholders: importers looking for a new supplier, lenders exposed to a single\n"
       "origin, carriers serving an affected trade lane",
    X0, 5.52, CW, 0.9, 13, color=GREY)
txt(s, "github.com/rahul-mandadi/tariff-rush", X0, Y_TAKE, CW, 0.4, 13, bold=True, color=RED)
s.notes_slide.notes_text_frame.text = (
    "SPEAKER SPLIT: slides 1-4 one of us, 5-8 the other. Both must speak.\n"
    "Eight slides, UNDER 10 MINUTES. Slide 7 needs the most time; 1 and 4 the least.\n""slides/SCRIPT.md is written to 9:15 measured. Do not ad-lib past it.\n"
    "Slides 9, 10 and 11 are backup for questions, not part of the talk.\n\n"
    "Do not read the stakeholder line aloud. It is there for the rubric and the PDF.\n\n"
    "================ Q&A PREP ================\n"
    "The deck is scoped to data, limits and next steps on purpose. These are not on the "
    "slides, but we should be able to answer all six cold.\n\n"
    "1. DOMAIN PROBLEM. A tariff is announced with a future start date, importers rush ahead "
    "of it, and imports fall afterwards. Someone exposed to the targeted country has to decide "
    "on announcement day whether to wait it out or re-source, and the data that would settle "
    "it arrives about five weeks after each month closes. Slides 2 and 3.\n\n"
    "2. DATA SCIENCE PROBLEM. Three, in order: a classification problem (does a surge occur), "
    "a regression problem (how large), and a duration problem (how long does the aftermath "
    "last, with right-censoring for episodes still running at the end of the panel). Slide 4 "
    "states them in plain language; this is the technical framing.\n\n"
    "3. WHO AND WHAT. Whoever carries exposure to one origin rather than to total volume: an "
    "importer deciding whether to requalify a supplier, a lender holding that as credit risk, "
    "a carrier running that origin's service. We are explicit that we are still testing which "
    "of those the data serves best. An earlier version of this project named port and terminal "
    "operators; we tested that and dropped it, because displaced volume arrives from a "
    "different country through substantially the same US customs districts.\n\n"
    "4. DATA SOURCES. Two, both public and free. US Census international trade API for monthly "
    "imports, pulled at HS10 (slide 5). The Federal Register API for tariff actions, 2,792 "
    "documents classified down to 134 real actions (backup slide 9). The product lists behind "
    "each action come from the USITC Harmonized Tariff Schedule, chapter 99.\n\n"
    "5. METHODOLOGY. Pull at HS10 because tariff orders are written at HS8 and HS10 nests "
    "inside it, so matching is exact rather than approximate. Build a counterfactual per series "
    "from pre-event data only. Then compare a tariffed product from a tariffed country against "
    "the same product from countries that were not tariffed, in the same month. That last step "
    "is the important one: a commodity price shock moves every origin together and cancels, "
    "while a tariff moves one origin against the rest.\n\n"
    "6. EVALUATION AND METRICS. Every estimate is paired with a placebo: the same calculation "
    "with every event shifted back 24 months. If a result does not separate from its own "
    "placebo we do not report it as a result. That discipline has already retired three "
    "candidate methods. For the predictive questions, forward-chaining validation by year and "
    "grouped by case, so no case appears in both folds and the model is always tested on cases "
    "later than the ones it learned from, scored against a deliberately hard naive benchmark "
    "rather than against zero.")

# ---------------------------------------------------------------- 2 context
add("Every tariff comes with a date.",
    fig="01_context.png",
    caption="Fig. 1   Copper imports. Announced July 2025, in force from August.\n"
            "Imports had been climbing since February, because the duty was expected.\n"
            "Goods pulled forward are borrowed from later months, the question in our title [5].",
    notes="LAYMAN CONTEXT. Assume nobody knows what a tariff is.\n\n"
          "A tariff is a tax on imports. The government announces it, and it starts on a named "
          "date weeks or months later.\n\n"
          "That gap creates an obvious incentive: get your goods in before the tax starts.\n\n"
          "POINT AT THE CHART AND BE ACCURATE ABOUT IT. The rush does not wait for the "
          "announcement. Copper runs 1.25 billion in February and 3.22 in July, the month it "
          "was announced, because a Section 232 copper investigation was public long before the "
          "proclamation. The announcement-to-start gap here is three weeks; the build-up is "
          "five months. So the thing that starts the rush is the tariff becoming likely, not "
          "becoming official. That is part of why question 1 is worth asking.\n\n"
          "Then August falls to 1.74 and November to 1.06, because buyers already stocked up.\n\n"
          "DO NOT OVERSELL THE DIP. The line comes back up from December. Eighteen months of "
          "copper is one product and one event, and it is on this slide to explain the idea, "
          "not to prove anything. The measurement is slides 6 to 8.\n\n"
          "This behavior is called front-loading. That is the whole subject of the project.\n\n"
          "Define BORROWED here, out loud, because it is the title of the project: goods that "
          "would have been imported in October arrive in August instead. Nothing was created or "
          "destroyed, it just moved. If the whole dip afterwards is that, it is borrowed. If "
          "some of it never comes back, it is real. That is what we are trying to tell apart.")

# ---------------------------------------------------------------- 3 problem
add("The decision comes before the data.",
    fig="02_timeline.png",
    caption="Fig. 2   Importers, lenders and carriers all decide here.\nCensus publishes monthly trade about five weeks after the month closes.",
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
             "classification, then regression",
             "**2.  What happens after the duty starts?**",
             "borrowed back, lost for good, or bought from somewhere else",
             "**3.  How long does it last?**",
             "duration, counting episodes still running"],
    bullet_size=20,
    caption="This presentation is about the data and what it can support. Results come next.",
    notes="THE ANALYTIC PROBLEM. Short, it is a signpost.\n\n"
          "Question 1 is the rush. Question 2 is what the drop afterwards actually means, which "
          "is the hard one: borrowed means the goods arrive early and the dip is just payback, "
          "lost means that demand never comes back, and bought from somewhere else means the same "
          "goods arrive from a different country. Question 3 is how long it lasts.\n\n"
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
# real HS8 lines, not a chapter roll-up: the whole point of this slide is that we work
# at the level a tariff order names, so the table has to show that level
rows5 = [("74031100", "CHILE", "715,897,592", "73,977,447"),
         ("74031100", "CANADA", "118,144,886", "11,854,813"),
         ("74031100", "GERMANY", "93,060,459", "10,000,049"),
         ("74081160", "CANADA", "78,104,444", "7,467,535"),
         ("74031100", "PERU", "50,457,615", "5,317,013")]
hdr5 = ("product", "country", "value, $", "kg")
wid5 = [max(len(hdr5[i]), max(len(r[i]) for r in rows5)) for i in range(4)]
f5 = lambda r: "  ".join((str(v).ljust(wid5[i]) if i < 2 else str(v).rjust(wid5[i]))
                         for i, v in enumerate(r))
tbl5 = "\n".join([f5(hdr5), "-" * (sum(wid5) + 6)] + [f5(r) for r in rows5])
txt(s5, "Table 1   One product, one country, one month.", 7.70, 2.22, 4.88, 0.4, 14,
    bold=True)
txt(s5, "Copper, March 2025.  Two separate 8-digit lines.",
    7.70, 2.60, 4.88, 0.4, 12, color=GREY)
txt(s5, tbl5, 7.70, 3.00, 4.88, 1.9, 10, font="Courier New", spacing=1.35)
txt(s5, "140 months, Jan 2015 to Aug 2026\n15.9 million product-country-month records\n"
        "Pulled at 10 digits, which nest inside the 8 tariffs name",
    7.70, 4.72, 4.88, 1.2, 12, color=GREY, spacing=1.25)
txt(s5, "Census trade API  +  Federal Register API\n2,792 documents, 134 real tariff actions",
    7.70, 5.62, 4.88, 0.8, 12, bold=True, spacing=1.25)
txt(s5, "Fig. 3   Imports we cover, by year; the grey 2026 bar is eight months, not twelve.\n"
        "2017 adds up to 2,340 billion dollars against a published 2.34 trillion, and all 140\n"
        "months reconcile against a separate total the API returns on its own.",
    X0, Y_TAKE, CW, 1.0, 16, color=GREY, spacing=1.10)
s5.notes_slide.notes_text_frame.text = (
    "THE DATA. Two things on this slide, go left then right.\n\n"
    "Left: monthly US imports from the Census Bureau, free and public, 140 months.\n\n"
    "Right: what a row actually is. One 8-digit product, one country, one month. Chapter 74 "
    "is copper; inside it are 88 separate 8-digit lines in that month alone, and a tariff "
    "names lines, not chapters. Value is always "
    "reported. Weight in kilograms is reported for about 91% of rows and is the better measure, "
    "because it does not move when prices move, and it counts goods arriving by truck and rail "
    "which the shipping-weight columns miss entirely.\n\n"
    "The important choice: we pull at 10 digits. Tariff orders are written at 8, and 10 nests "
    "inside 8, so we can match a tariff to exactly the products it names instead of guessing. "
    "Say this slowly, it matters for slide 7.\n\n"
    "Why trust it: read the takeaway line.\n\n"
    "Then mention the tariff side in one sentence: we also searched the Federal Register, "
    "2,792 documents, and classified 134 of them as real tariff actions, in two waves, 2018-19 "
    "and a bigger one in 2025. Backup slide 9 has the chart if anyone asks.")

# ---------------------------------------------------------------- 6 caveat
add("Unusual is not the same as tariffed.",
    fig="05_chapters.png",
    caption="Fig. 4   We built a detector for unusual months. Each product chapter is measured\n"
            "against its own normal range, built only from data before 2025 [6].",
    notes="METHOD AND ITS LIMIT. This is the slide that shows judgement, do not skip it.\n\n"
          "First explain the x-axis in one sentence: for each product we built what it would "
          "have done anyway from earlier years, drew a band for ordinary month-to-month wobble, "
          "and this is how far outside that band 2025 went. Backup slide 10 shows the band on "
          "copper if anyone wants to see it.\n\n"
          "Some of these are plausible tariff stories: organic chemicals and pharmaceuticals "
          "were under open tariff threat in 2025, and gold moved into US vaults ahead of "
          "expected duties.\n\n"
          "Some are not. Silk is a 55-million-dollar chapter, so almost any month looks extreme "
          "next to its own history. Works of art and clocks are small and lumpy.\n\n"
          "Cocoa is the one to dwell on. It is on the list because cocoa prices roughly tripled after "
          "bad West African harvests. We measure in dollars, so a price spike reads as a volume "
          "surge.\n\n"
          "So the detector finds unusual months. It does not know why. Something has to connect "
          "an unusual month to an actual tariff, and that is the next slide.")

# ---------------------------------------------------------------- 7 finding
add("And this is where it nearly came apart.",
    fig="07_coverage.png",
    caption="Fig. 5   The typical tariff action covers about 5% of its chapter's value. A third cover under 1%.\n"
            "Copper, for example: ten actions touch it, and seven cover under 1% of it.\n"
            "Published work measures these at 8 to 10 digits [1]; coarser data shrinks estimates [2][3].",
    notes="THE KEY SLIDE. If time runs short, this is the one that must survive.\n\n"
          "A tariff order does not say 'chapter 74, copper'. It points at a list of 8-digit "
          "product codes, usually published in a separate legal notice. Until you read those "
          "lists, the only thing you can do is treat a whole chapter as tariffed whenever an "
          "action touches anything inside it.\n\n"
          "We read them: 9,083 distinct 8-digit codes across 162 surcharge codes. Say 'surcharge "
          "codes' and not 'actions', because 134 is the number of Federal Register actions and "
          "the two are not the same thing.\n\n"
          "The typical action covers about 5% of its chapter's value. A third cover under 1%.\n\n"
          "So chapter-level treatment means roughly 95% of what you are measuring is trade the "
          "tariff never touched. Any real reaction in the 5% gets averaged away by the 95% that "
          "did nothing.\n\n"
          "That is exactly what happened to us. Our first attempt to measure an effect found "
          "nothing. The null was our ruler, not the world.\n\n"
          "SAY 'ONE OF THREE REASONS'. coverage/FINDINGS.md lists three causes of that null and "
          "ranks this one second. The first is that our announcement dates are mostly "
          "implementing notices, so the median official window is nine days and there is barely "
          "any anticipation period left in the data; the copper story on slide 2 is the answer "
          "to that, since the rush runs on news rather than on documents. The third is that the "
          "partner dimension was collapsed, which the across-origins design on slide 8 fixes. "
          "Dilution is the one that generalizes beyond us, which is why it is the one on the "
          "slide. Do not call it the reason.\n\n"
          "The fix is to work at the 8-digit level, where a tariff either names a product or it "
          "does not. Everything after this is built that way.\n\n"
          "-- NARRATE IT THROUGH COPPER, which they already know from slides 2, 5 and 6 --\n"
          "The copper line is on the slide now, so do not just read it. Read it once, then add "
          "the part that is not up there:\n"
          "Ten separate tariff actions touch copper, chapter 74. Three of them cover more than "
          "half the chapter: 95%, 59%, 59%. The other seven cover under 1%, and several are "
          "civil-aircraft carve-outs that name a single product line. The median action touching "
          "copper covers less than a tenth of one percent of it.\n"
          "So if you mark copper as tariffed whenever any action fires, seven times out of ten "
          "you have flagged an entire chapter over something touching less than one percent of "
          "it. That is what the chart shows, across all 1,350 action-chapter pairs.\n\n"
          "IF ASKED '5% of what exactly': the median is taken over the 1,350 action-chapter "
          "pairs. Collapse it to one number per action and the median is 1.3%, so the slide is "
          "the conservative version.")

# ---------------------------------------------------------------- 8 status
add("Where we are.",
    bullets=["**Built and checked**",
             "140 months at the level tariffs are written, reconciled against published totals.",
             "**A detector, and its limit**",
             "It finds unusual months. It cannot tell a tariff from a price shock.",
             "**134 tariff actions, with the products behind each one**",
             "Start dates re-read from the order texts, plus the 8-digit product lists.",
             "**How we will measure it, and fix that limit**",
             "One product across origins: a price shock moves them all, a tariff moves one.",
             "**How we will know it is real**",
             "Every estimate against a placebo. Three methods have already failed it.",
             "**Next**",
             "Question 1 first, then questions 2 and 3 for the final report."],
    bullet_size=16, bullet_top=1.86, bullet_step=0.40, take_y=6.74, take_rule=True,
    caption="Take-away for anyone working with this data: do not measure tariff effects at chapter level.\n"
            "The typical action touches 5% of a chapter, so a real effect averages away to nothing.",
    notes="DISCUSSION AND NEXT STEPS.\n\n"
          "Be straight that this is data and limits, not results. Results come next.\n\n"
          "The fourth pair is the one to land, because it closes the problem slide 6 opened. "
          "Slide 6 said the detector cannot tell a tariff from a price shock. The answer is to "
          "stop comparing a product to its own past and start comparing it across origins in "
          "the same month: cocoa got more expensive for everyone, so every origin moves "
          "together and the comparison cancels it out. A tariff hits one origin, so it does "
          "not cancel. That one sentence is the method of the whole project.\n\n"
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
    caption="Fig. 6   2,792 Federal Register documents reviewed, 134 are real tariff actions.\nMedian gap from announcement to start date is about 9 days.",
    notes="BACKUP, not part of the talk. Use if asked where the tariff dates come from or how "
          "many actions there are.\n\n"
          "Two waves: 2018-19, and a much bigger one in 2025. The legal authority turns out to "
          "matter, which is why they are split out here.")

add("Backup: what a normal range looks like.",
    fig="04_normal.png",
    caption="Fig. 7   Copper against its own expected range, built only from data before the\n"
            "tariff. Seasonal-trend decomposition, after Cleveland et al. [6].",
    notes="BACKUP, not part of the talk. Use if asked how the normal range on slide 6 is built.\n\n"
          "Copper peaks 89% above normal against a band of 50%, so it clears.\n\n"
          "Aluminum does NOT clear: it peaks at 26% against a band of 100%, because its own "
          "history is volatile. Same tariff year, and the test says no. A test that can say no "
          "is the only kind worth having.")

# ------------------------------------------------- 11, references
sr = prs.slides.add_slide(BLANK)
chrome(sr)
txt(sr, "Backup: references.", X0, Y_HEAD, CW, 0.80, 38, bold=True)
refs = [
 "[1]  Fajgelbaum, P., Goldberg, P., Kennedy, P. and Khandelwal, A. (2020). The Return to",
 "       Protectionism. Quarterly Journal of Economics 135(1), 1-55.",
 "[2]  Schrammel, M. and Schreiber, S. (2023). How Does Data Aggregation Impact Elasticity of",
 "       Substitution Estimation? USITC Economics Working Paper 2023-10-B.",
 "[3]  Imbs, J. and Mejean, I. (2015). Elasticity Optimism. American Economic Journal:",
 "       Macroeconomics 7(3), 43-83.",
 "[4]  Flaaen, A. and Pierce, J. (2019). Disentangling the Effects of the 2018-2019 Tariffs on a",
 "       Globally Connected U.S. Manufacturing Sector. Federal Reserve FEDS 2019-086.",
 "[5]  Khan, S. Y. and Khederlarian, A. (2021). How does trade respond to anticipated tariff",
 "       changes? Evidence from NAFTA. Journal of International Economics 133, 103538.",
 "[6]  Cleveland, R., Cleveland, W., McRae, J. and Terpenning, I. (1990). STL: A seasonal-trend",
 "       decomposition procedure based on LOESS. Journal of Official Statistics 6(1), 3-73.",
]
y = 1.95
for ln in refs:
    txt(sr, ln, X0, y, CW, 0.34, 13, color=INK if ln.startswith("[") else GREY)
    y += 0.30
txt(sr, "Data: US Census international trade API  |  Federal Register API  |  USITC Harmonized Tariff Schedule, chapter 99",
    X0, Y_TAKE, CW, 0.5, 14, color=GREY)
sr.notes_slide.notes_text_frame.text = (
    "BACKUP, not part of the talk. Use if asked about prior work.\n\n"
    "The two that matter: [1] is the frontier paper on this exact shock and it works at HS-10, "
    "stating that the 2018 tariff increases were 'predominantly set at the 8-digit Harmonized "
    "System level'. That is why we pull at HS10 and analyse at HS8.\n\n"
    "[2] is USITC's own work estimating the same elasticity at HTS 2, 4, 6 and 8 digits and "
    "finding that estimates from aggregated data are smaller, which they attribute to "
    "heterogeneity bias. Our 5% number is the specific version of that general result.\n\n"
    "[4] faced the same problem and solved it the way we did: a continuous value-weighted "
    "coverage share instead of a binary tariffed/not flag.\n\n"
    "[3] is the general statement of the same aggregation problem outside tariffs. [5] is the "
    "closest prior work on front-loading itself: trade responds to tariff changes that are "
    "announced in advance, which is the behaviour slide 2 shows. [6] is the decomposition "
    "behind the normal range on slide 6 and backup slide 10.\n\n"
    "Worth saying plainly if asked: nobody appears to have published the specific diagnostic we "
    "ran, which is to assign treatment at chapter level when the tariff names HS8 and measure "
    "how much of the chapter that actually covers. The general attenuation result is known; the "
    "number for US tariff actions is ours.")

out = "slides/Mandadi_Khalsa_Presentation1.pptx"
prs.save(out)
import os
print(f"wrote {out}  ({len(prs.slides._sldIdLst)} slides, {os.path.getsize(out)/1000:.0f} KB)")
