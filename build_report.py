"""Render REPORT1.md to a PDF with the figures placed, via Chrome headless.

No pandoc on this machine, so markdown -> styled HTML -> print-to-pdf. Figures are referenced in
the markdown as [[FIG:n|file|caption]] and expanded here, so the prose and the figure order
cannot drift apart.

Usage:  python3 build_report.py      # from the repo root
"""
import base64
import os
import re
import subprocess

import markdown

SRC, HTML, PDF = "REPORT1.md", "report1.html", "Mandadi_Khalsa_Report1.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: letter; margin: 0.8in 0.85in; }
body { font-family: "Avenir Next", Helvetica, Arial, sans-serif; font-size: 10pt;
       line-height: 1.26; color: #14161A; }
h1 { font-size: 17pt; margin: 0 0 2pt 0; line-height: 1.2; }
h2 { font-size: 12pt; margin: 12pt 0 3pt 0; }
h3 { font-size: 10.5pt; margin: 9pt 0 2pt 0; }
p  { margin: 0 0 6pt 0; text-align: justify; }
figure { margin: 9pt 0; page-break-inside: avoid; text-align: center; }
figure img { width: 70%; }
figcaption { font-size: 8.5pt; text-align: left; color: #44474d; margin-top: 3pt; line-height: 1.3; }
table { border-collapse: collapse; font-size: 9.5pt; margin: 7pt 0; }
th, td { border-bottom: 1px solid #ccc; padding: 3pt 10pt 3pt 0; text-align: left; }
.meta { font-size: 10pt; margin: 0 0 3pt 0; }
"""


def fig(m):
    n, path, cap = m.group(1), m.group(2), m.group(3)
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    return (f'<figure><img src="data:image/png;base64,{b64}">'
            f'<figcaption><b>Fig. {n}.</b> {cap}</figcaption></figure>')


src = open(SRC).read()
src = re.sub(r"\[\[FIG:(\d+)\|([^|]+)\|([^\]]+)\]\]", fig, src)
body = markdown.markdown(src, extensions=["tables"])
open(HTML, "w").write(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head>"
                      f"<body>{body}</body></html>")

subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={PDF}", os.path.abspath(HTML)],
               check=True, capture_output=True)
out = subprocess.run(["pdfinfo", PDF], capture_output=True, text=True).stdout
pages = [l for l in out.split("\n") if l.startswith("Pages")]
print(f"wrote {PDF}  ({pages[0] if pages else '?'})")
