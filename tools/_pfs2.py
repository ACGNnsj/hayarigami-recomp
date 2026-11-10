import struct, hashlib
def parse(p):
    d = open(p, "rb").read()
    recs = []
    off = 0x10
    while off + 0x40 <= len(d):
        f1, f2 = struct.unpack_from("<QQ", d, off - 0x10)
        name = d[off:off+32].split(b"\x00")[0]
        if not name or not all(32 <= c < 127 for c in name):
            break
        recs.append((name.decode(), f2, f1))   # name, offset, size
        off += 0x40
    return d, recs

base_p = r"D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/start.dat"
patch_p = r"D:/consoles/ns/010095B01AF94000/RomFs/FOAF1/start.dat"
db, rb = parse(base_p)
dp, rp = parse(patch_p)
print("records", len(rb), len(rp))
bd = {n: (o, s) for n, o, s in rb}
pd_ = {n: (o, s) for n, o, s in rp}
changed = []
for n in bd:
    if n in pd_ and (bd[n][1] != pd_[n][1] or db[bd[n][0]:bd[n][0]+bd[n][1]] != dp[pd_[n][0]:pd_[n][0]+pd_[n][1]]):
        changed.append(n)
print("changed entries:", len(changed))
for n in changed[:40]:
    print("  ", n, "base", bd[n][1], "patch", pd_[n][1])
print("fonts base/patch:")
for n in bd:
    if n.startswith("font"):
        print("  ", n, bd[n][1], pd_.get(n, (0,0))[1])
