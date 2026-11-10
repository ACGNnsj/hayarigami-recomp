import os
for root in ('D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs-tree', 'D:/consoles/ns/010095B01AF94000/RomFs'):
    print('==', root)
    big = []
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            s = os.path.getsize(p)
            if s > 1000000:
                big.append((s, os.path.relpath(p, root)))
    for s, n in sorted(big):
        print('  %8.2fMB %s' % (s / 1048576, n))