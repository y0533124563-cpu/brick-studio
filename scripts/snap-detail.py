"""Prints every connection of chosen parts with position (LDraw units)."""
import json, os, sys
d = sys.argv[1]
for num in sys.argv[2:]:
    p = os.path.join(d, "snap", num + ".json")
    if not os.path.exists(p):
        print(f"::notice title={num}::NO DATA"); continue
    out = []
    for r in json.load(open(p)):
        out.append(f"{r[0]} {r[1]} secs={r[3]} S=({r[4]},{r[5]},{r[6]}) D=({r[7]},{r[8]},{r[9]}) L={r[13]}")
    print(f"::notice title={num} ({len(out)})::" + " | ".join(out[:12]))
    first = open(os.path.join(d, "parts", num + ".dat"), errors="ignore").read().splitlines()[:12]
    print(f"::notice title={num} file::" + " | ".join(first))
