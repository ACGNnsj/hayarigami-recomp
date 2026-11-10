p = "D:/consoles/ns/hayarigami-recomp/tools/_mp4e.py"
ls = open(p, encoding="utf-8").read().split(chr(10))
idx = [i for i, x in enumerate(ls) if "children(st[" in x]
assert len(idx) == 1, idx
ls[idx[0]] = "    has_avc = (t0 == traks[0])"
open(p, "w", encoding="utf-8").write(chr(10).join(ls))
print("fixed at", idx[0])