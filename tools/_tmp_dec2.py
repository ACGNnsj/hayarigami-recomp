
import struct
import texture2ddecoder as t
from PIL import Image
def dec(name,W,H):
    p='D:/consoles/ns/hayarigami-recomp/build/v0/raw_fresh/'+name+'.bin'
    d=open(p,'rb').read()
    bw,bh,bpb=4,4,16
    rb=(W+bw-1)//bw*bpb
    bl_pitch=(rb+2047)&~2047
    gobs_x=bl_pitch//64
    def gob_off(x,y):
        return (x%64//32)*256+(y%8//2)*64+(x%32//16)*32+(y%2)*16+x%16
    bhGOB=1<<3; block=512*bhGOB; out=bytearray()
    rows=(H+bh-1)//bh
    for by in range(rows):
        for bx in range((W+bw-1)//bw):
            x=bx*16
            off=(by//(8*bhGOB))*gobs_x*block+(x//64)*block+((by%(8*bhGOB))//8)*512+gob_off(x,by)
            out+=d[off:off+16] if off+16<=len(d) else b'\x00'*16
    img=t.decode_bc7(bytes(out),W,H)
    Image.frombytes('RGBA',(W,H),img).save('D:/consoles/ns/hayarigami-recomp/build/v0/raw_fresh_dec_'+name+'.png')
    print(name,'ok size',len(d))
dec('tex_004_1920x1080_fmt4d_t3_d0_lay1',1920,1080)
dec('tex_005_1040x350_fmt4d_t3_d0_lay1',1040,350)
dec('tex_008_1024x1024_fmt4d_t3_d0_lay1',1024,1024)
