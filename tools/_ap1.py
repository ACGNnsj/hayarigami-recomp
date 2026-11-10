import sys
base = 'D:/consoles/ns/hayarigami-recomp/'
def load(path):
    with open(base + path, 'rb') as f: raw = f.read()
    crlf = b'\r\n' in raw
    return raw.decode('utf-8').replace('\r\n', '\n'), crlf
def save(path, t, crlf):
    if crlf: t = t.replace('\n', '\r\n')
    with open(base + path, 'wb') as f: f.write(t.encode('utf-8'))
def patch(path, pairs):
    t, crlf = load(path)
    for old, new in pairs:
        c = t.count(old)
        assert c == 1, (path, old[:70], c)
        t = t.replace(old, new)
    save(path, t, crlf)
    print(path, len(pairs), 'edits ok, crlf=' + str(crlf))
chunks = []
for i in ['1', '2', '3', '4', '5']:
    with open(base + 'tools/_mfb' + i + '.txt', 'r', newline='') as f: chunks.append(f.read())
MF = ''.join(chunks)
assert 'mf_out(Movie *m' in MF and len(MF) > 8000, len(MF)
patch('framework/runtime/movie.h', [
    ('enum { MOVIE_TYPE_VP9 = 3,', 'enum { MOVIE_TYPE_AVC = 1, MOVIE_TYPE_VP9 = 3,'),
])
patch('framework/runtime/ov_movie.c', [
    ('#include <vpx/vpx_decoder.h>', '#include <vpx/vpx_decoder.h>\n\n#include <mfapi.h>\n#include <mferror.h>\n#include <mfidl.h>\n#include <mftransform.h>\n#include <objbase.h>\n#include <wmcodecdsp.h>'),
    ('    vpx_codec_ctx_t vpx;\n    int vpx_live;', '    vpx_codec_ctx_t vpx;\n    int vpx_live;\n    IMFTransform *mf;\n    int mf_live, mf_is_avc, mf_ready, mf_broken, mf_have_sps, mf_have_pps, mf_pre, mf_thread_init, mf_warned;\n    uint8_t *mf_seq;\n    size_t mf_seq_len, mf_seq_cap;'),
    ('static int vpx_open(Movie *m) {', MF + 'static int vpx_open(Movie *m) {'),
    ('        vpx_codec_err_t e = VPX_CODEC_OK;\n        const char *bad = NULL;', '        vpx_codec_err_t e = VPX_CODEC_OK;\n        const char *bad = NULL;\n        int failed = 0;\n        HRESULT mf_hr = S_OK;'),
    ('        vpx_codec_destroy(&m->vpx);\n        m->vpx_live = 0;\n    }', '        vpx_codec_destroy(&m->vpx);\n        m->vpx_live = 0;\n    }\n    mf_close(m);'),
])
patch('tools/build_haya.sh', [
    ('-l:libvpx.a -l:libzstd.a', '-l:libvpx.a -lmfplat -lmfuuid -lole32 -l:libzstd.a'),
])
print('applier1 done')