base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "framework/runtime/ov_movie.c"
t = open(p, encoding="utf-8").read()
blk = open(base + "tools/_mfc2.txt", encoding="utf-8").read()
old = "    if (m->mf_is_avc && !mf_read_csd(c, md, m))" + chr(10) + "        rt_log(\"movie: no usable csd-0 avcC; the SPS/PPS are collected from the stream instead\");"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, blk)
open(p, "w", encoding="utf-8").write(t)
print("gated csd applied")