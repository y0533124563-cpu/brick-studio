"""Downloads the LDraw parts library into web/ldraw and builds web/ldraw/index.json.

The LDraw Parts Library is © LDraw.org contributors, licensed CC BY 2.0.
File names are lowercased so the website (case-sensitive) can find them.
"""
import io, json, os, re, sys, urllib.request, zipfile

URL = "https://library.ldraw.org/library/updates/complete.zip"
ZIP = sys.argv[1] if len(sys.argv) > 1 else "ldraw-complete.zip"
OUT = "web/ldraw"

if not os.path.exists(ZIP):
    print("Downloading", URL)
    req = urllib.request.Request(URL, headers={"User-Agent": "brick-studio-build"})
    with urllib.request.urlopen(req, timeout=600) as r, open(ZIP, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
print("Zip size MB:", os.path.getsize(ZIP) // (1 << 20))

index = []
count = 0
with zipfile.ZipFile(ZIP) as z:
    for info in z.infolist():
        if info.is_dir():
            continue
        name = info.filename.replace("\\", "/")
        low = name.lower()
        if low.startswith("ldraw/"):
            low = low[6:]
        if not (low.startswith("parts/") or low.startswith("p/") or low == "ldconfig.ldr"):
            continue
        data = z.read(info)
        dest = os.path.join(OUT, low)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        count += 1

        # catalogue entry for top-level parts only
        m = re.fullmatch(r"parts/([^/]+)\.dat", low)
        if not m:
            continue
        text = data.decode("utf-8", errors="ignore").splitlines()
        if not text:
            continue
        desc = text[0].strip()
        desc = desc[1:].strip() if desc.startswith("0") else desc
        desc = re.sub(r"\s+", " ", desc)
        if not desc or desc[0] in "~=_|" or "moved to" in desc.lower():
            continue
        ok, cat = True, None
        for line in text[1:40]:
            t = line.split()
            if len(t) >= 3 and t[0] == "0" and t[1] == "!LDRAW_ORG":
                kind = t[2]
                if kind not in ("Part", "Shortcut") or (len(t) > 3 and t[3] in ("Alias", "Physical_Colour")):
                    ok = False
            if len(t) >= 3 and t[0] == "0" and t[1] == "!CATEGORY":
                cat = " ".join(t[2:])
        if not ok:
            continue
        if not cat:
            cat = desc.split(" ")[0]
        index.append([m.group(1), desc, cat])

def natural(e):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", e[0])]

index.sort(key=natural)
with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
print(f"Wrote {count} files, {len(index)} parts in catalogue")
