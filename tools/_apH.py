base = "D:/consoles/ns/hayarigami-recomp/"
t = open(base + "framework/runtime/ov_movie.c", encoding="utf-8").read()
old = 'mime && !strcmp(mime, "video/avc");\\n    if (m->mf_is_avc) {\\n        if (!mf_open(m)) rt_fatal("movie: H.264 MFT creation");\\n    } else if (!vpx_open(m))'
new = 'mime && !strcmp(mime, "video/avc");\n    if (m->mf_is_avc) {\n        if (!mf_open(m)) rt_fatal("movie: H.264 MFT creation");\n    } else if (!vpx_open(m))'
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new)
open(base + "framework/runtime/ov_movie.c", "w", encoding="utf-8").write(t)
print("P fixed")