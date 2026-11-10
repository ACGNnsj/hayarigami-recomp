import struct
p = 'D:/consoles/ns/hayarigami-recomp/build/v0/romfs-patches/package_tex.dat'
d = open(p, 'rb').read()
def entry(i):
    off = 0x10 + i*0x40
    name = d[off:off+32].split(b'\x00')[0].decode()
    size, foff = struct.unpack_from('<QQ', d, off+48)
    return name, foff, size
for i in (0, 4, 9):
    n, o, s = entry(i)
    print(n, 'off', o, 'size', s)
    print('  ', d[o:o+64].hex())