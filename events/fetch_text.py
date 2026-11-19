"""Fill events/raw/ with full text for every indexed document. Concurrent, checkpointed."""
import json, os, urllib.request
from concurrent.futures import ThreadPoolExecutor

OUT = "events/raw"
docs = json.load(open("events/fr_index.json"))
todo = [d for d in docs
        if d.get("raw_text_url")
        and not (os.path.exists(f"{OUT}/{d['document_number']}.txt")
                 and os.path.getsize(f"{OUT}/{d['document_number']}.txt") > 200)]
print(f"{len(docs)} indexed, {len(docs)-len(todo)} already cached, {len(todo)} to fetch")

def one(d):
    p = f"{OUT}/{d['document_number']}.txt"
    for _ in range(3):
        try:
            with urllib.request.urlopen(d["raw_text_url"], timeout=40) as r:
                body = r.read()
            if len(body) > 200:
                tmp = p + ".part"; open(tmp, "wb").write(body); os.replace(tmp, p)
                return True
        except Exception:
            pass
    return False

with ThreadPoolExecutor(max_workers=10) as ex:
    res = list(ex.map(one, todo))
print(f"fetched {sum(res)}, failed {len(res)-sum(res)}")
print(f"cache now holds {len(os.listdir(OUT))} files")
