base = 'D:/consoles/ns/hayarigami-recomp/'
path = base + 'framework/runtime/ov_movie.c'
t = open(path, encoding='utf-8').read()
A = open(base + 'tools/_mfA.txt', encoding='utf-8').read()
B = open(base + 'tools/_mfB.txt', encoding='utf-8').read()
C = open(base + 'tools/_mfC.txt', encoding='utf-8').read()
def swap(start_marker, end_marker, body):
    global t
    i = t.index(start_marker)
    j = t.index(end_marker, i)
    t = t[:i] + body + chr(10) + t[j:]
# 1. output type negotiation
swap('static int mf_set_output(Movie *m) {', chr(10) + 'static void mf_configure_mft(', A)
# 2. input feeder (in-band sequence header)
swap('static HRESULT mf_in(Movie *m', chr(10) + 'static HRESULT mf_out(', B)
# 3. output sample allocation + copy-out
swap('static HRESULT mf_out(Movie *m', '// The avcC record of the movie', C)
# 4. drop the blob that this decoder silently ignores
old = '    if (SUCCEEDED(hr) && seq && seqlen) hr = t->lpVtbl->SetBlob(t, &MF_MT_MPEG_SEQUENCE_HEADER, seq, (UINT32)seqlen);'
assert t.count(old) == 1
t = t.replace(old, '    // The sequence header is prepended to the first sample instead of being carried on the type: with the' + chr(10) + '    // blob set, this decoder accepts every packet and emits nothing.' + chr(10) + '    (void)seq;' + chr(10) + '    (void)seqlen;')
# 5. struct fields
old2 = '    int mf_live, mf_is_avc, mf_ready, mf_broken, mf_have_sps, mf_have_pps, mf_pre, mf_thread_init, mf_warned;'
assert t.count(old2) == 1
t = t.replace(old2, old2 + chr(10) + '    int mf_out_w, mf_out_h, mf_fed_first;   // geometry the decoder chose, and whether it has seen its first sample')
# 6. reset them with the rest
old3 = '    m->mf_pre = m->mf_thread_init = m->mf_warned = 0;'
assert t.count(old3) == 1
t = t.replace(old3, old3 + chr(10) + '    m->mf_out_w = m->mf_out_h = m->mf_fed_first = 0;')
open(path, 'w', encoding='utf-8').write(t)
print('movie patch applied')