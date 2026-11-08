import zlib,struct
def readpng(p):
    b=open(p,'rb').read(); off=8; idat=b''
    while off<len(b):
        ln=struct.unpack('>I',b[off:off+4])[0]; ty=b[off+4:off+8]; data=b[off+8:off+8+ln]
        if ty==b'IHDR': w,h=struct.unpack('>II',data[:8]); ct=data[9]
        elif ty==b'IDAT': idat+=data
        elif ty==b'IEND': break
        off+=12+ln
    raw=zlib.decompress(idat); ch=4 if ct==6 else 3; stride=w*ch
    out=bytearray(w*h*ch); prev=bytearray(stride)
    for y in range(h):
        ft=raw[y*(stride+1)]; line=raw[y*(stride+1)+1:(y+1)*(stride+1)]; cur=bytearray(stride)
        for x in range(stride):
            a=cur[x-ch] if x>=ch else 0; bb=prev[x]; c=prev[x-ch] if x>=ch else 0; v=line[x]
            if ft==1: v+=a
            elif ft==2: v+=bb
            elif ft==3: v+=(a+bb)>>1
            elif ft==4:
                pp=a+bb-c; pa=abs(pp-a); pb=abs(pp-bb); pc=abs(pp-c)
                v+= a if (pa<=pb and pa<=pc) else (bb if pb<=pc else c)
            cur[x]=v&255
        out[y*stride:(y+1)*stride]=cur; prev=cur
    return w,h,ch,out
w,h,ch,d=readpng('D:/consoles/ns/hayarigami-recomp/build/v0/full_th3.png')
# black mask per 64x64 cell
print('    '+''.join(str((x//64)%10) for x in range(0,w,64)))
for y0 in range(0,h,64):
    row=''
    for x0 in range(0,w,64):
        s=0; n=0
        for y in range(y0,min(y0+64,h),8):
            for x in range(x0,min(x0+64,w),8):
                i=(y*w+x)*ch
                s+= d[i]+d[i+1]+d[i+2]; n+=3
        v=s/n
        row+= '.' if v>60 else ('o' if v>25 else ('x' if v>8 else '#'))
    print(f'{y0:4d} '+row)
