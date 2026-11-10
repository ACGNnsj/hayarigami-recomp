import struct
def boxes(d, off, end, depth=0, want=("moov","trak","mdia","minf","stbl","avc1","avcC","stsd","stco","co64","stsz","stsc")):
    out=[]
    p=off
    while p+8<=end:
        size=struct.unpack_from(">I",d,p)[0]; typ=d[p+4:p+8].decode("latin1")
        hdr=8
        if size==1:
            size=struct.unpack_from(">Q",d,p+8)[0]; hdr=16
        elif size==0:
            size=end-p
        if size<hdr or p+size>end: break
        out.append((depth,typ,p,size))
        if typ in want:
            out+=boxes(d,p+hdr,p+size,depth+1,want)
        p+=size
    return out
for tag,p in (("old", r"D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree/FOAF1/movie.mp4"),
              ("new", r"D:/consoles/ns/010095B01AF94000/RomFs/FOAF1/movie.mp4")):
    d=open(p,"rb").read()
    print(tag, "size", len(d))
    for depth,typ,off,size in boxes(d,0,len(d)):
        if typ in ("moov","avcC","avc1","stco","co64","stsz","ftyp"):
            print("   "*depth, typ, off, size, d[off+8:off+8+16].hex() if typ in ("avcC","ftyp") else "")
