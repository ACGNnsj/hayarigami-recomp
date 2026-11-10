import struct
p = "D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/movie.mp4"
d = open(p, "rb").read()
print("size", len(d))
def boxes(d, off, end, depth=0):
    out = []
    while off + 8 <= end:
        n, t = struct.unpack(">I4s", d[off:off+8])
        t = t.decode("latin1")
        if n == 1: n = struct.unpack(">Q", d[off+8:off+16])[0]; h = 16
        elif n == 0: n = end - off; h = 8
        else: h = 8
        out.append((depth, t, off, n))
        if t in ("moov", "trak", "mdia", "minf", "stbl", "edts", "dinf"):
            out += boxes(d, off + h, off + n, depth + 1)
        if t == "stsd" and depth > 0:
            out += boxes(d, off + h + 8, off + n, depth + 1)
        off += n
    return out
for depth, t, off, n in boxes(d, 0, len(d)):
    if t in ("avc1", "mp4a", "avcC", "esds", "mvhd", "tkhd"):
        print(" " * depth + t, "off", off, "size", n)