"""Build the Presentation 2 resubmission (v2) as an editable .pptx.

Same deck as slides/build_deck2.py (which built the version submitted on 2026-11-06 and is kept
unchanged), with the results replaced by the November corrections in FINAL_REPORT.md:

  slide 5   new: the public evidence that importers make this decision
  slide 6   method now says months with no trade count as zero, and how many notices were read
  slide 6   the aftermath split by whether the duty became permanent (fig 12), replacing "the
            targeted country does not bounce back" and its "42 percent above its usual level"
  slide 7   new: what happened to each targeted product within 18 months (fig 14)
  slide 9   notes: the antidumping result holds in physical quantity
  slide 10  discussion rewritten to the corrected numbers
  slide 11  checks: quantity, and the 21 notices removed
  slide 12  the monthly forecast (fig 19)
  slide 13  the lookup (fig 16) and the next step

Every number traces to FINAL_REPORT.md. Style and helpers are build_deck2.py's, unchanged.

Usage:  python3 slides/build_deck2b.py      # from the repo root
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
    "SPEAKER SPLIT: suggest Rahul 1-6, Raunak 7-12. Both must speak.\n"
    "Target under 10 minutes.\n\n"
    "Open with one line: a tariff is a tax on imports.\n\n"
    "The story: copper looks like it came back, but only the untaxed part did. Across hundreds "
    "of antidumping cases, where the duty becomes permanent the targeted country loses about a "
    "third of its position and does not get it back within 18 months; nearly six in ten "
    "targeted products fall and stay down.")

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

# ---------------------------------------------------------------- public evidence that the decision exists
add("Importers make this call, and it is slow.",
    bullets=[
        "**They switch.** In the trade commission's own surveys, 27 of 54 aluminum extrusion "
        "buyers and 23 of 45 steel nail buyers changed suppliers, mostly for other reasons.",
        "**It takes months.** Qualifying a new supplier took from days to 18 months; tin mill "
        "buyers averaged about seven.",
        "**Some move early.** Floor & Decor moved its Chinese tile sourcing to other countries "
        "after the 2019 preliminary duties.",
        "**Waiting can pay.** Deposits are refunded if the duty is lifted, so when to act matters.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.66,
    caption="Sources: USITC final staff reports, Publications 5560, 5370 and 5492; Floor & Decor "
            "Form 10-K, February 2020.",
    take_rule=True,
    notes="This is who the answer is for, and the evidence that they make this decision.\n\n"
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
          "So the decision starts early, but finishing it takes months, and deposits are refunded if "
          "the duty is lifted, which is why a forecast that sharpens over the first months could "
          "help. This shows the decision and its timing exist; it does not validate our forecast "
          "or measure what it would save. Only a few purchasers per report tie their switching to "
          "the case itself.")

# ---------------------------------------------------------------- 5 the method
add("How we measure it, product by product.",
    bullets=[
        "**One product from one country, every month,** using the eight-digit product codes "
        "tariff orders are written in: 15.9 million rows of Census trade data, 2015 to 2026.",
        "**Compared with other countries selling the same product that month,** with months of "
        "no trade counted as zero. A change shared by all of them cancels out.",
        "**Checked against a fake date.** The same calculation on the same cases two years "
        "earlier. A real effect has to beat the fake one.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.62,
    caption="707 preliminary notices form 507 country cases; 384 have a full 18 months, 286 a fake "
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
          "We read every decision notice: 21 of 728 did not start a duty (negative findings, "
          "side notices, reviews of old orders) and are out. Uncertainty is computed over whole "
          "investigations, because one petition often names several countries.")

# ---------------------------------------------------------------- 6 the aftermath (finding 2)
add("Losses persist in cases that become orders.", fig="12_order_vs_negative.png",
    caption="These duties tax one product from one named country. Where the duty became permanent "
            "(329 cases), that country's imports fell about 31% against rival suppliers over the 18 "
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

# ---------------------------------------------------------------- 7 outcomes (finding 3)
add("Six in ten fall and do not recover.", fig="14_outcomes.png",
    caption="384 cases, each counted once. 25% did not fall, 17% fell and recovered, 42% stayed "
            "down while trading, 16% fell and had no imports in months 13 to 18 (fake date: 3%).",
    notes="This is what a buyer of one of these products can expect.\n\n"
          "Definitions: fell means the country's share of the product's imports dropped at least "
          "a fifth below its level before the case, within six months of the duty. Came back "
          "means back at or above that level for three months in a row. Stopped trading means no "
          "imports at all in months 13 to 18. Each case counts once, and only cases with a full 18 "
          "months are in the shares.\n\n"
          "Counting from the month of the fall, about one in four products was back within 18 "
          "months of falling, against six in ten on the fake date. Where the commission confirmed "
          "the duty, nearly one in five fell and stopped trading.\n\n"
          "Stopped trading is a subset of falling and not coming back. Counting every product, "
          "including a few that came back first, 19% had no imports in months 13 to 18.\n\n"
          "Robust: with a 10% or 30% definition of a fall, 16% still stop trading. On just the "
          "282 cases that also have a fake date, 13% stop trading against 3%. And built only "
          "from earlier cases, these rates beat a blind guess on later cases in five of six "
          "years.")

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
          "This check applies to the category rankings. The antidumping result holds in physical "
          "quantity: among months with trade, quantity and value estimates are similar (minus 0.31 "
          "and minus 0.30 log points). Both ranges include zero, so this is consistent with lower "
          "volume but does not rule out price changes.")

# ---------------------------------------------------------------- 10 discussion
add("What this means.",
    bullets=[
        "**For an importer tied to one country:** weigh qualifying another supplier early. Six "
        "in ten targeted products fell without recovering; one in six also had none a year on.",
        "**When to look again:** on day one, use the historical rates; once a product has fallen, "
        "a monthly model tells recoveries apart better.",
        "**For anyone measuring tariffs:** study the products a tariff names, not the whole "
        "category, and check quantities as well as dollars.",
    ],
    bullet_size=20, bullet_top=2.15, bullet_step=0.78,
    notes="This is the Discussion. One takeaway for each audience; about a minute.\n\n"
          "The first bullet comes from 384 past cases. It is what usually happens, not a promise "
          "for any one supplier, and we have not tested it with importers.\n\n"
          "We find no clear average surge before these duties, so little buying ahead to pay back. "
          "For cases that became orders the answer is closer to real than borrowed, over the 18 "
          "months we observe; that is not proof the business left for good.")

# ---------------------------------------------------------------- 11 what the checks confirmed
add("What the checks confirmed.",
    bullets=[
        "**Inflation and price.** Shared price changes cancel; in tonnes the fall matches dollars.",
        "**Every duty decision read.** 707 kept; 21 that started no duty removed.",
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
          "The 21 notices removed: 4 negative findings, 9 side notices about retroactive duties, "
          "8 reviews of orders that already existed.")

# ---------------------------------------------------------------- 12 next
add("By month 4, the forecast tells them apart.", fig="19_monthly_forecast.png",
    caption="Held-out later years, data as published each month. Day one: no reliable gain. "
            "Month 4: 78% of pairs ranked correctly; month 5: 81%. Next slide: the model as a lookup.",
    notes="Where the duty stays, the business does not come back, and within a few months we can "
          "tell fairly well which products will.\n\n"
          "Each month the model re-scores every product that has visibly fallen and is not yet "
          "back, using only trade data Census had published, notices published by then, and rivals "
          "not yet named in another case; it trains only on earlier cases whose outcomes were "
          "published.\n\n"
          "Numbers if asked: day one, Brier 0.240 against 0.249 for history, a gain of 0.008 whose "
          "range includes zero. By month 4, boosting ranks a product that came back above one that "
          "did not in 78% of pairs, 0.040 better than that month's historical rate (0.027 to "
          "0.052); by month 5, 81%. In months 4 to 6 it outperformed a latest-share model by 0.012 "
          "to 0.016. These are products already falling, a set that changes month to month, and "
          "the sample is 139 investigation groups, not the 16,969 product-month rows.")

# ---------------------------------------------------------------- 13 the lookup
add("Under half the old share, few come back.", fig="16_lookup.png",
    caption="Held-out years only. Each cell: of 100 products that fell, how many came back by month "
            "18. Next, by December 11: whether this holds for China's 2018 tariffs.",
    take_rule=True,
    notes="Close here: this is what a sourcing team would read. Where the duty was confirmed and "
          "the published share is under half its old level, 13 in 100 came back; where it was "
          "lifted and the share is back to four-fifths, 82.\n\n"
          "Small text in each cell: the model's estimate and how many cases are behind it. "
          "Recalibrating on earlier years made later years worse, so the estimates are the model's "
          "own; at the vote its most confident third runs about 12 points high, so we show what "
          "happened first.\n\n"
          "If asked about the rush before tariffs like copper's: we are rebuilding that tariff "
          "list document by document before we report anything on it.")

out = "slides/Mandadi_Khalsa_Presentation2_v2.pptx"
prs.save(out)
print(f"wrote {out}  ({len(prs.slides._sldIdLst)} slides, {os.path.getsize(out)/1000:.0f} KB)")
