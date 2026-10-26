"""Prints which catalogue parts match given words (shown as build notes)."""
import re, sys, zipfile
words = [w.lower() for w in sys.argv[2:]]
z = zipfile.ZipFile(sys.argv[1])
hits = {w: [] for w in words}
for info in z.infolist():
    n = info.filename.lower()
    m = re.fullmatch(r"ldraw/parts/([^/]+)\.dat", n)
    if not m:
        continue
    lines = z.read(info).decode("utf-8", "ignore").splitlines()
    if not lines:
        continue
    desc = re.sub(r"\s+", " ", lines[0][1:].strip())
    if not desc or desc[0] in "~=_|" or "moved to" in desc.lower():
        continue
    for w in words:
        if w in desc.lower():
            hits[w].append(f"{m.group(1)} {desc}")
for w, lst in hits.items():
    lst.sort(key=len)
    print(f"::notice title={w} ({len(lst)})::" + " | ".join(lst[:40]))
