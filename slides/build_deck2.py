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


# ---------------------------------------------------------------- 1 title
s = prs.slides.add_slide(BLANK)
chrome(s, names=False)
txt(s, "Borrowed or Real", X0, 2.05, CW, 1.05, 48, bold=True)
txt(s, "When a tariff hits, does the business come back?", X0, 3.12, CW, 0.7, 25, color=RED)
txt(s, "Rahul Reddy Mandadi   +   Raunaksingh Khalsa", X0, 4.18, CW, 0.5, 18, bold=True)
txt(s, "DS 5500 Data Science Capstone   |   Presentation 2   |   November 2026",
    X0, 4.66, CW, 0.5, 13, color=GREY)
txt(s, "For importers and lenders who depend on one supplier country.",
    X0, 5.52, CW, 0.9, 13, color=GREY)
txt(s, "github.com/rahul-mandadi/tariff-rush", X0, Y_TAKE, CW, 0.4, 13, bold=True, color=RED)
s.notes_slide.notes_text_frame.text = (
    "SPEAKER SPLIT: suggest Rahul 1-5, Raunak 6-11. Both must speak.\n"
    "Target under 10 minutes.\n\n"
    "Open with one line: a tariff is a tax on imports.\n\n"
    "The story: copper looks like it came back, but only the untaxed part did; and across "
    "hundreds of antidumping cases, the targeted country does not regain its earlier position "
    "for at least the 18 months we can see.")

# ---------------------------------------------------------------- 2 the question, with copper
add("Copper rushed in, crashed, then came back.", fig="01_context.png",
    caption="When a tariff is announced, importers often buy early, then imports drop. Is that "
            "drop borrowed, meaning they bought ahead and will be back, or real, meaning the "
            "business has left? Copper looks borrowed: total imports came back.",
    notes="This is the question in the title. Borrowed means bought early and comes back. Real "
          "means gone.\n\n"
          "Copper is our running example because the answer is not what it looks like. Hold that "
          "thought for two slides.")

