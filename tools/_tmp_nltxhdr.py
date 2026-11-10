
import struct
for tag,p in [("base","D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/graphics_bg.dat"),
              ("patch","D:/consoles/ns/hayarigami-recomp/build/v0/romfs-patches/FOAF1/graphics_bg.dat")]:
    d=open(p,'rb').read()
    off=0x10
    while off+0x40<=len(d):
        name=d[off:off+32].split(b'\x00')[0]
        if not name or not all(32<=c<127 for c in name): break
        size,foff=struct.unpack_from('<QQ',d,off+48)
        if name.decode() in ("bg5569.nltx","bg5567.nltx","bg5568.nltx"):
            b=d[foff:foff+128]
            print(tag,name.decode(),"size",size)
            print("  magic",b[:8],"u32:",struct.unpack_from('<16I',b,8))
            print("  u64:",struct.unpack_from('<8Q',b,8))
            # payload head after 128?
            print("  payload head:",d[foff+64:foff+96].hex())
        off+=0x40
