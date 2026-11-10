import struct, sys, hashlib
def parse(p):
    d = open(p, "rb").read()
    assert d[:9] == b"PS_FS_V1:"
    recs = []
    off = 0x10
    while off + 0x40 <= len(d):
        f1, f2 = struct.unpack_from("<QQ", d, off - 0x10)
        name = d[off:off+32].split(b"\x00")[0]
        if not name or not all(32 <= c < 127 for c in name):
            break
        recs.append((name.decode(), f1, f2))
        off += 0x40
    return d, recs

for tag, p in (("base", "D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/start.dat"),
               ("patch", "D:/consoles/ns/hayarigami-recomp/ns/010095B01AF94000/RomFs/FOAF1/start.dat".replace("/ns/","/"))):
    pass

pairs = [("base", r"D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/start.dat"),
         ("patch", r"D:/consoles/ns/010095B01AF94000/RomFs/FOAF1/start.dat")]
for tag, p in pairs:
    d, recs = parse(p)
    print(tag, "size", len(d), "records", len(recs), "table end ~", 0x10 + 0x40*len(recs))
    for name, f1, f2 in recs[:6]:
        print("   ", name, f1, f2)
