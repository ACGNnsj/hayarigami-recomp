
import sys, collections, json
sys.path.insert(0, r"D:\consoles\ns\hayarigami-recomp\tools")
from nso import Nso
n = Nso(r"D:\consoles\ns\hayarigami-recomp\build\extracted\v0\exefs\subsdk0")
und = [s[0] for s in n.syms if s[2]==0]
print("subsdk0 imports", len(und))
# summarize by namespace token
def ns(name):
    if not name.startswith("_ZN2nn"): return "OTHER"
    body = name[6:]
    # after _ZN2nn, read digits
    i = 0
    while i < len(body) and body[i].isdigit(): i += 1
    return body[i:].split(str(len(body[i:])),1)[0] if body[i:][:2].isdigit() is False else body[i:][:12]
c = collections.Counter(ns(x) for x in und)
for k,v in c.most_common(30): print(f"  {k}: {v}")
print("--- nvn count:", sum(1 for x in und if x.startswith("nvn") or x.startswith("_ZN2nv")))
print("--- sample non-nn:", [x for x in und if not x.startswith("_ZN2nn") and not x.startswith("nvn")][:25])
