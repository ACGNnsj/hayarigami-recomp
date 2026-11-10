import os, hashlib, sys
UP = r"D:/consoles/ns/010095B01AF94000/RomFs"
BASE = r"D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree"
OUT = r"D:/consoles/ns/hayarigami-recomp/build/patch-tree"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

os.makedirs(OUT, exist_ok=True)
lines = []
missing = []
for root, dirs, files in os.walk(UP):
    for fn in files:
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, UP).replace("\\", "/")
        bp = os.path.join(BASE, rel)
        if not os.path.exists(bp):
            missing.append((rel, "no original"))
            continue
        s_new = sha(p)
        s_old = sha(bp)
        size = os.path.getsize(p)
        if s_new == s_old:
            print("same:", rel)
            continue
        lines.append("%s\t%d\t%s\t%s" % (rel, size, s_new, s_old))
        print("overlay:", rel, size)
print("missing:", missing)
if lines:
    open(os.path.join(OUT, "manifest.tsv"), "w", newline="\n").write("\n".join(lines) + "\n")
print("manifest lines:", len(lines))
