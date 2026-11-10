import struct
mods = ["main", "subsdk0", "sdk"]
base = "D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/"
for m in mods:
    d = open(base + m, "rb").read()
    magic = d[0:4]; flags = struct.unpack("<I", d[12:16])[0]
    print("===", m, magic, "flags", hex(flags))
    for key in [b"FindInt32", b"csd-", b"9MediaData", b"MediaData8"]:
        n = 0; i = d.find(key)
        while i >= 0 and n < 4:
            print("  ", key.decode(), "at", i, repr(d[max(0,i-24):i+44]))
            n += 1; i = d.find(key, i + 1)
        if n == 0: print("  ", key.decode(), "ABSENT")