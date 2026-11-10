import struct
P = "D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/movie.mp4"
d = open(P, "rb").read()
def box(off):
    n = struct.unpack(">I", d[off:off+4])[0]
    return n, d[off+4:off+8].decode("latin1")
def children(off, end=None):
    n, t = box(off)
    if end is None: end = off + n
    out = {}; po = off + 8
    while po + 8 <= end:
        n2, t2 = box(po)
        if n2 < 8: break
        out.setdefault(t2, []).append(po); po += n2
    return out
moov = 32
traks = children(moov)["trak"]
t0 = traks[1]
md = children(t0)["mdia"][0]
minf = children(md)["minf"][0]
stbl = children(minf)["stbl"][0]
st = children(stbl)
sd = st["stsd"][0]
e0 = sd + 16
n0, t0c = box(e0)
entry = d[e0:e0+n0]
print("mp4a entry hex:", entry.hex())
# audio sample table
sz = st["stsz"][0]; co = st["stco"][0]; sc = st["stsc"][0]
ssz_n = struct.unpack(">I", d[sz+12:sz+16])[0]
ssz_c = struct.unpack(">I", d[sz+16:sz+20])[0]
sco_c = struct.unpack(">I", d[co+12:co+16])[0]
print("audio samples", ssz_c, "const size", ssz_n, "chunks", sco_c)
sizes = []
if ssz_n:
    sizes = [ssz_n]*ssz_c
else:
    for i in range(ssz_c):
        sizes.append(struct.unpack(">I", d[sz+20+4*i:sz+24+4*i])[0])
offs = []
for i in range(sco_c):
    offs.append(struct.unpack(">I", d[co+16+4*i:co+20+4*i])[0])
print("first chunk off", offs[0], "first sizes", sizes[:6], "sum", sum(sizes))
o = offs[0]
print("sample0 head:", d[o:o+24].hex())
print("sample1 head:", d[offs[0]+sizes[0]:offs[0]+sizes[0]+24].hex())
# stts
ts = st["stts"][0]
n_ent = struct.unpack(">I", d[ts+12:ts+16])[0]
print("stts entries", n_ent)
for i in range(min(n_ent,4)):
    c, dur = struct.unpack(">II", d[ts+16+8*i:ts+24+8*i])
    print("  count", c, "delta", dur, "->", 256000000/dur/256 if dur else 0)
