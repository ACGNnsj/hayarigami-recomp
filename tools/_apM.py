base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "framework/runtime/ov_movie.c"
t = open(p, encoding="utf-8").read()
o = "{ 0x62ce7e72, 0x4c02, 0x4adb, { 0xa8, 0xfd, 0xdf, 0xb5, 0x43, 0x9c, 0x09, 0xd6 } }"
n = "{ 0x62ce7e72, 0x4c71, 0x4d20, { 0xb1, 0x5d, 0x45, 0x28, 0x31, 0xa8, 0x7d, 0x9d } }"
assert t.count(o) == 1
t = t.replace(o, n)
o2 = "({62CE7E72-4C02-4ADB-A8FD-DFB5439C09D6})"
n2 = "({62CE7E72-4C71-4D20-B15D-452831A87D9D}, verified in HKCR)"
assert t.count(o2) == 1
t = t.replace(o2, n2)
open(p, "w", encoding="utf-8").write(t)
print("guid corrected")