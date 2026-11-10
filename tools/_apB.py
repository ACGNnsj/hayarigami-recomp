base = "D:/consoles/ns/hayarigami-recomp/"
raw = open(base + "framework/runtime/ov_movie.c", "rb").read()
crlf = b"\r\n" in raw
t = raw.decode("utf-8").replace("\r\n", "\n")
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:64]), t.count(old))
    t = t.replace(old, new)
rep("    int stub = type != MOVIE_TYPE_VP9 && stub_on();", "    int host = type == MOVIE_TYPE_VP9 || type == MOVIE_TYPE_AVC;\n    int stub = !host && stub_on();")
rep("    if ((type != MOVIE_TYPE_VP9 && !stub) || host_off()) {", "    if ((!host && !stub) || host_off()) {")
rep("    m->stub = stub;", "    m->stub = stub;\n    m->mf_is_avc = !stub && type == MOVIE_TYPE_AVC;")
rep("(AVC video, AAC audio) consumes its input", "(AAC audio and the like) consumes its input")
rep("// movie::Decoder for VP9 on the host with libvpx (BSD-3-Clause, linked statically).", "// movie::Decoder on the host: VP9 with libvpx (BSD-3-Clause, linked statically), AVC/H.264 Annex B with the inbox\n// Media Foundation decoder.")