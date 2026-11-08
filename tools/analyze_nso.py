
import sys, struct, collections
sys.path.insert(0, r"D:\consoles\ns\hayarigami-recomp\tools")
from nso import Nso

p = r"D:\consoles\ns\010095B01AF94000\ExeFs\main"
n = Nso(p)
print("build_id", n.build_id)
print("size", hex(n.size), "text", n.text, "rodata", n.rodata, "data", n.data, "bss", hex(n.bss_size))
print("needed", n.needed)
print("n_syms", len(n.syms), "n_relocs", len(n.relocs))
und = [s for s in n.syms if s[2] == 0]
print("undefined (imports):", len(und))
names = collections.Counter()
for name, info, shndx, val, size in und:
    names[name] += 1
for k, v in sorted(names.items()):
    print("IMP", k, v)
