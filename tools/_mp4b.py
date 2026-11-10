import struct
p = "D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/movie.mp4"
d = open(p, "rb").read()
avc1 = 457
print("avc1 children:")
off = avc1 + 8 + 78
end = avc1 + 204
avcc = None
while off + 8 <= end:
    n, t = struct.unpack(">I4s", d[off:off+8])
    t = t.decode("latin1")
    print("  ", t, "size", n)
    if t == "avcC": avcc = d[off+8:off+n]
    off += n
print("avcC", len(avcc), "bytes:", avcc[:24].hex())
v = avcc
ln = (v[4] & 3) + 1
nsps = v[5] & 31
print("lengthSize", ln, "numSPS", nsps)
o = 6
for i in range(nsps):
    l = struct.unpack(">H", v[o:o+2])[0]; o += 2
    print("  SPS", l, "bytes head:", v[o:o+8].hex())
    o += l
npps = v[o]; o += 1
print("numPPS", npps)
for i in range(npps):
    l = struct.unpack(">H", v[o:o+2])[0]; o += 2
    print("  PPS", l, "bytes:", v[o:o+l].hex())
    o += l