import struct
p = "D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/movie.mp4"
d = open(p, "rb").read()
def full(box_off): return struct.unpack(">I", d[box_off+8:box_off+12])[0]
stbls = []
off = 0
moov = d.find(b"moov", 0)
print("moov at", moov)
pos = moov + 8
mend = moov + struct.unpack(">I", d[moov:moov+4])[0]
while pos + 8 <= mend:
    n = struct.unpack(">I", d[pos:pos+4])[0]; t = d[pos+4:pos+8]
    if t == b"trak": stbls.append(pos)
    pos += n
print("trak count", len(stbls))
def sub(box, path):
    t0, n0 = box; end = t0 + n0; out = {}
    po = t0 + 8
    while po + 8 <= end:
        n = struct.unpack(">I", d[po:po+4])[0]; t = d[po+4:po+8].decode("latin1")
        out[t] = po
        if t in path: return po
        po += n
    return None
vt = None
for t0 in stbls:
    n0 = struct.unpack(">I", d[t0:t0+4])[0]
    mdia = sub((t0, n0), ["mdia"])
    print("trak", t0, "mdia", mdia)