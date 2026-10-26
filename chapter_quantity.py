"""Rebuild the chapter anomaly ranking on quantity instead of dollars.

Kylie Bemis asked for this in the presentation on 2026-10-16, after the cocoa example: a dollar
series cannot tell a price spike from a volume surge, so the detector on slide 6 was measuring
the wrong thing for at least two of the ten chapters it flagged.

It is not a simple swap. Quantity is reported in the unit native to each product, and at chapter
level those units are mixed: apparel is in dozens, footwear in pairs, ships in units, and 56 of
98 chapters report kilograms for under 70% of their value. The anomaly measure is scale-free,
since it asks how far a chapter went outside its OWN band, so the unit does not have to match
across chapters. It does have to be stable within one.

So this keeps only the dominant unit per chapter, and only chapters where that unit covers at
least MIN_COVER of chapter value. Everything else has no usable quantity series at chapter level
and is reported as such rather than silently dropped.

Usage:  python3 chapter_quantity.py      # from the repo root
"""
import collections
import glob

import numpy as np
import pandas as pd

MIN_COVER = 0.80          # dominant unit must carry this much of a chapter's value
OUT = "eda/chapter_month_qty.csv"


def dominant_units():
    """The unit each chapter mostly trades in, and how much of its value that covers."""
    agg = collections.defaultdict(collections.Counter)
    for f in sorted(glob.glob("panel/hs8/*.parquet")):
        d = pd.read_parquet(f, columns=["chapter", "value", "unit"])
        d["ch"] = d.chapter.astype(str).str.zfill(2)
        for (ch, u), v in d.groupby(["ch", "unit"]).value.sum().items():
            agg[ch][u] += v
    rows = []
    for ch, c in agg.items():
        tot = sum(c.values())
        u, v = c.most_common(1)[0]
        rows.append(dict(chapter=ch, unit=u, cover=v / tot if tot else 0.0))
    return pd.DataFrame(rows).set_index("chapter")


def panel(dom):
    """Monthly quantity per chapter, counting only rows in that chapter's dominant unit."""
    rows = []
    for f in sorted(glob.glob("panel/hs8/*.parquet")):
        ym = f.split("/")[-1][:7]
        d = pd.read_parquet(f, columns=["chapter", "value", "qty", "unit"])
        d["ch"] = d.chapter.astype(str).str.zfill(2)
        d = d.join(dom.unit.rename("dom"), on="ch")
        keep = d[d.unit == d.dom]
        g = keep.groupby("ch").agg(qty=("qty", "sum"), value=("value", "sum"))
        for ch, r in g.iterrows():
            rows.append(dict(chapter=ch, ym=ym + "-01", qty=r.qty, value=r.value))
    return pd.DataFrame(rows)


def expected(s, cut="2024-12"):
    """Same counterfactual as gen_figures.py, so the two rankings are comparable."""
    pre = np.log(s[:cut])
    me = pre.groupby(pre.index.month).mean() - pre.mean()
    t = np.arange(len(pre))
    slope, intercept = np.polyfit(t[-36:], pre.values[-36:], 1)
    pred = np.exp(pre.values[-1] + slope * (np.arange(len(s)) - (len(pre) - 1))
                  + s.index.month.map(me).values)
    resid = pre.values - (intercept + slope * t) - pre.index.month.map(me).values
    return pd.Series(pred, index=s.index), float(np.std(resid, ddof=1))


def rank(df, col):
    out = []
    for ch, g in df.groupby("chapter"):
        s = g.set_index("ym")[col].sort_index()
        s = s[s > 0]
        if len(s) < 100 or s[:"2024-12"].min() <= 0:
            continue
        pred, sd = expected(s)
        dev = (s / pred - 1).loc["2025-01":"2025-08"]
        if dev.empty or sd == 0:
            continue
        out.append(dict(chapter=ch, ratio=dev.max() / (1.96 * sd)))
    return pd.DataFrame(out).set_index("chapter").ratio.sort_values(ascending=False)


dom = dominant_units()
usable = dom[dom.cover >= MIN_COVER]
print(f"chapters with a dominant unit covering >={MIN_COVER:.0%} of value: "
      f"{len(usable)} of {len(dom)}")

df = panel(dom)
df["ym"] = pd.to_datetime(df.ym)
df = df[df.chapter.isin(usable.index)]
df.to_csv(OUT, index=False)

q = rank(df, "qty")
v = rank(df, "value")
cmp = pd.DataFrame({"by_quantity": q, "by_dollars": v}).dropna()
cmp["unit"] = usable.unit
cmp = cmp.sort_values("by_quantity", ascending=False)

# chapter labels taken from the first heading of each chapter in the USITC tariff schedule
NAMES = {"01": "live animals", "05": "animal products", "09": "coffee & spices",
         "12": "oil seeds", "18": "cocoa", "26": "ores", "28": "inorganic chem",
         "29": "organic chemicals", "30": "pharmaceuticals", "41": "hides & leather",
         "43": "furskins", "45": "cork", "48": "paper", "50": "silk", "71": "gold & gems",
         "72": "iron & steel", "74": "copper", "76": "aluminium", "78": "lead", "80": "tin",
         "84": "machinery", "89": "ships", "91": "clocks", "97": "works of art"}
cmp["name"] = [NAMES.get(i, i) for i in cmp.index]

print(f"\nchapters rankable on both: {len(cmp)}\n")
print("TOP 10 BY QUANTITY (what the detector should have used)")
print(cmp.head(10)[["name", "unit", "by_quantity", "by_dollars"]].round(2).to_string(index=False))
print("\nTOP 10 BY DOLLARS (what slide 6 showed), and where they land on quantity")
d10 = cmp.sort_values("by_dollars", ascending=False).head(10)
print(d10[["name", "unit", "by_dollars", "by_quantity"]].round(2).to_string(index=False))
print(f"\nwrote {OUT}")
