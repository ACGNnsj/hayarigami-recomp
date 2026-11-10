
import struct
p='D:/consoles/ns/hayarigami-recomp/build/v0/romfs-patches/package_tex.dat'
d=open(p,'rb').read()
def parse(d):
    recs=[]; off=0x10
    while off+0x40<=len(d):
        name=d[off:off+32].split(b'\x00')[0]
        if not name or not all(32<=c<127 for c in name): break
        size,foff=struct.unpack_from('<QQ',d,off+48)
        recs.append((name.decode(),foff,size)); off+=0x40
    return recs
for name,off,size in parse(d)[:4]:
    b=d[off:off+128]
    print(name,'size',size)
    print(' header hex:',b[:64].hex())
    # try u32 fields after magic
    print(' u32:',struct.unpack_from('<16I',b,8))
