"""Builds web/ldraw/snap/<part>.json: the real connection points of every LDraw part.

Connection data comes from the LDCad Shadow Library by Roland Melkert and contributors
(https://github.com/RolandMelkert/LDCadShadowLibrary), licensed CC BY-SA 4.0.
The generated snap files are shared under the same licence.

Each output record (LDraw units, part coordinates):
  [gender, caps, slide, [shape, radius, length, ...], Sx,Sy,Sz, Dx,Dy,Dz, Ux,Uy,Uz, length]
S is where the connection starts, D the direction it runs, U a reference direction across it.
"""
import json, math, os, re, sys

LD = sys.argv[1] if len(sys.argv) > 1 else "web/ldraw"
SH = sys.argv[2] if len(sys.argv) > 2 else "shadow"
OUT = os.path.join(LD, "snap")
os.makedirs(OUT, exist_ok=True)

# ---------- small 3x4 matrix helpers (row-major, implicit last row 0 0 0 1) ----------
I = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0)
def mul(A, B):
    r = []
    for i in range(3):
        a0, a1, a2, a3 = A[i*4:i*4+4]
        for j in range(4):
            v = a0*B[j] + a1*B[4+j] + a2*B[8+j]
            if j == 3:
                v += a3
            r.append(v)
    return tuple(r)
def mk(pos, ori):
    a, b, c, d, e, f, g, h, i = ori
    return (a, b, c, pos[0], d, e, f, pos[1], g, h, i, pos[2])
def apply(M, p):
    x, y, z = p
    return (M[0]*x+M[1]*y+M[2]*z+M[3], M[4]*x+M[5]*y+M[6]*z+M[7], M[8]*x+M[9]*y+M[10]*z+M[11])
def adir(M, p):
    x, y, z = p
    return (M[0]*x+M[1]*y+M[2]*z, M[4]*x+M[5]*y+M[6]*z, M[8]*x+M[9]*y+M[10]*z)
def norm(v):
    l = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    return (v[0]/l, v[1]/l, v[2]/l) if l > 1e-9 else None

# ---------- file lookup ----------
def index_tree(root):
    m = {}
    for base, _, files in os.walk(root):
        for fn in files:
            full = os.path.join(base, fn)
            m[os.path.relpath(full, root).replace(os.sep, "/").lower()] = full
    return m
LDF = index_tree(LD)
SHF = index_tree(SH)
def find(tree, name):
    n = name.lower().replace("\\", "/").strip()
    if n.startswith("s/"):
        opts = ["parts/" + n]
    elif n.startswith("48/") or n.startswith("8/"):
        opts = ["p/" + n]
    else:
        opts = ["parts/" + n, "p/" + n]
    for o in opts:
        if o in tree:
            return tree[o]
    return None
def read(path):
    if not path:
        return []
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read().splitlines()

PARAM = re.compile(r"\[(\w+)=([^\]]*)\]")
def params(line):
    return {k.lower(): v.strip() for k, v in PARAM.findall(line)}
def nums(s, n):
    try:
        v = [float(x) for x in s.split()]
        return v if len(v) == n else None
    except ValueError:
        return None
def grid_offsets(s):
    if not s:
        return [(0.0, 0.0)]
    t = s.split()
    try:
        i = 0
        cx = t[i] == "C"; i += cx
        nx = int(float(t[i])); i += 1
        cz = t[i] == "C"; i += cz
        nz = int(float(t[i])); i += 1
        sx = float(t[i]); sz = float(t[i+1])
    except (IndexError, ValueError):
        return [(0.0, 0.0)]
    xs = [((k - (nx-1)/2) if cx else k) * sx for k in range(nx)]
    zs = [((k - (nz-1)/2) if cz else k) * sz for k in range(nz)]
    return [(x, z) for x in xs for z in zs]
