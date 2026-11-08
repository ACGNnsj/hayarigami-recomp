import texture2ddecoder as t, struct, zlib
p='D:/consoles/ns/hayarigami-recomp/build/v0/raw/tex_001_1920x1080_fmt4d_t3_d0_lay1.bin'
d=open(p,'rb').read()
W,H=1920,1080; rows=270; nblk_x=W//4
row_bytes=W//4*16; gobs_x=row_bytes//64
def gob_off(x,y):
    return (x%64//32)*256+(y%8//2)*64+(x%32//16)*32+(y%2)*16+x%16
def stream(th):
    bh=1<<th; block=512*bh; out=bytearray()
    for by in range(rows):
        for bx in range(nblk_x):
            x=bx*16
            off=(by//(8*bh))*gobs_x*block+(x//64)*block+((by%(8*bh))//8)*512+gob_off(x,by)
            if off+16>len(d): off=0
            out+=d[off:off+16]
    return bytes(out)
def png(path,w,h,rgb):
    raw=b''.join(b'\x00'+rgb[y*w*3:(y+1)*w*3] for y in range(h))
    def chunk(tk,data):
        return struct.pack('>I',len(data))+tk+data+struct.pack('>I',zlib.crc32(tk+data)&0xffffffff)
    open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b''))
for th in (0,1,2,3,4):
    bc=stream(th)
    img=t.decode_bc7(bc,W,H)
    rgb=bytearray(W*H*3)
    rgb[0::3]=img[0::4]; rgb[1::3]=img[1::4]; rgb[2::3]=img[2::4]
    png(f'D:/consoles/ns/hayarigami-recomp/build/v0/full_th{th}.png',W,H,bytes(rgb))
    print('ok',th)
