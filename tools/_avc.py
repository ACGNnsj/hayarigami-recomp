import struct, hashlib
base = "D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/"
for name in ["FOAF1", "FOAF2", "FOAF3"]:
    d = open(base + name + "/movie.mp4", "rb").read()
    i = d.find(b"avcC")
    if i < 0: print(name, "no avcC"); continue
    n = struct.unpack(">I", d[i-4:i])[0]
    rec = d[i+4:i-4+n]
    print(name, "avcC", len(rec), "sha8", hashlib.sha256(rec).hexdigest()[:8], rec[:12].hex())