
import sys, re
sys.path.insert(0, r"D:\consoles\ns\hayarigami-recomp\tools")
from nso import Nso
n = Nso(r"D:\consoles\ns\010095B01AF94000\ExeFs\main")
img = bytes(n.image)
# extract printable ascii strings
strs = re.findall(rb"[\x20-\x7e]{6,}", img)
dec = [s.decode() for s in strs]
print("n_strings", len(dec))
def show(title, pat, limit=40):
    print("===", title)
    c=0
    for s in dec:
        if re.search(pat, s, re.I):
            print("  ", s[:160]); c+=1
            if c>=limit: break
show("engine/version", r"nmpl|nippon|nis\b|version|build|copyright", 25)
show("romfs files", r"\.dat|\.mp4|\.bin|\.szs|\.arc|FOAF", 40)
show("shader", r"shader|\.nso|glsl|spv|program", 20)
show("debug paths", r"[A-Za-z]:\\\\|/home/|src/|\.cpp|\.c\b", 25)
show("sdk", r"nn::|nnSdk|nintendo", 10)
