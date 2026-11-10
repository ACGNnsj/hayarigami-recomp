import sys
sys.path.insert(0, "D:/consoles/ns/hayarigami-recomp/tools")
from nso import Nso
for m in ["main", "subsdk0", "sdk"]:
    n = Nso("D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/" + m)
    im = [s[0] for s in n.imports()]
    ex = [s[0] for s in n.exports()]
    mdi = sorted(set(s for s in im if "MediaData" in s))
    mde = sorted(set(s for s in ex if "MediaData" in s))
    print("===", m, "imports MediaData:", len(mdi), "exports MediaData:", len(mde))
    for s in mdi + ["--"] + mde: print("   ", s)