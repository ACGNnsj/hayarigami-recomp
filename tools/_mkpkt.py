import struct, hashlib
d = open("D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/movie.mp4","rb").read()
i = d.find(b"avcC")
n = struct.unpack(">I", d[i-4:i])[0]
rec = d[i+4:i-4+n]
out = bytearray(); k = rec[5] & 31; p = 6
for _ in range(k):
    ln = struct.unpack(">H", rec[p:p+2])[0]; p += 2
    out += b"\x00\x00\x00\x01" + rec[p:p+ln]; p += ln
np = rec[p]; p += 1
for _ in range(np):
    ln = struct.unpack(">H", rec[p:p+2])[0]; p += 2
    out += b"\x00\x00\x00\x01" + rec[p:p+ln]; p += ln
open("D:/consoles/ns/hayarigami-recomp/build/v0/spspps.bin","wb").write(bytes(out))
print("spspps", len(out), hashlib.sha256(bytes(out)).hexdigest()[:8], bytes(out).hex())
def boxes(b, s, e):
    i = s
    while i + 8 <= e:
        m = struct.unpack(">I", b[i:i+4])[0]; typ = b[i+4:i+8]
        if m < 8: break
        yield typ, i+8, i+m
        i += m
def find(b, s, e, path):
    for typ, s2, e2 in boxes(b, s, e):
        if typ == path[0]:
            if len(path) == 1: return (s2, e2)
            r = find(b, s2, e2, path[1:])
            if r: return r
    return None
moov = find(d,0,len(d),[b"moov"]); trak = find(d,moov[0],moov[1],[b"trak"])
stbl = find(d,trak[0],trak[1],[b"mdia",b"minf",b"stbl"])
S = {t: (s, e) for t, s, e in boxes(d, stbl[0], stbl[1])}
s,e = S[b"stsz"]; p = d[s:e]; cnt = struct.unpack(">I", p[8:12])[0]; unit = struct.unpack(">I", p[4:8])[0]
sizes = [unit]*cnt if unit else [struct.unpack(">I", p[12+4*i:16+4*i])[0] for i in range(cnt)]
s,e = S[b"stco"]; p = d[s:e]; nch = struct.unpack(">I", p[4:8])[0]
offs = [struct.unpack(">I", p[8+4*i:12+4*i])[0] for i in range(nch)]
pk = bytearray()
for i in range(40):
    s0 = d[offs[i]:offs[i]+sizes[i]]
    pk += struct.pack(">I", len(s0)) + s0
open("D:/consoles/ns/hayarigami-recomp/build/v0/packets.bin","wb").write(bytes(pk))
print("packets", len(pk))