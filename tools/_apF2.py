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