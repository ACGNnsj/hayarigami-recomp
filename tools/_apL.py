base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "framework/runtime/ov_movie.c"
t = open(p, encoding="utf-8").read()
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:64]), t.count(old))
    t = t.replace(old, new)
rep('    if (m->format != MOVIE_FORMAT_NV12) {', '    // Format 4 is this title NV12: the same packed layout.\n    if (m->format != MOVIE_FORMAT_NV12 && m->format != 4) {')
rep('(NV12 = %d only)', '(NV12 = %d or 4)')
rep('stub ? "skipped, no decoding" : vpx_codec_version_str(), type, format', 'stub ? "skipped, no decoding" : type == MOVIE_TYPE_AVC ? "Media Foundation" : vpx_codec_version_str(), type, format')
open(p, 'w', encoding='utf-8').write(t)
print('gate open + log')