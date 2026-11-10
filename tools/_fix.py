p = "D:/consoles/ns/hayarigami-recomp/tools/_mp4e.py"
ls = open(p, encoding="utf-8").read().split(chr(10))
assert ls[11].startswith("moov = "), ls[11]
ls[11] = "moov = 32"
open(p, "w", encoding="utf-8").write(chr(10).join(ls))
print("line12 pinned")