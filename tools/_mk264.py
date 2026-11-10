import struct
d = open("D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/movie.mp4","rb").read()
def boxes(b, s, e):
    i = s
    while i + 8 <= e:
        n = struct.unpack(">I", b[i:i+4])[0]; typ = b[i+4:i+8]
        if n < 8: break
        yield typ, i+8, i+n
        i += n
def find(b, s, e, path):
    for typ, s2, e2 in boxes(b, s, e):
        if typ == path[0]:
            if len(path) == 1: return (s2, e2)
            r = find(b, s2, e2, path[1:])
            if r: return r
    return None
moov = find(d, 0, len(d), [b"moov"])
trak = find(d, moov[0], moov[1], [b"trak"])
stbl = find(d, trak[0], trak[1], [b"mdia", b"minf", b"stbl"])
S = {}
for typ, s, e in boxes(d, stbl[0], stbl[1]): S[typ] = (s, e)
print("stbl boxes", [k.decode() for k in S])
s, e = S[b"stsz"]; p = d[s:e]
cnt = struct.unpack(">I", p[8:12])[0]
unit = struct.unpack(">I", p[4:8])[0]
sizes = [unit]*cnt if unit else [struct.unpack(">I", p[12+4*i:16+4*i])[0] for i in range(cnt)]
key = b"stco" if b"stco" in S else b"co64"
s, e = S[key]; p = d[s:e]
nch = struct.unpack(">I", p[4:8])[0]
w = 4 if key == b"stco" else 8
fmt = ">I" if w == 4 else ">Q"
offs = [struct.unpack(fmt, p[8+w*i:8+w*(i+1)])[0] for i in range(nch)]
print("samples", cnt, "chunks", nch, "sizes0", sizes[:4], "offs0", offs[:3])
out = bytearray(); tot = 0
n = min(cnt, len(offs), 30)
for i in range(n):
    s0 = d[offs[i]:offs[i]+sizes[i]]
    j = 0
    while j + 4 <= len(s0):
        m = struct.unpack(">I", s0[j:j+4])[0]; j += 4
        if m == 0 or j + m > len(s0): break
        out += b"\x00\x00\x00\x01" + s0[j:j+m]; j += m; tot += 1
open("D:/consoles/ns/hayarigami-recomp/build/v0/test.264","wb").write(bytes(out))
print("annexb", len(out), "nals", tot)