"""Pull HTS chapter 99 from USITC: the surcharge codes and the notes that list covered products.

Two artifacts:
  coverage/raw/hts99_codes.json  680 surcharge codes with rate and description
  coverage/raw/hts99_notes.txt   the chapter 99 publication as text, which carries the U.S. notes
"""
import os, json, urllib.request, subprocess

OUT = "coverage/raw"
CODES = f"{OUT}/hts99_codes.json"
PDF   = f"{OUT}/hts99.pdf"
NOTES = f"{OUT}/hts99_notes.txt"

def get(url, path, label):
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        print(f"  {label:<24} cached ({os.path.getsize(path)/1e6:.1f} MB)")
        return
    with urllib.request.urlopen(url, timeout=180) as r:
        open(path, "wb").write(r.read())
    print(f"  {label:<24} fetched ({os.path.getsize(path)/1e6:.1f} MB)")

os.makedirs(OUT, exist_ok=True)
get("https://hts.usitc.gov/reststop/exportList?from=9903.00.00&to=9903.99.99&format=JSON&styles=false",
    CODES, "surcharge codes")
get("https://hts.usitc.gov/reststop/file?release=currentRelease&filename=Chapter%2099",
    PDF, "chapter 99 publication")

if not (os.path.exists(NOTES) and os.path.getsize(NOTES) > 10000):
    subprocess.run(["pdftotext", "-layout", PDF, NOTES], check=True)
print(f"  {'notes text':<24} {os.path.getsize(NOTES)/1e6:.1f} MB")

codes = json.load(open(CODES))
print(f"\n{len(codes)} surcharge codes, {sum(1 for c in codes if c.get('general'))} with a stated rate")
