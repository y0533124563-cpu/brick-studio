#!/usr/bin/env python3
"""Map the numbers printed in building-instruction booklets (element IDs, e.g. 6099714)
to an LDraw part number and LDraw colour, using the free Rebrickable data downloads.
Writes web/ldraw/elements.json as {"element id": ["ldraw part", ldraw colour code or -1]}.
Usage: get-elements.py <web/ldraw>"""
import csv, gzip, io, json, os, re, sys, urllib.request

LD = sys.argv[1]
BASE = 'https://cdn.rebrickable.com/media/downloads/'

def fetch(name):
    req = urllib.request.Request(BASE + name, headers={'User-Agent': 'brick-studio-build'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return list(csv.DictReader(io.StringIO(gzip.decompress(r.read()).decode('utf-8'))))

try:
    elements = fetch('elements.csv.gz')
    colors = fetch('colors.csv.gz')
except Exception as e:
    print(f'::warning title=Element numbers::could not download Rebrickable data ({e}); booklet numbers will not be searchable')
    sys.exit(0)

# LDraw parts we actually have
index = json.load(open(os.path.join(LD, 'index.json')))
have = {str(e[0]).lower(): str(e[0]) for e in index}

def to_ld(*names):
    for n in names:
        if not n:
            continue
        n = n.lower()
        if n in have:
            return have[n]
        # printed / patterned / assembly variants: fall back to the plain part
        for pat in (r'(pr|pat|pb|px|ps|pt)\d.*$', r'c\d+.*$', r'-f\d.*$', r'[a-z]+$'):
            m = re.sub(pat, '', n)
            if m != n and m in have:
                return have[m]
        for suf in 'abcd':
            if n + suf in have:
                return have[n + suf]
    return None

# LDraw colours (code -> rgb) from ldconfig
ldc = {}
for line in open(os.path.join(LD, 'ldconfig.ldr'), encoding='utf-8', errors='ignore'):
    m = re.match(r'^0\s+!COLOUR\s+(\S+)\s+CODE\s+(\d+)\s+VALUE\s+#([0-9A-Fa-f]{6})(.*)$', line)
    if m:
        ldc[int(m.group(2))] = (m.group(3).upper(), 'ALPHA' in m.group(4))
by_rgb = {}
for code, (rgb, tr) in ldc.items():
    by_rgb.setdefault((rgb, tr), code)

col = {}
for c in colors:
    try:
        cid = int(c['id'])
    except (ValueError, KeyError):
        continue
    rgb, tr = (c.get('rgb') or '').upper(), (c.get('is_trans') or '').lower() in ('t', 'true', '1')
    if cid in ldc and ldc[cid] == (rgb, tr):
        col[cid] = cid            # same number in both systems
    elif (rgb, tr) in by_rgb:
        col[cid] = by_rgb[(rgb, tr)]
    elif cid in ldc:
        col[cid] = cid

out, miss = {}, 0
for e in elements:
    eid = (e.get('element_id') or '').strip()
    if not eid.isdigit():
        continue
    part = to_ld(e.get('part_num'), e.get('design_id'))
    if not part:
        miss += 1
        continue
    try:
        cc = col.get(int(e.get('color_id')), -1)
    except (TypeError, ValueError):
        cc = -1
    out[eid] = [part, cc]

json.dump(out, open(os.path.join(LD, 'elements.json'), 'w'), separators=(',', ':'))
print(f'::notice title=Element numbers::{len(out)} booklet numbers mapped to parts ({miss} without a 3D part)')
for t in ('6099714', '4211815', '302324', '6135494', '4583862', '303401'):
    print(f'::notice title=Element {t}::{out.get(t)}')
