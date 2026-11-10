
import struct
targets={(768,3200),(1280,768),(1920,1080),(1600,1600),(1024,64)}
for p in ["D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/graphics_bg.dat",
          "D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/graphics_ci.dat",
          "D:/consoles/ns/hayarigami-recomp/build/v0/romfs-patches/FOAF1/graphics_bg.dat",
          "D:/consoles/ns/hayarigami-recomp/build/v0/romfs-patches/FOAF1/graphics_ci.dat",
          "D:/consoles/ns/hayarigami-recomp/build/v0/romfs-patches/package_tex.dat"]:
    try:
        d=open(p,'rb').read()
    except Exception as e:
        print("missing",p); continue
    if d[:8]!=b'PS_FS_V1':
        print(p,"not PS_FS"); continue
    off=0x10; found=[]
    while off+0x40<=len(d):
        name=d[off:off+32].split(b'\x00')[0]
        if not name or not all(32<=c<127 for c in name): break
        size,foff=struct.unpack_from('<QQ',d,off+48)
        if foff+64<=len(d) and d[foff:foff+8]==b'NMPLTEX1':
            w,h=struct.unpack_from('<II',d,foff+24)
            if (w,h) in targets:
                found.append((name.decode(),w,h,foff,size))
        off+=0x40
    print("==",p.split('/')[-2]+'/'+p.split('/')[-1],"hits",len(found))
    for n,w,h,o,s in found[:20]:
        print('  ',n,w,h,'off',o,'size',s)
