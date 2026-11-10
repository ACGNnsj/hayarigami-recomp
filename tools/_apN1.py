base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "framework/runtime/ov_movie.c"
t = open(p, encoding="utf-8").read()
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:64]), t.count(old))
    t = t.replace(old, new)
rep('static MovieGuest G;', 'static MovieGuest G;\nstatic uint64_t g_md_find_pointer, g_md_find_size;   // NnMediaData csd access')
rep('G.md_find_string = need("_ZNK5movie9MediaData10FindStringEPKcPS2_");', 'G.md_find_string = need("_ZNK5movie9MediaData10FindStringEPKcPS2_");\n        g_md_find_pointer = need("_ZNK5movie11NnMediaData11FindPointerEPKcPPv");\n        g_md_find_size = need("_ZNK5movie11NnMediaData8FindSizeEPKcPm");')
open(p, 'w', encoding='utf-8').write(t)
print('N1 applied')