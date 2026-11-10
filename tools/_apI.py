base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "tools/build_haya.sh"
t = open(p, encoding="utf-8").read()
o = "-lmfplat -lmfuuid -lole32"
assert t.count(o) == 1
t = t.replace(o, "-lmfplat -lmfuuid -lwmcodecdspuuid -lole32")
open(p, "w", encoding="utf-8").write(t)
print("link fixed")