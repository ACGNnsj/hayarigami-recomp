import sys, glob
mods = ["D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/main", "D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/subsdk0", "D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/sdk"]
cands = ["FindInt32", "FindData", "findData", "csd-0", "csd-1", "9MediaData"]
for m in mods:
    d = open(m, "rb").read()
    print("=== ", m.split("/")[-1], len(d))
    for c in cands:
        n = 0; i = d.find(c.encode())
        while i >= 0 and n < 3: n += 1; i = d.find(c.encode(), i + 1)
        print("  ", c, n)