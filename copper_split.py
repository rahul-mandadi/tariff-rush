"""The copper tonnage split either side of the Section 232 duty.

Reported in the appendix of REPORT1.md. Committed because the figures were first computed
interactively and nothing in the repository reproduced them, which is not a standard we want to
apply to other people's work and not our own.

Headings 7407 to 7413 are the semi-finished products the duty names; 74031100 is refined cathodes,
which paragraph 8 of Proclamation 10962 treats as an input material and does not tax. Both series
count only rows reported in kilograms. Windows are stated explicitly because the result moves with
them: a pre-action baseline of August 2024 to January 2025, the peak month of March to July 2025,
and a settled average over March to August 2026.

Usage:  python3 copper_split.py      # from the repo root
"""
import glob

import pandas as pd

SEMI = ["7407", "7408", "7409", "7410", "7411", "7412", "7413"]
CATH = "74031100"
BASE, PEAK, AFTER = ("2024-08", "2025-01"), ("2025-03", "2025-07"), ("2026-03", "2026-08")

rows = []
for f in sorted(glob.glob("panel/hs8/*.parquet")):
    d = pd.read_parquet(f, columns=["hs8", "qty", "unit"])
    d = d[d.unit == "KG"]
    h = d[d.hs8.astype(str).str.startswith("74")].copy()
    h["hd"] = h.hs8.astype(str).str[:4]
    rows.append(dict(ym=f.split("/")[-1][:7],
                     semi=h[h.hd.isin(SEMI)].qty.sum() / 1e6,
                     cath=h[h.hs8.astype(str) == CATH].qty.sum() / 1e6))
s = pd.DataFrame(rows).set_index("ym")

print("chapter 74, thousand tonnes a month, kilogram-reported rows only\n")
print(f"{'':28}{'baseline':>10}{'peak':>8}{'after':>8}{'after/base':>12}")
for col, lab in [("semi", "semi-finished (taxed)"), ("cath", "cathodes (not taxed)")]:
    b = s.loc[BASE[0]:BASE[1], col].mean()
    p = s.loc[PEAK[0]:PEAK[1], col].max()
    a = s.loc[AFTER[0]:AFTER[1], col].mean()
    print(f"  {lab:26}{b:>10.0f}{p:>8.0f}{a:>8.0f}{a/b:>11.2f}x")
