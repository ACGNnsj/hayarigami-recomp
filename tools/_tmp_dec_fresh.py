
import struct
import texture2ddecoder as t
p='D:/consoles/ns/hayarigami-recomp/build/v0/raw_fresh/tex_001_1920x1080_fmt4d_t3_d0_lay1.bin'
d=open(p,'rb').read()
print('size',len(d))
W,H=1920,1080
bw,bh,bpb=4,4,16
rb=(W+bw-1)//bw*bpb
bl_pitch=(rb+2047)&~2047
rows=(H+bh-1)//bh
print('rb',rb,'bl_pitch',bl_pitch,'rows',rows)
gobs_x=bl_pitch//64
def gob_off(x,y):
    return (x%64//32)*256+(y%8//2)*64+(x%32//16)*32+(y%2)*16+x%16
def stream(th):
    bhGOB=1<<th; block=512*bhGOB; out=bytearray()
    for by in range(rows):
        for bx in range((W+bw-1)//bw):
            x=bx*16
            off=(by//(8*bhGOB))*gobs_x*block+(x//64)*block+((by%(8*bhGOB))//8)*512+gob_off(x,by)
            if off+16>len(d): out+=b'\x00'*16
            else: out+=d[off:off+16]
    return bytes(out)
for th in (3,):
    bc=stream(th)
    print('stream bytes',len(bc))
    img=t.decode_bc7(bc,W,H)
    print('decoded bytes',len(img))
    open('D:/consoles/ns/hayarigami-recomp/build/v0/raw_fresh_dec_th3_rgba.bin','wb').write(img)
    # write simple PNG via PIL if available
    try:
        from PIL import Image
        im=Image.frombytes('RGBA',(W,H),img)
        im.save('D:/consoles/ns/hayarigami-recomp/build/v0/raw_fresh_dec_th3.png')
        print('png saved')
    except Exception as e:
        print('PIL fail',e)
