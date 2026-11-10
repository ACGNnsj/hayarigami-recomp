base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "framework/runtime/ov_movie.c"
t = open(p, encoding="utf-8").read()
chunk = open(base + "tools/_mfc1.txt", encoding="utf-8").read().replace(chr(10) + "/ ", chr(10) + "// ")
assert "mf_read_csd" in chunk
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:70]), t.count(old))
    t = t.replace(old, new)
rep("static int vpx_open(Movie *m) {", chunk + chr(10) + chr(10) + "static int vpx_open(Movie *m) {")
rep('G.md_find_string = need("_ZNK5movie9MediaData10FindStringEPKcPS2_");', 'G.md_find_string = need("_ZNK5movie9MediaData10FindStringEPKcPS2_");' + chr(10) + '        g_md_find_pointer = need("_ZNK5movie11NnMediaData11FindPointerEPKcPPv");' + chr(10) + '        g_md_find_size = need("_ZNK5movie11NnMediaData8FindSizeEPKcPm");')
rep('    } else if (!vpx_open(m)) rt_fatal("movie: libvpx VP9 decoder initialisation");', '    } else if (!vpx_open(m)) rt_fatal("movie: libvpx VP9 decoder initialisation");' + chr(10) + '    if (m->mf_is_avc && !mf_read_csd(c, md, m))' + chr(10) + '        rt_log("movie: no usable csd-0 avcC; the SPS/PPS are collected from the stream instead");')
open(p, "w", encoding="utf-8").write(t)
print("csd patch applied")