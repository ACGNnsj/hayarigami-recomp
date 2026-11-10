d=open('build/extracted/v0/romfs-tree/FOAF1/start.dat','rb').read()
seg=d[20003840:20003840+209011]
for m in (b'Yaz0',b'Yay0',b'SARC',b'BNTX',b'ZSTD',b'LZMA'):
    print(m,seg.find(m))
