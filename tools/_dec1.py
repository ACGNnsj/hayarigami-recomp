import texture2ddecoder as t, struct, zlib, sys
def decode(src, W, H, th, out):
    d=open(src,'rb').read()
    nblk_x=(W+3)//4; row_bytes=nblk_x*16; gobs_x=row_bytes//64; rows=(H+3)//4
    bh=1<<th; block=512*bh
    def gob_off(x,y):
        return (x%64//32)*256+(y%8//2)*64+(x%32//16)*32+(y%2)*16+x%16
    s=bytearray()
    for by in range(rows):
        for bx in range(nblk_x):
            x=bx*16
            off=(by//(8*bh))*gobs_x*block+(x//64)*block+((by%(8*bh))//8)*512+gob_off(x,by)
            if off+16>len(d): off=0
            s+=d[off:off+16]
    img=t.decode_bc7(bytes(s),W,H)
    rgb=bytearray(W*H*3); rgb[0::3]=img[0::4]; rgb[1::3]=img[1::4]; rgb[2::3]=img[2::4]
    raw=b''.join(b'\x00'+rgb[y*W*3:(y+1)*W*3] for y in range(H))
    def chunk(tk,data):
        return struct.pack('>I',len(data))+tk+data+struct.pack('>I',zlib.crc32(tk+data)&0xffffffff)
    open(out,'wb').write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b''))
    print('wrote',out,W,H,'len',len(d))
decode('D:/consoles/ns/hayarigami-recomp/build/v0/raw/tex_002_1295x700_fmt4d_t3_d0_lay1.bin',1295,700,3,'D:/consoles/ns/hayarigami-recomp/build/v0/tex002.png')
