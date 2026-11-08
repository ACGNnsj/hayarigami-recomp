import sys
sys.path.insert(0, r'D:/consoles/ns/xc2-recomp')
import recomp.nso as N
for f in ['main','sdk','subsdk0']:
    n = N.Nso(rf'D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/{f}')
    sz = n.dyn.get(27); ia = n.dyn.get(25); it = n.dyn.get(12)
    print(f, 'INIT_ARRAYSZ', sz, 'entries', (sz//8) if sz else None, 'INIT_ARRAY', hex(ia) if ia else None, 'INIT', hex(it) if it else None)