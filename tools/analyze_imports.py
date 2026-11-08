
import sys, collections
sys.path.insert(0, r"D:\consoles\ns\hayarigami-recomp\tools")
from nso import Nso
n = Nso(r"D:\consoles\ns\010095B01AF94000\ExeFs\main")
und = [s[0] for s in n.syms if s[2] == 0]
groups = collections.Counter()
special = []
for name in und:
    if not name.startswith("_ZN2nn"): 
        special.append(name); continue
    body = name[6:]
    ns = body.split("2",1)[0] if "2" in body else body
    # crude: take up to first digit marker
    groups[body[:14]] += 1
print("TOTAL", len(und))
print("--- non-nn imports ---")
for s in special: print("  ", s)
print("--- nn groups ---")
for k,v in groups.most_common(40): print(f"  {k}: {v}")
print("--- nvn/aud/vi/hid mentions ---")
for name in und:
    if any(t in name.lower() for t in ("nvn","nvdrv","audren","auddev","audin","vi","hid","gfx","gpu","am ","account")):
        print("  ", name)
