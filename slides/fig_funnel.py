"""Figure: how 10,730 Federal Register notices become 502 cases (the data cleaning and matching steps).

Reads:  events/adcvd_index.json, events/adcvd_events.csv, events/adcvd_products.csv, panel/hs8/,
        adcvd_episodes_collapsed.csv, panel/adcvd_stacks_real.parquet, and the notice lists in
        measure/adcvd_stacked.py
Writes: slides/fig/25_matching_funnel.png
Run:    python3 slides/fig_funnel.py      (after measure/adcvd_stacked.py)
"""
import ast
import glob
import json
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

K_HI = 18


def stacked_constant(name):
    """A constant from measure/adcvd_stacked.py, read without running that script."""
    for node in ast.parse(open("measure/adcvd_stacked.py").read()).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return ast.literal_eval(node.value)
    raise KeyError(name)


EXCLUDE, CC_ONLY, INI_FIX = (stacked_constant(n) for n in ["EXCLUDE", "CC_ONLY", "INI_FIX"])

# the same filters, in the same order, as measure/adcvd_stacked.py
listed = json.load(open("events/adcvd_index.json"))
e = pd.read_csv("events/adcvd_events.csv", dtype={"cty": str})
for doc, ini in INI_FIX.items():
    r = e.document_number == doc
    e.loc[r, "initiation_date"] = ini
    e.loc[r, "window_days"] = (pd.to_datetime(e.loc[r, "publication_date"]) - pd.Timestamp(ini)).dt.days
p = pd.read_csv("events/adcvd_products.csv", dtype={"hs8": str})
prods = {d: set(g.hs8) for d, g in p.groupby("document_number")}

prelim = e[e.stage == "preliminary"]
dated = prelim[prelim.window_days.notna() & (prelim.window_days >= 60)]
coded = dated[dated.document_number.isin(prods)]
kept = coded[~coded.document_number.isin(EXCLUDE | CC_ONLY)]

files = sorted(glob.glob("panel/hs8/*.parquet"))
in_panel = set(pd.concat([pd.read_parquet(f, columns=["hs8"]) for f in files]).hs8)
last_month = max(int(f[-15:-11]) * 12 + int(f[-10:-8]) - 1 for f in files)
named = set().union(*(prods[d] for d in kept.document_number.unique()))
kept = kept[kept.document_number.map(lambda d: bool(prods[d] & in_panel))]

ep = pd.read_csv("adcvd_episodes_collapsed.csv", dtype={"cty": str})
stacked = set(pd.read_parquet("panel/adcvd_stacks_real.parquet", columns=["sid"]).sid)
compared = ep[ep.index.isin(stacked)]
full = compared[compared.b + K_HI <= last_month]

n = lambda d: d.document_number.nunique()  # noqa: E731
removed = len(set(coded.document_number) & (EXCLUDE | CC_ONLY))
assert (n(kept), len(kept), len(ep), removed, len(full)) == (687, 697, 502, 31, 381), \
    (n(kept), len(kept), len(ep), removed, len(full))

steps = [
    ("Antidumping and countervailing notices,\nFederal Register 2015 to 2026", len(listed),
     f"dropped {len(listed) - n(e):,}: yearly reviews of existing duties, sunset reviews, court decisions"),
    ("Notices from new investigations", n(e),
     f"dropped {n(e) - n(prelim):,}: case openings, final decisions, orders "
     "(collection starts at the preliminary)"),
    ("Preliminary decisions", n(prelim),
     f"dropped {n(prelim) - n(dated)}: opening date missing or fewer than 60 days before "
     "the preliminary decision"),
    ("... with the case's opening date", n(dated),
     f"dropped {n(dated) - n(coded)}: no product code could be read from the text"),
    ("... with product codes", n(coded),
     f"dropped {removed}: start no new duty (negative findings, side notices, reviews, circumvention)"),
    ("Notices that start a new duty", n(kept),
     f"{len(kept)} country decisions; companion notices merged into one case per country and investigation"),
    ("Cases", len(ep),
     f"{ep.cluster.nunique()} groups, {ep.cty.nunique()} countries; dropped {len(ep) - len(compared)}: "
     f"under 18 months of data before the case, or no prior trade or rival"),
    ("Cases that can be compared with rivals", len(compared),
     f"dropped {len(compared) - len(full)}: under 18 months of data after the duty so far"),
    ("Cases with all 18 months of data", len(full), ""),
]

plt.rcParams.update({
    "font.family": "Avenir Next", "font.size": 15, "text.color": "#14161A",
    "axes.edgecolor": "#6E737C", "figure.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white"})
RED, GREY, INK = "#C8102E", "#6E737C", "#14161A"
fig, ax = plt.subplots(figsize=(10, 10.5))
STEP = 2.6
top = len(listed)
for i, (label, count, note) in enumerate(steps):
    y = -STEP * i
    ax.barh(y, count, height=0.95, color=RED if label.startswith("Cases") else "#3A4150")
    ax.text(-0.01 * top, y, label, ha="right", va="center", fontsize=16)
    ax.text(count + 0.008 * top, y, f"{count:,}", ha="left", va="center", fontsize=17, fontweight="600")
    if note:
        ax.text(0, y - 0.65, textwrap.fill(note, 62), ha="left", va="top", fontsize=14.5, color=GREY,
                linespacing=1.15)
ax.set_xlim(0, top * 1.08)
ax.set_ylim(-STEP * len(steps) + 1.4, 0.8)
ax.axis("off")
ax.set_title(f"From {top:,} notices to {len(ep)} cases\n"
             f"product codes: {len(named & in_panel)} of the {len(named)} named by the kept notices "
             f"appear in the Census data",
             loc="left", x=-0.55, fontsize=17, fontweight="600", color=INK)
fig.savefig("slides/fig/25_matching_funnel.png")
print(f"wrote slides/fig/25_matching_funnel.png; {len(full)} cases with all 18 months "
      f"(panel ends {last_month // 12}-{last_month % 12 + 1:02d})")
