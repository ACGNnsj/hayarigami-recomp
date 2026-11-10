import json
MP4 = 'D:/consoles/ns/hayarigami-recomp/build/extracted/latest/romfs/FOAF1/movie.mp4'
offs = json.load(open('D:/consoles/ns/hayarigami-recomp/build/v0/audmap.json'))['offs']
def adts(length, profile=1, fi=3, ch=2):
    full = length + 7
    return bytes([0xFF, 0xF1, ((profile & 3) << 6) | ((fi & 15) << 2) | ((ch >> 2) & 1),
        ((ch & 3) << 6) | ((full >> 11) & 3), (full >> 3) & 0xFF, ((full & 7) << 5) | 0x1F, 0xFC])
f = open(MP4, 'rb')
kinds = {}
with open('D:/consoles/ns/hayarigami-recomp/build/v0/aac_st.adts', 'wb') as o:
    n = 0
    for i in range(300, 340):
        off, sz = offs[i]
        f.seek(off); d = f.read(sz)
        kinds[d[0]] = kinds.get(d[0], 0) + 1
        o.write(adts(len(d)) + d); n += 1
print('wrote', n, 'kinds:', {hex(k): v for k, v in kinds.items()})
