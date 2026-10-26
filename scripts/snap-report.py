"""Prints the connection summary of chosen parts (as build notes)."""
import json, os, sys
d = sys.argv[1]
idx = {n: desc for n, desc, _ in json.load(open(os.path.join(d, "index.json")))}
for num in sys.argv[2:]:
    p = os.path.join(d, "snap", num + ".json")
    if not os.path.exists(p):
        print(f"::notice title={num}::{idx.get(num, '?')} - NO DATA"); continue
    recs = json.load(open(p))
    summ = {}
    for r in recs:
        k = f"{r[0]}-{r[3][0]}{r[3][1]:g}-{r[1]}"
        summ[k] = summ.get(k, 0) + 1
    print(f"::notice title={num}::{idx.get(num, '?')} - " + ", ".join(f"{k}x{v}" for k, v in sorted(summ.items())))
