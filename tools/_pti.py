import struct
def parse(p):
    d = open(p, 'rb').read()
    assert d[:8] == b'PS_FS_V1', d[:8]
    recs = []
    off = 0x10
    while off + 0x40 <= len(d):
        name = d[off:off+32].split(b'\x00')[0]
        if not name or not all(32 <= c < 127 for c in name):
            break
        size, foff = struct.unpack_from('<QQ', d, off + 48)
        recs.append((name.decode(), foff, size))
        off += 0x40
    return d, recs
p = 'D:/consoles/ns/hayarigami-recomp/build/v0/romfs-patches/package_tex.dat'
d, recs = parse(p)
print('entries:', len(recs), 'filelen:', len(d))
for n, o, s in recs:
    print(' ', n, 'off', o, 'size', s, 'head:', d[o:o+16].hex() if o+s <= len(d) else 'OUT OF RANGE')