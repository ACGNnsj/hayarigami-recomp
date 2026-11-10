import os
files = {
 "base_foaf1": r"D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/start.dat",
 "patch_foaf1": r"D:/consoles/ns/010095B01AF94000/RomFs/FOAF1/start.dat",
}
cn = {"这":"\u8fd9".encode(), "说":"\u8bf4".encode(), "们":"\u4eec".encode(), "时":"\u65f6".encode()}
jp = {"の":b"\x82\xcc", "です":b"\x82\xc5\x82\xb7"}
for name, p in files.items():
    d = open(p,"rb").read(120_000_000)
    print(name, len(d))
    for k,v in cn.items():
        print("  utf8", k, d.count(v))
    for k,v in jp.items():
        print("  sjis", k, d.count(v))
    # ascii word samples
    import re
    words = re.findall(rb"[A-Za-z_][A-Za-z0-9_./]{4,30}", d[:400000])
    print("  sample ascii:", [w.decode('latin1') for w in words[:12]])
