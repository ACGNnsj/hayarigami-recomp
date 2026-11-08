
import sys, re, collections
sys.path.insert(0, r"D:\consoles\ns\hayarigami-recomp\tools")
from nso import Nso
for mod in ("main","subsdk0"):
    n = Nso(rf"D:\consoles\ns\hayarigami-recomp\build\extracted\latest\exefs\{mod}")
    img = bytes(n.image)
    strs = [s.decode() for s in re.findall(rb"[\x20-\x7e]{8,}", img)]
    paths = [s for s in strs if re.search(r"\.(cpp|hpp|c|h)\b", s)]
    print(f"== {mod}: strings={len(strs)} source-ish={len(paths)}")
    bases = collections.Counter(p.replace("\\\\","/").split("/")[-1] for p in paths)
    print("   distinct files:", len(bases))
    for k,v in bases.most_common(15): print("   ", v, k)
    dirs = collections.Counter(p.replace("\\\\","/").split("/")[-2] for p in paths if "/" in p)
    print("   top dirs:", dirs.most_common(12))
