base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "framework/runtime/ov_movie.c"
t = open(p, encoding="utf-8").read()
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:70]), t.count(old))
    t = t.replace(old, new)
decl = "static uint64_t g_md_find_pointer, g_md_find_size;   // NnMediaData csd access (the concrete type behind Configure's format)"
rep(decl + chr(10), "")
rep("static MovieGuest G;", "static MovieGuest G;" + chr(10) + decl)
open(p, "w", encoding="utf-8").write(t)
print("statics hoisted")