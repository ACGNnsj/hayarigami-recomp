d=open('D:/consoles/ns/hayarigami-recomp/build/v0/raw/tex_001_1920x1080_fmt4d_t3_d0_lay1.bin','rb').read()
W,BW=1920,4
nblk_x=W//4
rows=270
def gob_off(x,y):
    return (x%64//32)*256+(y%8//2)*64+(x%32//16)*32+(y%2)*16+x%16
def count(stride, bh, order='xy'):
    band_rows=8*bh
    zero=0; outr=0
    for by in range(rows):
        for bx in range(nblk_x):
            x=bx*16
            band=by//band_rows
            if order=='xy':
                off=band*stride*512*bh+(x//64)*512*bh+((by%band_rows)//8)*512+gob_off(x,by)
            else:
                off=(x//64)*((rows+band_rows-1)//band_rows)*512*bh+band*512*bh+((by%band_rows)//8)*512+gob_off(x,by)
            if off+16>len(d): outr+=1; continue
            if d[off:off+16]==b'\x00'*16: zero+=1
    return zero,outr
for stride in (120,128,136,160):
    for bh in (1,2,4,8,16,32,64):
        z,o=count(stride,bh)
        print(f'stride={stride} bh={bh} zero={z} oob={o}')
