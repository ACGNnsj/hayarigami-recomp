
import struct, os
for p in ["D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/graphics_bg.dat",
          "D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/graphics_ci.dat",
          "D:/consoles/ns/hayarigami-recomp/build/v0/romfs-patches/FOAF1/graphics_bg.dat",
          "D:/consoles/ns/hayarigami-recomp/build/v0/romfs-patches/FOAF1/graphics_ci.dat"]:
    if not os.path.exists(p):
        print("missing", p); continue
    d=open(p,'rb').read()
    print("==",p,"len",len(d),"magic",d[:8])
    if d[:8]==b'PS_FS_V1':
        off=0x10; recs=[]
        while off+0x40<=len(d):
            name=d[off:off+32].split(b'\x00')[0]
            if not name or not all(32<=c<127 for c in name): break
            size,foff=struct.unpack_from('<QQ',d,off+48)
            recs.append((name.decode(),foff,size)); off+=0x40
        print(" records",len(recs))
        for n,o,s in sorted(recs,key=lambda x:-x[2])[:12]:
            print('  ',n,'off',o,'size',s,'head',d[o:o+32].hex() if o+32<=len(d) else 'OOR')
