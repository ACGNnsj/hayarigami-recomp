base = "D:/consoles/ns/hayarigami-recomp/"
raw = open(base + "framework/runtime/ov_movie.c", "rb").read()
crlf = b"\r\n" in raw
t = raw.decode("utf-8").replace("\r\n", "\n")
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:64]), t.count(old))
    t = t.replace(old, new)
rep('    int stub = type != MOVIE_TYPE_VP9 && stub_on();', '    int host = type == MOVIE_TYPE_VP9 || type == MOVIE_TYPE_AVC;\\n    int stub = !host && stub_on();')
rep('    if ((type != MOVIE_TYPE_VP9 && !stub) || host_off()) {', '    if ((!host && !stub) || host_off()) {')
rep('    m->stub = stub;', '    m->stub = stub;\\n    m->mf_is_avc = !stub && type == MOVIE_TYPE_AVC;')
rep('(AVC video, AAC audio) consumes its input', '(AAC audio and the like) consumes its input')
rep('// movie::Decoder for VP9 on the host with libvpx (BSD-3-Clause, linked statically).', '// movie::Decoder on the host: VP9 with libvpx (BSD-3-Clause, linked statically), AVC/H.264 Annex B with the inbox\\n// Media Foundation decoder.')
rep('stub ? "stub" : "VP9",', 'stub ? "stub" : type == MOVIE_TYPE_AVC ? "AVC" : "VP9",')
rep('if (!mime || strcmp(mime, "video/x-vnd.on2.vp9") || w <= 0', 'if ((!mime || (strcmp(mime, "video/x-vnd.on2.vp9") && mime && strcmp(mime, "video/avc"))) || w <= 0')
rep('    if (!vpx_open(m)) rt_fatal("movie: libvpx VP9 decoder initialisation");', '    m->mf_is_avc = mime && !strcmp(mime, "video/avc");\\n    if (m->mf_is_avc) {\\n        if (!mf_open(m)) rt_fatal("movie: H.264 MFT creation");\\n    } else if (!vpx_open(m)) rt_fatal("movie: libvpx VP9 decoder initialisation");')
rep('%dx%d VP9, %d input buffers', '%dx%d %s, %d input buffers')
rep('", w, h, IN_BUFS,', '", w, h, m->mf_is_avc ? "AVC (Media Foundation)" : "VP9", IN_BUFS,')
assert t.count('!(m->started && m->vpx_live') == 2
t = t.replace('!(m->started && m->vpx_live', '!(m->started && (m->vpx_live || m->mf_live)')
enc = t.replace('\\n', '\\r\\n') if crlf else t
open(base + 'framework/runtime/ov_movie.c', 'wb').write(enc.encode('utf-8'))
print('apF applied')