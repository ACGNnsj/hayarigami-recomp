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
for tag, p in (('base', 'D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/start.dat'),
               ('patch', 'D:/consoles/ns/010095B01AF94000/RomFs/FOAF1/start.dat')):
    d, recs = parse(p)
    big = [(n, o, s) for n, o, s in recs if s > 400000]
    print(tag, 'total', len(d), 'records', len(recs), 'big:', len(big))
    for n, o, s in sorted(big, key=lambda x: -x[2])[:14]:
        print('   %-22s off %-10d size %-9d head %s' % (n, o, s, d[o+16:o+40].hex()))