"""Census intltrade imports, HS10 x partner x month, 2015 onward.

HS10 is the finest published level and nests exactly under the HS8 lines the
tariff orders are written at, so product matching is exact rather than
approximate. GEN_QY1_MO is carried because it is only populated at this level
and, unlike the weight fields, it counts truck and rail arrivals.

One API call per month, each checkpointed to its own gzip, so a restart skips
whatever is already on disk. Written atomically via .tmp + os.replace so an
interrupted run never leaves a half file that looks cached.

Usage:  CK=<census key> python3 harvest_hs10.py
"""
import json, urllib.request, urllib.error, os, time, gzip, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

K = os.environ["CK"]
B = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
F = ("CTY_CODE,CTY_NAME,I_COMMODITY,GEN_VAL_MO,GEN_QY1_MO,UNIT_QY1,"
     "AIR_WGT_MO,VES_WGT_MO,CNT_WGT_MO,SUMMARY_LVL")
OUT = "panel/hs10"
WORKERS = 4
MIN_GZ = 500_000          # a real month gzips to ~7MB; anything smaller is suspect

MONTHS = [(y, m) for y in range(2015, 2027) for m in range(1, 13)]
MONTHS = [(y, m) for (y, m) in MONTHS if (y, m) <= (2026, 9)]


def fetch(y, m, tries=4):
    p = f"{OUT}/{y}-{m:02d}.json.gz"
    if os.path.exists(p) and os.path.getsize(p) > MIN_GZ:
        return y, m, "cached", 0
    q = (f"{B}?get={F}&YEAR={y}&MONTH={m:02d}&COMM_LVL=HS10"
         f"&I_COMMODITY=*&CTY_CODE=*&key={K}")
    for t in range(tries):
        try:
            resp = urllib.request.urlopen(q, timeout=900)
            raw = resp.read()
            # a month that is not published yet comes back 204 with an empty body,
            # which urllib reports as success; without this it fails as a JSON error
            if resp.status == 204 or not raw.strip():
                return y, m, "not published yet", 0
            d = json.loads(raw.decode())
            if len(d) < 50:
                return y, m, "empty", 0
            tmp = p + ".tmp"
            with gzip.open(tmp, "wt") as f:
                json.dump(d, f)
            os.replace(tmp, p)
            return y, m, "ok", len(d) - 1
        except urllib.error.HTTPError as e:
            if e.code == 204:                     # no data published for this month
                return y, m, "empty", 0
            if t == tries - 1:
                return y, m, f"http {e.code}", 0
            time.sleep(20 + 30 * t)
        except Exception as e:
            if t == tries - 1:
                return y, m, f"err {type(e).__name__}: {str(e)[:60]}", 0
            time.sleep(20 + 30 * t)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    tot = done = 0
    bad = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(fetch, y, m): (y, m) for y, m in MONTHS}
        for i, fu in enumerate(as_completed(futs), 1):
            y, m, st, n = fu.result()
            if st == "ok":
                tot += n
                done += 1
            elif st not in ("cached", "empty", "not published yet"):
                bad.append((y, m, st))
            el = time.time() - t0
            print(f"[{i:>3}/{len(MONTHS)}] {y}-{m:02d}  {st:<28} "
                  f"{n:>8,} rows   cum {tot:>11,}   {el/60:5.1f} min",
                  flush=True)

    print(f"\nfetched {done} months, {tot:,} new rows, "
          f"{(time.time()-t0)/60:.1f} min")
    on_disk = sorted(f for f in os.listdir(OUT) if f.endswith(".json.gz"))
    mb = sum(os.path.getsize(f"{OUT}/{f}") for f in on_disk) / 1e6
    print(f"on disk: {len(on_disk)} months, {mb:,.0f} MB")
    if bad:
        print(f"\nFAILED ({len(bad)}), rerun to retry:")
        for y, m, st in sorted(bad):
            print(f"  {y}-{m:02d}  {st}")
        sys.exit(1)
