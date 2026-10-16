"""Flatten the monthly gzips into one tidy panel and sanity-check it."""
import json,gzip,glob,csv,os,collections
RAW="panel/raw"; OUTCSV="panel/imports_hs2_panel.csv"
DROP_NAMES={"TOTAL FOR ALL COUNTRIES"}
NUM=("GEN_VAL_MO","AIR_WGT_MO","VES_WGT_MO","CNT_WGT_MO")

files=sorted(glob.glob(f"{RAW}/*.json.gz"))
print(f"monthly files on disk: {len(files)}")
n_in=n_out=0
months=set(); chapters=set(); partners=set()
val_by_month=collections.Counter()
with open(OUTCSV,"w",newline="") as fh:
    w=csv.writer(fh)
    w.writerow(["year","month","cty_code","cty_name","chapter",
                "value_usd","air_kg","ves_kg","cnt_kg"])
    for p in files:
        with gzip.open(p,"rt") as f: d=json.load(f)
        hdr=d[0]; idx={k:i for i,k in enumerate(hdr)}
        ym=os.path.basename(p).replace(".json.gz","")
        y,m=ym.split("-")
        for row in d[1:]:
            n_in+=1
            if row[idx["SUMMARY_LVL"]]!="DET": continue
            name=(row[idx["CTY_NAME"]] or "").strip()
            if name in DROP_NAMES: continue
            ch=(row[idx["I_COMMODITY"]] or "").strip()
            if len(ch)!=2: continue
            def num(k):
                v=row[idx[k]]
                try: return int(v)
                except (TypeError,ValueError): return 0
            vals=[num(k) for k in NUM]
            if vals[0]==0 and sum(vals[1:])==0: continue
            w.writerow([y,m,row[idx["CTY_CODE"]],name,ch]+vals)
            n_out+=1; months.add(ym); chapters.add(ch); partners.add(name)
            val_by_month[ym]+=vals[0]
print(f"rows read   : {n_in:,}")
print(f"rows kept   : {n_out:,}")
print(f"months      : {len(months)}  ({min(months)} to {max(months)})")
print(f"chapters    : {len(chapters)}")
print(f"partners    : {len(partners)}")
print("\ntotal US imports per month, sanity check (expect ~$200-300B):")
for ym in sorted(val_by_month)[:2]+sorted(val_by_month)[-3:]:
    print(f"  {ym}  ${val_by_month[ym]/1e9:,.0f}B")
print(f"\npanel written: {OUTCSV}  ({os.path.getsize(OUTCSV)/1e6:.0f} MB)")
