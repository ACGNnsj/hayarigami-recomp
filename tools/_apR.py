base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "framework/runtime/fs_host.c"
t = open(p, encoding="utf-8").read()
old = "    if (plen < 5 || strcmp(path + plen - 5, \".mp4\")) return;"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, "    if (plen < 4 || strcmp(path + plen - 4, \".mp4\")) return;   // \".mp4\" is four bytes")
open(p, "w", encoding="utf-8").write(t)
print('suffix fixed')