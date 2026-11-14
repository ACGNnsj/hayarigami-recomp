import struct
p = "D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/movie.mp4"
d = open(p, "rb").read()
def children(off):
    n = struct.unpack(">I", d[off:off+4])[0]; end = off + n; out = {}
    po = off + 8
    while po + 8 <= end:
        n2 = struct.unpack(">I", d[po:po+4])[0]; t2 = d[po+4:po+8].decode("latin1")
        out.setdefault(t2, []).append(po)
        po += n2
    return out
moov = 32
traks = children(moov)["trak"]
vt = None
for t0 in traks:
    md = children(t0)["mdia"][0]; mi = children(md)["minf"][0]; stb = children(mi)["stbl"][0]
    st = children(stb)
    names = sorted(st.keys())
    has_avc = (t0 == traks[0])
    print("trak", t0, "avc1" if has_avc else "audio", [k for k in names])
    if has_avc: vt = st
sz = vt["stsz"][0]; co = vt["stco"][0]; sc = vt["stsc"][0]
ssz_n = struct.unpack(">I", d[sz+12:sz+16])[0]; ssz_c = struct.unpack(">I", d[sz+16:sz+20])[0]
sco_c = struct.unpack(">I", d[co+12:co+16])[0]
ssc_c = struct.unpack(">I", d[sc+12:sc+16])[0]
print("samples", ssz_c, "sample_size_field", ssz_n, "chunks", sco_c, "runs", ssc_c)
first_off = struct.unpack(">I", d[co+16:co+20])[0]
first_sz = struct.unpack(">I", d[sz+20:sz+24])[0] if ssz_n == 0 else ssz_n
print("sample0 off", first_off, "size", first_sz)
s = d[first_off:first_off+first_sz]
print("sample0 head", s[:16].hex())
o = 0; nals = []
while o + 4 <= len(s) and len(nals) < 12:
    ln = struct.unpack(">I", s[o:o+4])[0]; o += 4
    if o >= len(s) or ln > len(s): nals.append(("BAD", ln)); break
    nals.append((s[o] & 31, ln))
    o += ln
print("length-prefixed NALs:", nals)
offs = []
i = 0
while i + 2 < len(s) and len(offs) < 64:
    if s[i] == 0 and s[i+1] == 0 and s[i+2] == 1: offs.append(i); i += 2
    i += 1
print("annexB start codes:", len(offs))