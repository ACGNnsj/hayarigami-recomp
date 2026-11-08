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
rows=(h+3)//4; cols=(w+3)//4
blk=[]
for by in range(rows):
    line=[]
    for bx in range(cols):
        s=0
        for yy in range(4):
            base=((by*4+yy)*w+bx*4)*ch
            for xx in range(4):
                i=base+xx*ch
                s+=d[i]+d[i+1]+d[i+2]
        line.append(s/48.0)  # mean per channel
    blk.append(line)
# report fully-black runs per block row of 64 (i.e. per 16 block rows)
for y0 in range(0,rows,16):
    seg=[]
    for by in range(y0,min(y0+16,rows)):
        run=0; runs=[]
        for bx in range(cols):
            if blk[by][bx] < 2.0: run+=1
            else:
                if run: runs.append((bx-run,run)); run=0
        if run: runs.append((cols-run,run))
        seg.append(runs)
    print('blockrows',y0,'-',y0+15, 'sample:', [(i,r) for i,r in enumerate(seg) if r][:6])
