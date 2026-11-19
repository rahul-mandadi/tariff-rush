"""Write slides/P2_SCRIPT.md, the spoken script for Presentation 2 v3, from the deck's own speaker notes.

The notes are written in slides/build_deck2c.py; this reads them back out of the built .pptx, so the
printed script and the notes in the deck cannot say different things. Edit build_deck2c.py, rebuild,
then rerun this.

Reads:  slides/Mandadi_Khalsa_Presentation2_v3.pptx
Writes: slides/P2_SCRIPT.md
Run:    python3 slides/write_script2.py      (after python3 slides/build_deck2c.py)
"""
import re

from pptx import Presentation

DECK = "slides/Mandadi_Khalsa_Presentation2_v3.pptx"
MAIN = 13            # slides 1 to 13 are the talk; then the Backup divider and the backup slides
RAHUL_LAST = 8
SLOW, NORMAL = 130, 145  # words a minute

# likely questions, and the backup slide (by its headline) that answers each
QUESTIONS = [
    ("What does a term mean?", "Terms we use."),
    ("Why gradient boosting and not another model?", "Other models give the same answer."),
    ("What could the analyst see in January, before the outcome?", "Taiwan, January 2025: what the analyst saw."),
    ("Why a fifth? What if the fall cutoff moves?", "A different cutoff, the same answer."),
    ("Why aren't the no-import rows at the top of the list?", "Below 60%, how far it fell matters little."),
    ("What if the analyst can check more, or fewer?", "Review these first: 82% stayed down."),
    ("How accurate is the model, and when does it start to work?", "By month 4, the forecast ranks them better."),
    ("What happens when the trade commission lifts the duty?", "Losses persist in cases that become orders."),
    ("How did you get from the notices to 502 cases?", "From 10,730 notices to 502 cases."),
    ("How exactly is the comparison built?", "How we measure it, product by product."),
    ("Do importers actually change suppliers?", "Buyers respond to duties, but slowly."),
    ("Did copper's total really come back?", "Copper's total imports came back."),
    ("How much of copper did the duty cover?", "But most copper was outside this duty."),
    ("What about inflation, and the other data checks?", "What the checks confirmed."),
    ("Presentation 1 feedback: the unusual-month score", "How we spot an unusual month."),
    ("Presentation 1 feedback: dollars against quantity", "Dollars alone can fool you."),
]


def headline(slide):
    """The largest text on the slide, which is its headline (or the title on slide 1)."""
    best, size = "", 0
    for sh in slide.shapes:
        if not sh.has_text_frame or not sh.text_frame.text.strip():
            continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size and r.font.size.pt > size:
                    best, size = sh.text_frame.text.strip(), r.font.size.pt
    return best


def words(text):
    return len(re.findall(r"\b\w+\b", text))


def ms(seconds):
    return f"{int(seconds // 60)}:{int(round(seconds % 60)):02d}"


slides = list(Presentation(DECK).slides)
rows = []
for n, s in enumerate(slides[:MAIN], 1):
    say, asked = [], []
    for para in s.notes_slide.notes_text_frame.text.split("\n\n"):
        para = para.strip()
        if not para or para.startswith("TIMING"):
            continue
        if para.startswith(("If asked", "Don't guess")):
            asked.append(para)
            continue
        para = re.sub(r"^(RAHUL|RAUNAK): ", "", para)
        if para.startswith("HANDOFF: "):
            para = "*Handoff:* " + para[len("HANDOFF: "):]
        say.append(para)
    w = sum(words(p) for p in say if not p.startswith("*Handoff"))
    rows.append(dict(n=n, head=headline(s), who="Rahul" if n <= RAHUL_LAST else "Raunak", say=say, asked=asked, w=w))

backup = {headline(s): n for n, s in enumerate(slides, 1) if n > MAIN}
total = sum(r["w"] for r in rows)
half = {who: sum(r["w"] for r in rows if r["who"] == who) for who in ["Rahul", "Raunak"]}

L = ["# Presentation 2, spoken script", "",
     "Generated from the speaker notes in `slides/Mandadi_Khalsa_Presentation2_v3.pptx`. Do not edit this",
     "file: change the notes in `slides/build_deck2c.py`, rebuild, then run `python3 slides/write_script2.py`.", "",
     f"**{total} words.** At a careful {SLOW} words a minute that is {ms(total / SLOW * 60)}; at a normal "
     f"{NORMAL}, {ms(total / NORMAL * 60)}.",
     f"Rahul, slides 1 to {RAHUL_LAST}: {half['Rahul']} words, about {ms(half['Rahul'] / NORMAL * 60)}. "
     f"Raunak, slides {RAHUL_LAST + 1} to {MAIN}: {half['Raunak']} words, about {ms(half['Raunak'] / NORMAL * 60)}.",
     "Per-slide times below are at the normal pace. Rehearse once with a clock.", "",
     "You do not have to say it word for word. Keep the numbers exact.", ""]
for who in ["Rahul", "Raunak"]:
    L += ["---", "", f"## {who}", ""]
    for r in [r for r in rows if r["who"] == who]:
        L += [f"### Slide {r['n']}. {r['head']}", "", f"*about {ms(r['w'] / NORMAL * 60)}*", ""]
        L += sum(([p, ""] for p in r["say"]), [])
        if r["asked"]:
            L += ["**If asked:**", ""] + [f"- {re.sub(r'^If asked: ?', '', a)}" for a in r["asked"]] + [""]
L += ["---", "", "## Questions, and the backup slide that answers each", "",
      "| question | backup slide |", "| --- | --- |"]
for q, h in QUESTIONS:
    assert h in backup, f"no backup slide headed {h!r}"
    L.append(f"| {q} | {backup[h]}. {h} |")
L.append("")
open("slides/P2_SCRIPT.md", "w").write("\n".join(L))
print(f"wrote slides/P2_SCRIPT.md: {total} words, {ms(total / NORMAL * 60)} at {NORMAL} a minute; "
      f"Rahul {half['Rahul']}, Raunak {half['Raunak']}")
