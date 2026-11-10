import json, struct, sys
MP4 = 'D:/consoles/ns/hayarigami-recomp/build/extracted/latest/romfs/FOAF1/movie.mp4'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'D:/consoles/ns/hayarigami-recomp/build/v0/aac_test.adts'
RANGE = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (1, 10 ** 9)
offs = json.load(open('D:/consoles/ns/hayarigami-recomp/build/v0/audmap.json'))['offs']
def adts_header(length, profile=1, fi=3, ch=2):
    full = length + 7
    h = bytearray(7)
    h[0] = 0xFF; h[1] = 0xF1
    h[2] = ((profile & 3) << 6) | ((fi & 15) << 2) | ((ch >> 2) & 1)
    h[3] = ((ch & 3) << 6) | ((full >> 11) & 3)
    h[4] = (full >> 3) & 0xFF
    h[5] = ((full & 7) << 5) | 0x1F
    h[6] = 0xFC
    return bytes(h)
f = open(MP4, 'rb')
n = 0; total = 0
with open(OUT, 'wb') as o:
    for i, (off, sz) in enumerate(offs):
        if not (RANGE[0] <= i < RANGE[0] + RANGE[1]): continue
        f.seek(off)
        d = f.read(sz)
        if i == 0:
            assert sz == 293 and d[:3] == bytes([0xde, 0x02, 0x00]), 'sample0 tag changed!'
            continue  # Lavc tag blob: game skips it too
        pass  # SCE+CPE mix (mono/stereo segments); MFT decides
        o.write(adts_header(len(d)) + d)
        n += 1; total += len(d) + 7
print('frames=%d adts_bytes=%d seconds=%.1f' % (n, total, n * 1024 / 48000))