# ---------------------------------------------------------------- 3 coverage (finding 1)
add("But most copper was outside this duty.", fig="09_sankey.png",
    caption="The 50% duty named wire, tubes and sheets: 29% of copper imports by value. Refined "
            "cathodes, copper sold as a raw input and 67% of the total, were outside it. That is "
            "typical: a tariff usually names about 5 dollars of every 100 its category imports.",
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

# ---------------------------------------------------------------- 4 the copper split
add("Split it, and the answer appears.", fig="11_copper_split.png",
    caption="The duty's main taxed products fell to about half their old level and stayed there. "
            "Untaxed cathodes are what came back. For the products the duty hit, the drop looks real. "
            "One material and one tariff, so an example; the next slides test it across hundreds.",
    notes="Numbers if asked, thousand tonnes a month: the taxed group ran 49 before, peaked at 68, "
          "settled at 27. Cathodes ran 89, peaked at 218, settled at 154.\n\n"
          "The two lines are the main taxed group (headings 7407 to 7413: bars, wire, plates, foil, "
          "tubes, fittings) and refined cathodes, not every copper product. Which is taxed comes "
          "from the proclamation's own paragraphs; its product annex is not in the Federal Register "
          "text we hold, so groups are assigned by what each heading covers.\n\n"
          "Both lines rose before the list of taxed products came out at the end of July. After it, "
          "only the taxed group stayed down.")

# ---------------------------------------------------------------- 5 the method
add("How we measure it, product by product.",
    bullets=[
        "**One product from one country, every month,** using the eight-digit product codes "
        "tariff orders are written in: 15.9 million rows of Census trade data, 2015 to 2026.",
        "**Compared with other countries selling the same product that month.** A price or "
        "demand change shared by all of them cancels out; the duty hits one.",
        "**Checked against a fake date.** The identical calculation on the same cases two years "
        "earlier, before those cases. A real effect has to beat the fake one.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.62,
    caption="Values are in nominal dollars. Price changes shared by every country, such as general "
            "inflation, cancel in this comparison.",
    take_rule=True,
    notes="This is the method Kylie asked us to explain.\n\n"
          "Why compare countries within a product: 2020 to 2025 moved every trade series at once. "
          "A before-and-after on one country cannot tell that apart from the duty. Comparing with "
          "other suppliers of the same product in the same month removes what they share.\n\n"
          "The caveat, if pushed: a price change specific to one country does not cancel, and a "
          "supplier that picks up the lost business is itself in the comparison group, so this "
          "measures relative standing.")

# ---------------------------------------------------------------- 6 the aftermath (finding 2)
add("The targeted country does not bounce back.", fig="10_event_plain.png",
    caption="Antidumping and countervailing duties tax one product from one named country. Across "
            "673 such events, its dollar imports ran 42% above its usual level against rival "
            "suppliers before the duty and averaged 6% after, without returning in the 18 months "
            "we see. Part may be an earlier run-up unwinding.",
    notes="Define both on the way in: an antidumping duty answers a complaint that a foreign "
          "producer sells below its home price; a countervailing duty answers a complaint that it is "
          "subsidised. Both name one product and one country, and there are hundreds of them, which "
          "is why we can test the question here.\n\n"
          "Reading the chart: zero is the country's usual position against rival suppliers, measured "
          "a year and a half before the case. It is not zero imports.\n\n"
          "So for these duties the drop looks real, not borrowed: eighteen months on, the country's "
          "position has not come back. That is a lasting fall in relative dollar value, not proof the "
          "business left for good, and we cannot yet say where it went.\n\n"
          "If asked how strong: the chart is 673 events. A separate per-case test on 508 episodes "
          "(338 antidumping, 169 countervailing, one unlabelled) compares each with its fake date "
          "and separates at p < 0.0001. Eight of those 508 are preliminary notices that did not "
          "start collection.")

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
            "in dollars because its price roughly tripled. Pharmaceuticals barely moved in tonnes but "
            "jumped in dollars in March 2025, led by Swiss medicines at about $5,000 a kilo.",
    notes="The takeaway: a category's dollar total alone can mislead, in both directions.\n\n"
          "Pharmaceuticals scores 2.26 on dollars and minus 0.34 on tonnes. In the medicine line "
          "with the biggest March jump, Swiss shipments ran about $5,185 a kilo against $183 for "
          "Indian ones, so a shift toward Swiss product lifts dollars far more than tonnes.\n\n"
          "This check applies to the category rankings. The antidumping result on slide 6 is in "
          "dollars, compared within the same product.")

# ---------------------------------------------------------------- 9 discussion
add("What this means.",
    bullets=[
        "**For an importer tied to one country:** after an antidumping duty the supplier did not "
        "regain its earlier position in the 18 months we see, so waiting it out is risky.",
        "**For anyone measuring tariffs:** study the products a tariff names, not the whole "
        "category, and check physical quantities as well as dollars.",
        "**For timing:** what matters is when a tariff becomes likely, not when it becomes "
        "official. Copper imports rose during the investigation, months before the duty.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.78,
    notes="This is the Discussion. One takeaway for each audience; about a minute.\n\n"
          "The first bullet is a reading of the evidence, not a tested rule for any one importer. "
          "Turning it into one is what the next step is for.")

# ---------------------------------------------------------------- 10 what the checks confirmed
add("What the checks confirmed.",
    bullets=[
        "**Inflation.** Values are nominal dollars. A price change shared by all suppliers leaves "
        "the main comparison unchanged; the category ranking keeps 8 or 9 of its top 10.",
        "**Finer product codes.** The data now uses the eight-digit codes tariffs name.",
        "**The tariff list.** 120 tariff documents, each tagged with the law it rests on.",
        "**Unusual-month score.** Now on one consistent scale; same top ten categories.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.62,
    caption="Each check runs from a script in the repository.",
    take_rule=True,
    notes="These answer Kylie's notes from Presentation 1.\n\n"
          "Say this about the list, since Kylie flagged it: last time we said 134. Fourteen of those "
          "were Labor Department notices about retraining for laid-off workers, not tariffs, so the "
          "list is 120.\n\n"
          "Inflation, two BLS price indexes: adjusting by all import prices keeps 8 of the top 10 "
          "(rank correlation 0.97); by non-fuel import prices, 9 of 10 (0.99). The all-imports index "
          "is driven by fuel, which fell over 2022 to 2024. Neither touches the antidumping result, "
          "where a shared price change cancels.\n\n"
          "The score: the old version divided a percentage gap by a log-scale wobble. Fixed, the "
          "scores shrink (pharmaceuticals 2.86 to 2.26), positions shift slightly, and the same ten "
          "categories stay in the top ten.")

# ---------------------------------------------------------------- 11 next
add("Next: how long until it comes back?",
    bullets=[
        "**The question.** For a business tied to one country, how long until its supplier is "
        "back within its usual range?",
        "**The data.** 508 antidumping and countervailing cases, some still running today.",
        "**The method.** A survival model, built for how-long questions, which keeps cases that "
        "have not recovered yet instead of dropping them.",
        "**The deliverable.** For an importer facing a case on their product: what usually "
        "happens, and how long it takes.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.62,
    caption="Report 2 and the final presentation.",
    take_rule=True,
    notes="Close here: the targeted country does not regain its earlier position for at least 18 "
          "months; the next question is how long.\n\n"
          "If asked about the rush itself: we are rebuilding the tariff list document by document, "
          "checking which countries each tariff actually hit and from what date, before we report "
          "anything on it.")

out = "slides/Mandadi_Khalsa_Presentation2.pptx"
prs.save(out)
print(f"wrote {out}  ({len(prs.slides._sldIdLst)} slides, {os.path.getsize(out)/1000:.0f} KB)")
