"""Dump every visible word of the deck, in reading order, for proofreading.

Shapes are emitted top-to-bottom then left-to-right, which is also how a reader scans the
slide. Because build_deck.py gives each bullet its own text box, a box printed out of
sequence means two boxes overlap on the slide, so this dump doubles as a layout check.

Usage:  python3 slides/dump_text.py      # from the repo root
"""
from pptx import Presentation
from pptx.util import Emu

SRC = "slides/Mandadi_Khalsa_Presentation1.pptx"
OUT = "slides/DECK_TEXT.txt"
TALK = 8

prs = Presentation(SRC)
L = [f"DECK TEXT DUMP  -  {SRC.split('/')[-1]}",
     f"{len(prs.slides._sldIdLst)} slides: {TALK} talk, {len(prs.slides._sldIdLst)-TALK} backup",
     "Every visible word on every slide, in reading order, with font size.",
     "Speaker notes follow each slide, marked NOTES. Notes do not appear in the PDF.",
     "=" * 78, ""]

for i, s in enumerate(prs.slides, 1):
    L += ["=" * 78, f"SLIDE {i}  [{'TALK' if i <= TALK else 'BACKUP'}]", "=" * 78]
    shapes = [sh for sh in s.shapes if sh.left is not None]
    shapes.sort(key=lambda sh: (round(Emu(sh.top).inches, 1), round(Emu(sh.left).inches, 1)))
    for sh in shapes:
        if sh.shape_type == 13 or sh.__class__.__name__ == "Picture":
            L.append(f"  [FIGURE  {Emu(sh.width).inches:.1f} x {Emu(sh.height).inches:.1f} in]")
            continue
        if not sh.has_text_frame:
            continue
        for pa in sh.text_frame.paragraphs:
            t = ''.join(r.text for r in pa.runs)
            if not t.strip():
                continue
            sz = next((r.font.size.pt for r in pa.runs if r.font.size), 0)
            b = "B" if any(r.font.bold for r in pa.runs) else " "
            L.append(f"  {sz:5.1f}pt {b}  {t}")
    if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip():
        L += ["", "  --- NOTES ---"]
        L += [f"  | {ln}" for ln in s.notes_slide.notes_text_frame.text.split("\n")]
    L.append("")

open(OUT, "w").write("\n".join(L))
print(f"wrote {OUT}  ({len(L)} lines)")
