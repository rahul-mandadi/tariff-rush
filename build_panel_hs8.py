"""Roll the HS10 month checkpoints up to the analysis grid: HS8 x partner x month.

HS10 is the pull level because it nests exactly under the HS8 lines the tariff
orders name. HS8 is the analysis level because that is what the orders name.

Quantity needs care. UNIT_QY1 is the unit native to each HS10 line, so two lines
under the same HS8 can be measured in different units (KG and NO, say) and
summing them would be meaningless. Where that happens the quantity is set to
null and the cell is flagged, so those cells fall back to value rather than
silently carrying a nonsense number.

CTY_CODE "-" is a TOTAL FOR ALL COUNTRIES row sitting in the same response as
the countries it sums. Left in, it doubles every total. Dropped and kept aside,
it is a free reconciliation check: the 226 real partners must add back to it.

Writes one parquet per month so memory stays flat and a rerun is cheap.

Usage:  python3 build_panel_hs8.py
"""
import json, gzip, os, glob, sys
import pandas as pd
import numpy as np

SRC = "panel/hs10"
OUT = "panel/hs8"
NUM = ["GEN_VAL_MO", "GEN_QY1_MO", "AIR_WGT_MO", "VES_WGT_MO", "CNT_WGT_MO"]


def load_month(path):
    with gzip.open(path, "rt") as f:
        d = json.load(f)
    df = pd.DataFrame(d[1:], columns=d[0])
    # the API echoes the filtered columns back, so I_COMMODITY and CTY_CODE
    # arrive twice; keeping both makes df.col return a DataFrame, not a Series
    df = df.loc[:, ~df.columns.duplicated()]
    df = df[df.SUMMARY_LVL == "DET"]
    for c in NUM:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def roll_up(df, year, month):
    world = df[df.CTY_CODE == "-"].GEN_VAL_MO.sum()
    df = df[df.CTY_CODE.str.fullmatch(r"\d{4}")]
    df = df[(df.GEN_VAL_MO > 0) | (df.GEN_QY1_MO > 0)].copy()
    df["hs8"] = df.I_COMMODITY.str[:8]
    df["hs6"] = df.I_COMMODITY.str[:6]
    df["chapter"] = df.I_COMMODITY.str[:2]
    keys = ["hs8", "CTY_CODE"]

    out = df.groupby(keys, sort=False).agg(
        hs6=("hs6", "first"),
        chapter=("chapter", "first"),
        cty_name=("CTY_NAME", "first"),
        value=("GEN_VAL_MO", "sum"),
        air_wgt=("AIR_WGT_MO", "sum"),
        ves_wgt=("VES_WGT_MO", "sum"),
        cnt_wgt=("CNT_WGT_MO", "sum"),
        qty=("GEN_QY1_MO", "sum"),
        n_lines=("I_COMMODITY", "size"),
    )

    # unit check, over the rows that actually carry a quantity
    q = df[df.GEN_QY1_MO > 0]
    units = q.groupby(keys, sort=False).UNIT_QY1.agg(["nunique", "first"])
    out = out.join(units.rename(columns={"nunique": "n_units", "first": "unit"}))
    out["n_units"] = out.n_units.fillna(0).astype(int)
    mixed = out.n_units > 1
    out.loc[mixed, "qty"] = np.nan
    out.loc[mixed, "unit"] = "MIXED"
    out.loc[out.n_units == 0, "qty"] = np.nan
    out["qty_ok"] = out.n_units == 1

    out = out.reset_index().rename(columns={"CTY_CODE": "cty"})
    out["year"] = int(year)
    out["month"] = int(month)
    out["ym"] = pd.Period(f"{year}-{month:02d}", freq="M").to_timestamp()
    return out.drop(columns=["n_units"]), world


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    paths = sorted(glob.glob(f"{SRC}/*.json.gz"))
    if not paths:
        sys.exit(f"no checkpoints in {SRC}/ -- run harvest_hs10.py first")

    tot_in = tot_out = 0
    mixed_tot = 0
    fails = []
    for p in paths:
        stem = os.path.basename(p).replace(".json.gz", "")
        y, m = stem.split("-")
        dst = f"{OUT}/{stem}.parquet"
        if os.path.exists(dst):
            print(f"{stem}  cached", flush=True)
            continue
        df = load_month(p)
        out, world = roll_up(df, y, int(m))
        gap = out.value.sum() - world
        if world > 0 and abs(gap) / world > 1e-6:
            print(f"{stem}  RECONCILE FAIL  partners ${out.value.sum()/1e9:.3f}B "
                  f"vs world ${world/1e9:.3f}B", flush=True)
            fails.append(stem)
        tmp = dst + ".tmp"
        out.to_parquet(tmp, index=False, compression="zstd")
        os.replace(tmp, dst)
        nmix = int((out.unit == "MIXED").sum())
        tot_in += len(df); tot_out += len(out); mixed_tot += nmix
        print(f"{stem}  {len(df):>7,} hs10 -> {len(out):>7,} hs8 cells"
              f"   mixed-unit {nmix:>5,}   ${out.value.sum()/1e9:>7.1f}B",
              flush=True)

    print(f"\n{tot_in:,} HS10 rows -> {tot_out:,} HS8 cells")
    if tot_out:
        print(f"mixed-unit cells: {mixed_tot:,} ({100*mixed_tot/tot_out:.2f}%) "
              f"-- these fall back to value")
    mb = sum(os.path.getsize(f) for f in glob.glob(f"{OUT}/*.parquet")) / 1e6
    print(f"on disk: {len(glob.glob(f'{OUT}/*.parquet'))} months, {mb:,.0f} MB")
    if fails:
        sys.exit(f"\nreconciliation failed for {len(fails)} months: {fails}")
