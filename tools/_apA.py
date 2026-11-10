base = "D:/consoles/ns/hayarigami-recomp/"
raw = open(base + "framework/runtime/ov_movie.c", "rb").read()
crlf = b"\r\n" in raw
t = raw.decode("utf-8").replace("\r\n", "\n")
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:60]), t.count(old))
    t = t.replace(old, new)
rep("t0 = kern_now_ns();\n            e = vpx_codec_decode",
"t0 = kern_now_ns();\n            if (m->mf_is_avc) {\n                if (!m->mf_thread_init) { mf_startup(); m->mf_thread_init = 1; }\n                {\n                const uint8_t *data = m->in[p.index] + p.offset;\n                size_t size = (size_t)p.size;\n                if (!m->mf_ready && !m->mf_broken) {\n                    mf_collect_seq(m, data, size);\n                    m->mf_pre++;\n                    if ((m->mf_have_sps && m->mf_have_pps) || m->mf_pre >= 64) mf_configure_mft(m);\n                }\n                if (m->mf_broken) failed = 1;\n                else if (m->mf_ready) {\n                    mf_hr = mf_in(m, data, size);\n                    if (SUCCEEDED(mf_hr)) mf_hr = mf_out(m, dst, w, h, &got);\n                    failed = FAILED(mf_hr);\n                }\n                }\n            } else {\n            e = vpx_codec_decode")
rep("                    got++;\n                }\n            }\n            dt = kern_now_ns() - t0;",
"                    got++;\n                }\n            }\n                failed = e != VPX_CODEC_OK;\n            }\n            dt = kern_now_ns() - t0;")
rep("            if (e != VPX_CODEC_OK || !got) {", "            if (failed || !got) {")
rep("                if (e != VPX_CODEC_OK) {", "                if (failed) {")