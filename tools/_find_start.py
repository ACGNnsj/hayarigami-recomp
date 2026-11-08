import sys
sys.path.insert(0, r'D:/consoles/ns/xc2-recomp')
from recomp.nso import Nso
for f in ['main','sdk','subsdk0']:
    n = Nso(rf'D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/{f}')
    ex = n.exports()
    hit = [s for s in ex if 'init5Start' in s[0]]
    print('==', f, 'exports', len(ex))
    for s in hit: print('   ', hex(s[1]), s[0])
    srt = [s for s in ex if 'nn4init' in s[0]]
    for s in srt[:12]: print('  nn4init:', hex(s[1]), s[0])