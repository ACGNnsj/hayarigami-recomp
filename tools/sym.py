import sys,bisect
A=sorted(int(l,16) for l in open(r'D:/consoles/ns/hayarigami-recomp/build/v0/faddr.txt'))
for a in sys.argv[1:]:
    v=int(a,16)
    i=bisect.bisect_right(A,v)-1
    if i<0: print(hex(v),'-> none'); continue
    print(hex(v),'-> f_%x'%A[i],'+%#x'%(v-A[i]),'size?', (A[i+1]-A[i]) if i+1<len(A) else -1)