def snap_matrices(p):
    pos = nums(p.get("pos", ""), 3) or [0, 0, 0]
    ori = nums(p.get("ori", ""), 9) or [1, 0, 0, 0, 1, 0, 0, 0, 1]
    base = mk(pos, ori)
    return [mul(base, mk((gx, 0, gz), (1, 0, 0, 0, 1, 0, 0, 0, 1))) for gx, gz in grid_offsets(p.get("grid"))]

memo, busy = {}, set()
def resolve(name):
    key = name.lower().replace("\\", "/").strip()
    if key in memo:
        return memo[key]
    if key in busy:
        return []
    busy.add(key)
    snaps = []
    # 1) connections inherited from sub-files
    for line in read(find(LDF, key)):
        t = line.split()
        if len(t) >= 15 and t[0] == "1":
            try:
                v = [float(x) for x in t[2:14]]
            except ValueError:
                continue
            M = (v[3], v[4], v[5], v[0], v[6], v[7], v[8], v[1], v[9], v[10], v[11], v[2])
            for s in resolve(" ".join(t[14:])):
                snaps.append(dict(s, M=mul(M, s["M"])))
    # 2) this file's own shadow info, in order
    for line in read(find(SHF, key)):
        if not line.startswith("0 !LDCAD"):
            continue
        p = params(line)
        if "SNAP_CLEAR" in line:
            cid = p.get("id")
            snaps = [s for s in snaps if cid and s.get("id") != cid.lower()]
        elif "SNAP_CYL" in line:
            st = p.get("secs", "").split()
            secs = []
            for k in range(0, len(st) - 2, 3):
                try:
                    secs.append((st[k], float(st[k+1]), float(st[k+2])))
                except ValueError:
                    pass
            if not secs:
                continue
            for M in snap_matrices(p):
                snaps.append(dict(id=p.get("id", "").lower(), g=p.get("gender", "M").upper()[:1], caps=p.get("caps", "one").lower(),
                                  slide=p.get("slide", "false").lower() == "true", center=p.get("center", "false").lower() == "true",
                                  secs=secs, M=M))
        elif "SNAP_INCL" in line and p.get("ref"):
            child = resolve(p["ref"])
            for M in snap_matrices(p):
                for s in child:
                    snaps.append(dict(s, M=mul(M, s["M"])))
    busy.discard(key)
    memo[key] = snaps
    return snaps

def r(v, n):
    return round(v, n) + 0.0
def record(s):
    M = s["M"]
    ys = math.sqrt(M[1]**2 + M[5]**2 + M[9]**2)
    if ys < 1e-6:
        return None
    L = sum(x[2] for x in s["secs"])
    S = apply(M, (0, L/2 if s["center"] else 0, 0))
    D = norm(adir(M, (0, -1, 0)))
    U = norm(adir(M, (1, 0, 0)))
    if not D or not U:
        return None
    k = U[0]*D[0] + U[1]*D[1] + U[2]*D[2]
    U = norm((U[0]-k*D[0], U[1]-k*D[1], U[2]-k*D[2])) or norm(adir(M, (0, 0, 1)))
    if not U:
        return None
    secs = []
    for sh, rad, ln in s["secs"]:
        secs += [sh, r(rad, 2), r(ln*ys, 2)]
    return [s["g"], s["caps"], 1 if s["slide"] else 0, secs,
            r(S[0], 2), r(S[1], 2), r(S[2], 2), r(D[0], 4), r(D[1], 4), r(D[2], 4), r(U[0], 4), r(U[1], 4), r(U[2], 4), r(L*ys, 2)]

with open(os.path.join(LD, "index.json"), encoding="utf-8") as f:
    catalogue = json.load(f)
done = 0
for num, _, _ in catalogue:
    recs = [x for x in (record(s) for s in resolve(num + ".dat")) if x]
    if not recs:
        continue
    with open(os.path.join(OUT, num.lower() + ".json"), "w") as f:
        json.dump(recs[:6000], f, separators=(",", ":"))
    done += 1
print(f"Connection data written for {done} of {len(catalogue)} parts")
