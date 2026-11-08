
import sys, json, re, os
sys.path.insert(0, r"D:\consoles\ns\hayarigami-recomp\tools")
from nso import Nso

def imports(p):
    n = Nso(p)
    return sorted({s[0] for s in n.syms if s[2]==0})

base = r"D:\consoles\ns\hayarigami-recomp\build\extracted\v0\exefs"
allimp = set()
per = {}
for m in ("main","subsdk0"):
    imp = imports(os.path.join(base,m))
    per[m] = imp
    allimp |= set(imp)

def coverage(root):
    # gather all text in runtime dir
    blob = []
    for dp, dn, fn in os.walk(root):
        if '.git' in dp: continue
        for f in fn:
            if f.endswith(('.c','.cpp','.h','.hpp','.inl','.inc','.txt','.json','.py')):
                try: blob.append(open(os.path.join(dp,f), encoding='utf-8', errors='ignore').read())
                except: pass
    text = "\n".join(blob)
    hit = [x for x in allimp if x and x in text]
    return hit, len(text)

for root in [r"D:\consoles\ns\xc2-recomp\runtime", r"D:\consoles\ns\Metroid-Dread-Recomp\runtime", r"D:\consoles\ns\totk-pc-recomp\runtime"]:
    if not os.path.isdir(root): 
        print(root, "MISSING"); continue
    hit, n = coverage(root)
    print(f"{os.path.basename(os.path.dirname(root))}: {len(hit)}/{len(allimp)} imported symbols appear in runtime ({n} chars scanned)")

json.dump({"main": per["main"], "subsdk0": per["subsdk0"]}, open(r"D:\consoles\ns\hayarigami-recomp\data\imports.json","w"), indent=1)
print("wrote data/imports.json", len(per["main"]), len(per["subsdk0"]))
