import struct,glob
for p in sorted(glob.glob('build/v0/bufdump/buf_*.bin')):
    d=open(p,'rb').read()
    if len(d)%4: continue
    n=len(d)//4
    v=struct.unpack('<%df'%n,d)
    for stride in (6,8,9):
        if n%stride: continue
        m=n//stride
        if m not in (4,6): continue
        xs=[v[i*stride] for i in range(m)]; ys=[v[i*stride+1] for i in range(m)]
        xr=(min(xs),max(xs)); yr=(min(ys),max(ys))
        if xr in [(0.0,384.0),(384.0,768.0),(768.0,1152.0),(1152.0,1536.0),(1536.0,1920.0)] and yr==(694.0,1014.0):
            print(p,'stride',stride,'m',m)
            for i in range(m):
                print('   ',[round(v[i*stride+k],4) for k in range(stride)])
            break
