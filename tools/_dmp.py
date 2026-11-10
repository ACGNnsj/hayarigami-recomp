import struct, sys
p = sys.argv[1]
d = open(p, 'rb').read()
assert d[:4] == b'MDMP', d[:4]
ver, nstreams, dirova = struct.unpack_from('<III', d, 4)
streams = {}
for i in range(nstreams):
    t, size, rva = struct.unpack_from('<III', d, dirova + i * 12)
    streams[t] = (size, rva)
print('streams:', [(t, streams[t]) for t in sorted(streams)])
# ModuleListStream = 7? print modules
if 4 in streams:
    size, rva = streams[4]
    (nmod,) = struct.unpack_from('<I', d, rva)
    print('modules:', nmod)
    mods = []
    for i in range(nmod):
        off = rva + 4 + i * 108
        f = struct.unpack_from('<QIIII' + '13I' + 'IIIIQQ', d, off)
        base = f[0]
        mods.append(base)
    print('bases:', ['0x%X' % b for b in sorted(mods)[:8]])
# ThreadListStream = 4
if 3 in streams:
    size, rva = streams[3]
    (nthread,) = struct.unpack_from('<I', d, rva)
    print('threads:', nthread)
    for i in range(nthread):
        off = rva + 4 + i * 48
        tid, susp, pcls, prio, teb, st_base, st_size, st_rva, ctx_size, ctx_rva = struct.unpack_from('<IIIIQQIIII', d, off)
        rip = struct.unpack_from('<Q', d, ctx_rva + 264)[0] if ctx_size >= 272 else 0
        rsp = struct.unpack_from('<Q', d, ctx_rva + 0xA8)[0] if ctx_size >= 272 else 0
        print('tid=%d rip=0x%X rsp=0x%X susp=%d' % (tid, rip, rsp, susp))
