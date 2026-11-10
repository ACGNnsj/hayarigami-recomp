import struct, sys
d = open(sys.argv[1], 'rb').read()
size, rva = struct.unpack_from('<III', d, 1608 - 12 + 12)[:0] or (0, 0)
# stream dir: find type 3
nstreams = struct.unpack_from('<I', d, 8)[0]
# header: sig(4) ver(4) nstreams(4) dirrva(4) ...
sig, ver, ns, dirova = struct.unpack_from('<IIII', d, 0)
print('ns=%d dirova=%d' % (ns, dirova))
for i in range(ns):
    t, sz, rv = struct.unpack_from('<III', d, dirova + i * 12)
    if t == 3:
        nthread = struct.unpack_from('<I', d, rv)[0]
        print('nthread=%d' % nthread)
        for j in range(min(nthread, 40)):
            off = rv + 4 + j * 48
            f = struct.unpack_from('<IIIIQQIIII', d, off)
            tid, susp, cs, ctxsz, ctxrva = f[0], f[1], f[8], f[9], 0
            # f = tid,susp,pcls,prio,teb,st_base,st_size,st_rva,ctx_size,ctx_rva
            tid, susp, pcls, prio, teb, stb, stsz, strva, ctxsz, ctxrva = f
            if tid in (17612, 50764, 48444, 55316):
                print('tid=%d teb=0x%X stb=0x%X stsz=%d strva=%d ctxsz=%d ctxrva=%d' % (tid, teb, stb, stsz, strva, ctxsz, ctxrva))
                if ctxrva and ctxsz >= 272:
                    print('  ctx bytes:', d[ctxrva:ctxrva+64].hex())
