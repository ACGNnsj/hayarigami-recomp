import struct
src = open('D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/movie.mp4','rb').read()
def boxes(b,s,e):
    i=s
    while i+8<=e:
        m=struct.unpack('>I',b[i:i+4])[0]; t=b[i+4:i+8]
        if m<8: break
        yield t,i+8,i+m
        i+=m
def find(b,s,e,path):
    for t,s2,e2 in boxes(b,s,e):
        if t==path[0]:
            if len(path)==1: return (s2,e2)
            r=find(b,s2,e2,path[1:])
            if r: return r
    return None
moov=find(src,0,len(src),[b'moov']); trak=find(src,moov[0],moov[1],[b'trak'])
stbl=find(src,trak[0],trak[1],[b'mdia',b'minf',b'stbl'])
S={t:(s,e) for t,s,e in boxes(src,stbl[0],stbl[1])}
s,e=S[b'stsz']; pz=src[s:e]; cnt=struct.unpack('>I',pz[8:12])[0]
sizes=[struct.unpack('>I',pz[12+4*i:16+4*i])[0] for i in range(cnt)]
s,e=S[b'stco']; pc=src[s:e]; nch=struct.unpack('>I',pc[4:8])[0]
offs=[struct.unpack('>I',pc[8+4*i:12+4*i])[0] for i in range(nch)]
s,e=S[b'stss']; ps=src[s:e]; ns=struct.unpack('>I',ps[4:8])[0]
sync=[struct.unpack('>I',ps[8+4*i:12+4*i])[0] for i in range(ns)]
print('samples',cnt,'sync count',ns,'first sync',sync[:5])
s,e=S[b'stts']; pt=src[s:e]; nt=struct.unpack('>I',pt[4:8])[0]
print('stts entries',nt,[ (struct.unpack('>I',pt[8+8*i:12+8*i])[0], struct.unpack('>I',pt[12+8*i:16+8*i])[0]) for i in range(min(nt,3))])
for i in range(6):
    s0=src[offs[i]:offs[i]+sizes[i]]; j=0; types=[]
    while j+4<=len(s0):
        m=struct.unpack('>I',s0[j:j+4])[0]; j+=4
        if m==0 or j+m>len(s0): break
        types.append((s0[j]&0x1f,m)); j+=m
    print(i,'size',sizes[i],'nals',types)