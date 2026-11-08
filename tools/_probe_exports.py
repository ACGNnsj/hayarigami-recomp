import sys
sys.path.insert(0, r'D:/consoles/ns/xc2-recomp')
import recomp.nso as N
n = N.Nso(r'D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/sdk')
ex = n.exports()[:10]
for s in ex: print(s)
print('sym count', len(n.exports()))