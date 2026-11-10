path = 'D:/consoles/ns/hayarigami-recomp/framework/runtime/ov_movie.c'
t = open(path, encoding='utf-8').read()
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:70]), t.count(old))
    t = t.replace(old, new)
rep('        m->mf->lpVtbl->ProcessMessage(m->mf, MFT_MESSAGE_NOTIFY_BEGIN_STREAMING, 0);', '        m->mf->lpVtbl->ProcessMessage(m->mf, MFT_MESSAGE_NOTIFY_BEGIN_STREAMING, 0);' + chr(10) + '        // Without START_OF_STREAM this decoder accepts every sample and emits nothing at all.' + chr(10) + '        m->mf->lpVtbl->ProcessMessage(m->mf, MFT_MESSAGE_NOTIFY_START_OF_STREAM, 0);')
rep('static HRESULT mf_in(Movie *m, const uint8_t *d, size_t n) {', 'static HRESULT mf_in(Movie *m, const uint8_t *d, size_t n, int64_t time_us) {')
rep('    if (SUCCEEDED(hr)) hr = s->lpVtbl->AddBuffer(s, buf);', '    if (SUCCEEDED(hr)) hr = s->lpVtbl->AddBuffer(s, buf);' + chr(10) + '    if (SUCCEEDED(hr) && time_us > 0) hr = s->lpVtbl->SetSampleTime(s, time_us * 10);   // 100 ns units')
rep('                    mf_hr = mf_in(m, data, size);', '                    mf_hr = mf_in(m, data, size, p.time);')
open(path, 'w', encoding='utf-8').write(t)
print('start_of_stream + timestamps')