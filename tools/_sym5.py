import sys
sys.path.insert(0, "D:/consoles/ns/hayarigami-recomp/tools")
from nso import Nso
n = Nso("D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/subsdk0")
ex = sorted(set(s[0] for s in n.exports()))
nn = [s for s in ex if "NnMediaData" in s]
print("NnMediaData count", len(nn))
for s in nn: print("   ", s)