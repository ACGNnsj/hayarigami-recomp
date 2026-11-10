import struct
d = open('D:/consoles/ns/hayarigami-recomp/build/v0/packets.bin','rb').read()
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
s,e=S[b'stsz']; pz=src[s:e]; cnt=struct.unpack('>I',pz[8:12])[0]; unit=struct.unpack('>I',pz[4:8])[0]
sizes=[unit]*cnt if unit else [struct.unpack('>I',pz[12+4*i:16+4*i])[0] for i in range(cnt)]
s,e=S[b'stco']; pc=src[s:e]; nch=struct.unpack('>I',pc[4:8])[0]
offs=[struct.unpack('>I',pc[8+4*i:12+4*i])[0] for i in range(nch)]
out=bytearray(); k=0
for i in range(min(cnt,len(offs))):
    s0=src[offs[i]:offs[i]+sizes[i]]
    j=0; ab=bytearray()
    while j+4<=len(s0):
        m=struct.unpack('>I',s0[j:j+4])[0]; j+=4
        if m==0 or j+m>len(s0): break
        ab+=b'\x00\x00\x00\x01'+s0[j:j+m]; j+=m
    out+=struct.pack('<I',len(ab))+bytes(ab); k+=1
open('D:/consoles/ns/hayarigami-recomp/build/v0/pk_annexb.bin','wb').write(bytes(out))
print('samples',k,'bytes',len(out))