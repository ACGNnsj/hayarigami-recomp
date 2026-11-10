import sys
base = 'D:/consoles/ns/hayarigami-recomp/'
def load(path):
    raw = open(base + path, 'rb').read()
    crlf = b'\r\n' in raw
    return raw.decode('utf-8').replace('\r\n', '\n'), crlf
def save(path, t, crlf):
    enc = t.replace('\n', '\r\n') if crlf else t
    open(base + path, 'wb').write(enc.encode('utf-8'))
def patch(path, pairs):
    t, crlf = load(path)
    for old, new in pairs:
        c = t.count(old)
        assert c == 1, (path, repr(old[:70]), c)
        t = t.replace(old, new)
    save(path, t, crlf)
    print(path, len(pairs), 'edits ok')
F1A_OLD = 't0 = kern_now_ns();\n            e = vpx_codec_decode'
F1A_NEW = 't0 = kern_now_ns();\n            if (m->mf_is_avc) {\n                if (!m->mf_thread_init) { mf_startup(); m->mf_thread_init = 1; }\n                {\n                const uint8_t *data = m->in[p.index] + p.offset;\n                size_t size = (size_t)p.size;\n                if (!m->mf_ready && !m->mf_broken) {\n                    mf_collect_seq(m, data, size);\n                    m->mf_pre++;\n                    if ((m->mf_have_sps && m->mf_have_pps) || m->mf_pre >= 64) mf_configure_mft(m);\n                }\n                if (m->mf_broken) failed = 1;\n                else if (m->mf_ready) {\n                    mf_hr = mf_in(m, data, size);\n                    if (SUCCEEDED(mf_hr)) mf_hr = mf_out(m, dst, w, h, &got);\n                    failed = FAILED(mf_hr);\n                }\n                }\n            } else {\n            e = vpx_codec_decode'