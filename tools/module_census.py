
import sys, hashlib, collections
sys.path.insert(0, r"D:\consoles\ns\hayarigami-recomp\tools")
from nso import Nso
from pathlib import Path
base = Path(r"D:\consoles\ns\hayarigami-recomp\build\extracted\v0\exefs")
upd  = Path(r"D:\consoles\ns\010095B01AF94000\ExeFs")
for label, p in [("base", base/"main"), ("update", upd/"main")]:
    b = p.read_bytes()
    n = Nso(str(p))
    und = [s[0] for s in n.syms if s[2]==0]
    print(f"{label}: bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()[:32]} text={n.text[1]} rodata={n.rodata[1]} data={n.data[1]} bss={n.bss_size} needed={n.needed} syms={len(n.syms)} imports={len(und)} relocs={len(n.relocs)}")
for m in ["sdk","subsdk0","rtld"]:
    p = base/m
    if p.exists():
        b = p.read_bytes()
        try:
            n = Nso(str(p)); print(f"{m}: bytes={len(b)} text={n.text[1]} needed={n.needed} imports={len([s for s in n.syms if s[2]==0])}")
        except Exception as e:
            print(f"{m}: bytes={len(b)} not NSO ({e})")
