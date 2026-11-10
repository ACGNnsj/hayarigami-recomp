base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "tools/build_haya.sh"
t = open(p, encoding="utf-8").read()
o = "-lmfuuid -lwmcodecdspuuid -lole32"
assert t.count(o) == 1
open(p, "w", encoding="utf-8").write(t.replace(o, "-lmfuuid -lole32"))
print("lib dropped")