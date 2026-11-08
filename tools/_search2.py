def gob_off(x,y):
    return (x%64//32)*256+(y%8//2)*64+(x%32//16)*32+(y%2)*16+x%16
def scan(path,W,H,bh,strides):
    d=open(path,'rb').read()
    nblk_x=(W+3)//4; rows=(H+3)//4; band_rows=8*bh
    best=[]
    for stride in strides:
        zero=0; oob=0
        for by in range(rows):
            for bx in range(nblk_x):
                x=bx*16
                off=(by//band_rows)*stride*512*bh+(x//64)*512*bh+((by%band_rows)//8)*512+gob_off(x,by)
                if off+16>len(d): oob+=1; continue
                if d[off:off+16]==b'\x00'*16: zero+=1
        best.append((zero,oob,stride))
    best.sort()
    return best[:4]
base='D:/consoles/ns/hayarigami-recomp/build/v0/raw/'
print('1080p bh8', scan(base+'tex_001_1920x1080_fmt4d_t3_d0_lay1.bin',1920,1080,8,range(112,145)))
print('1295 bh8', scan(base+'tex_002_1295x700_fmt4d_t3_d0_lay1.bin',1295,700,8,range(76,140)))
print('1024x64 bh2', scan(base+'tex_003_1024x64_fmt4d_t1_d0_lay1.bin',1024,64,2,range(56,100)))
