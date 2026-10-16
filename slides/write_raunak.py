"""Write slides/RAUNAK_SCRIPT.md: Raunak's half, standalone, from slides/speech.py.

Separate file because it is a thing to send someone, not a thing to present from. It has to
stand on its own: Raunak has not sat through the analysis, so every slide gets a plain sentence
saying what it is for before the words to say.

Usage:  python3 slides/write_raunak.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import speech

MINE = [5, 6, 7, 8]
TITLE = {5: "What we have", 6: "Unusual is not the same as tariffed",
         7: "And this is where it nearly came apart", 8: "Where we are"}

# one plain sentence per slide so he knows what he is doing, not just what to recite
JOB = {
5: "This is the data slide. You are telling them where the numbers come from, what one row is, "
   "and why we pulled it at ten digits instead of something coarser. The ten digit bit is the "
   "part that matters later, so do not rush it.",
6: "This is the honest slide. You show the first thing we tried, and then you say why it is not "
   "enough. The point you are landing is that finding a weird month is not the same as finding a "
   "tariff. Cocoa is the example that proves it.",
7: "This is the most important slide in the deck. You are telling them our first attempt "
   "returned nothing, and then telling them exactly why. If you only nail one slide, nail this.",
8: "This is the close. A list of what exists, how we will measure it, how we will check it is "
   "real, and one thing for them to take away.",
}

NUMBERS = [
 ("five percent", "the typical tariff action covers about 5% of its product group's value"),
 ("a third", "a third of them cover less than 1%"),
 ("ninety-five percent", "so about 95% of what you measure was never tariffed"),
]

L = [
"# Raunak, this is your half",
"",
"Slides 5 to 8. Rahul takes 1 to 4 and hands over by saying your name, at about "
f"{speech.ms(speech.clock(4))}.",
"",
f"**Your half is about {speech.ms(sum(speech.secs(n) for n in MINE))}.** The whole talk has to come in "
"under 10 minutes, so there is not much slack. The same words are in the speaker notes in the "
"pptx, under SAY THIS on each slide, so you can present straight off the notes.",
"",
"You do not have to say it word for word. Say it however it comes out naturally. The one thing "
"to keep exact is the numbers.",
"",
"---",
"",
"## What Rahul has already said, so you can pick up from it",
"",
"- A tariff is a tax on imports. It gets announced one day and starts on a later day, and "
"importers rush to get goods in before it starts. Then imports drop.",
"- Our question is what that drop means. Borrowed means the goods just came early and it evens "
"out. Real means the business went somewhere else and stayed there.",
"- The reason anyone cares: somebody has to decide on announcement day whether to find a new "
"supplier, and the official data does not arrive for about two months.",
"- He ends on our three questions, then says your name.",
"",
]

for n in MINE:
    L += ["---", "",
          f"## Slide {n}. {TITLE[n]}",
          "",
          f"*{speech.ms(speech.secs(n))}*",
          "",
          f"**What this slide is doing:** {JOB[n]}",
          "",
          "**Say:**",
          "",
          speech.SPEAK[n],
          "",
          f"**While you say it:** {speech.CUE[n]}",
          ""]

L += ["---", "", "## The numbers to get exactly right", "",
      "Everything else you can paraphrase. These three are the argument on slide 7:", ""]
for a, b in NUMBERS:
    L.append(f"- **{a}** : {b}")
L += ["",
      "And the sentence that carries it, which is worth saying slowly:",
      "",
      "> If you label a product group tariffed when ninety-five percent of it wasn't, the real",
      "> reaction in that five percent gets averaged away by everything that didn't move.",
      "",
      "---", "", "## If someone asks you something", "",
      "These are the ones likely to land on your slides. Short answers are fine, and \"we are "
      "still testing that\" is a real answer, not a cop-out.", ""]
for q, a in speech.QA:
    L += [f"**\"{q}\"**", "", a, ""]
L += ["---", "",
      "## If you want to swap",
      "",
      "Slide 7 is the hardest one and it is in your half. If you would rather Rahul took 7 and you "
      "closed on 8, that works and it is easy to switch. Slide 8 is a list and a takeaway line. "
      "Just say so before the rehearsal rather than on the day.",
      ""]

open("slides/RAUNAK_SCRIPT.md","w").write("\n".join(L) + "\n")
w = sum(len(speech.SPEAK[n].split()) for n in MINE)
print(f"wrote slides/RAUNAK_SCRIPT.md  ({w} spoken words, "
      f"{speech.ms(sum(speech.secs(n) for n in MINE))})")
