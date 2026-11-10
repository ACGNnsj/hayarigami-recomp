import struct, re, sys, os
def parse(p):
    d = open(p, "rb").read()
    recs = {}
    off = 0x10
    while off + 0x40 <= len(d):
        f1, f2 = struct.unpack_from("<QQ", d, off - 0x10)
        name = d[off:off+32].split(b"\x00")[0]
        if not name or not all(32 <= c < 127 for c in name):
            break
        recs[name.decode()] = (f2, f1)
        off += 0x40
    return d, recs

pairs = {"base": r"D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/start.dat",
         "patch": r"D:/consoles/ns/010095B01AF94000/RomFs/FOAF1/start.dat"}
out = {}
for tag, p in pairs.items():
    d, recs = parse(p)
    for n in ("sys1.nltx", "selecter1.nltx", "story1.dat"):
        o, s = recs[n]
        b = d[o:o+s]
        out[(tag, n)] = b

def scan(b):
    res = {}
    # utf-16le japanese/chinese
    try:
        t16 = b.decode("utf-16-le", "ignore")
    except Exception:
        t16 = ""
    res["u16_cn"] = sum(t16.count(c) for c in "这说们时个国为发后里")
    res["u16_kana"] = sum(t16.count(c) for c in "あいうえおかきくけこさしすせそたちつてとなにぬねの")
    try:
        t8 = b.decode("utf-8", "ignore")
    except Exception:
        t8 = ""
    res["u8_cn"] = sum(t8.count(c) for c in "这说们时个国为发后里")
    res["u8_kana"] = sum(t8.count(c) for c in "あいうえおかきくけこ")
    try:
        ts = b.decode("shift_jis", "ignore")
    except Exception:
        ts = ""
    res["sjis_kana"] = sum(ts.count(c) for c in "あいうえおかきくけこ")
    res["sjis_cn"] = sum(ts.count(c) for c in "这说们时个")
    return res

for k, b in out.items():
    print(k, "bytes", len(b), scan(b))
    print("   head:", b[:64].hex())
