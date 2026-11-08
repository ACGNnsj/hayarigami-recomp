d=open('D:/consoles/ns/hayarigami-recomp/build/v0/raw/tex_001_1920x1080_fmt4d_t3_d0_lay1.bin','rb').read()
n=len(d)//16
z=[i for i in range(n) if d[i*16:(i+1)*16]==b'\x00'*16]
print('chunks',n,'zero',len(z))
print('first zero indices',z[:20])
# consecutive runs
runs=[]; 
prev=None; start=None
for i in z:
    if prev is None or i!=prev+1:
        if start is not None: runs.append((start,prev-start+1))
        start=i
    prev=i
if start is not None: runs.append((start,prev-start+1))
print('runs',len(runs),'longest',sorted(runs,key=lambda r:-r[1])[:8])
