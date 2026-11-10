import struct
tgts = {(768,3200),(1280,768),(1600,1600),(1024,64),(208,60)}
for p in ['build/extracted/v0/romfs-tree/FOAF1/start.dat','build/extracted/v0/romfs-tree/FOAF1/database.dat','build/v0/romfs-patches/FOAF1/start.dat']:
    try: d=open(p,'rb').read()
    except Exception as e: print('missing',p); continue
    print('==',p,len(d),'head',d[:8])
    if d[:8]!=b'PS_FS_V1': continue
    off=0x10;n=0
    while off+0x40<=len(d):
        nm=d[off:off+32].split(b'\x00')[0]
        if not nm or not all(32<=c<127 for c in nm): break
        size,foff=struct.unpack_from('<QQ',d,off+48)
        if foff+64<=len(d) and d[foff:foff+8]==b'NMPLTEX1':
            w,h=struct.unpack_from('<II',d,foff+24)
            tag='TGT' if (w,h) in tgts else '...'
            print('  ',tag,nm.decode(),w,h,'off',foff,'size',size); n+=1
        off+=0x40
    print('  total',n)
