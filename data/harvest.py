"""Census intltrade imports monthly panel, HS2 x partner, 2015 onward.
One API call per month; each month checkpointed to its own gzip so a
restart skips what is already on disk."""
import json,urllib.request,os,time,gzip,sys
K=os.environ["CK"]
B="https://api.census.gov/data/timeseries/intltrade/imports/hs"
F="CTY_CODE,CTY_NAME,I_COMMODITY,GEN_VAL_MO,AIR_WGT_MO,VES_WGT_MO,CNT_WGT_MO,SUMMARY_LVL"
OUT="panel/raw"

def month(y,m,tries=3):
    p=f"{OUT}/{y}-{m:02d}.json.gz"
    if os.path.exists(p) and os.path.getsize(p)>2000: return "skip",0
    q=f"{B}?get={F}&YEAR={y}&MONTH={m:02d}&COMM_LVL=HS2&I_COMMODITY=*&CTY_CODE=*&key={K}"
    for t in range(tries):
        try:
            raw=urllib.request.urlopen(q,timeout=420).read()
            d=json.loads(raw.decode())
            if len(d)<50: return "empty",0
            with gzip.open(p,"wt") as f: json.dump(d,f)
            return "ok",len(d)-1
        except Exception as e:
            if t==tries-1: return f"err {str(e)[:40]}",0
            time.sleep(10+10*t)

tot=0; done=0
for y in range(2015,2027):
    for m in range(1,13):
        st,n=month(y,m)
        if st=="ok":
            tot+=n; done+=1
            print(f"{y}-{m:02d}  {n:>7,} rows   (cumulative {tot:,})",flush=True)
        elif st=="skip":
            print(f"{y}-{m:02d}  cached",flush=True)
        elif st=="empty":
            print(f"{y}-{m:02d}  no data yet, stopping",flush=True); sys.exit(0)
        else:
            print(f"{y}-{m:02d}  {st}",flush=True)
        time.sleep(1)
print(f"\nDONE: {done} months fetched, {tot:,} rows")
