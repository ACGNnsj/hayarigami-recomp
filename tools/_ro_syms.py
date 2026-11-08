import sys, json
sys.path.insert(0, r'D:/consoles/ns/xc2-recomp')
import recomp.nso as N
for f in ['main','subsdk0','sdk']:
    n = N.Nso(rf'D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/{f}')
    ex = [s[0] for s in n.exports() if '_ZN2nn2ro' in s[0]]
    im = [s[0] for s in n.imports() if '_ZN2nn2ro' in s[0]]
    print('==', f, 'exp', len(ex), 'imp', len(im))
    for s in sorted(set(ex+im)): print('  ', s)