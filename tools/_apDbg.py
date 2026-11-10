path = 'D:/consoles/ns/hayarigami-recomp/framework/runtime/ov_movie.c'
t = open(path, encoding='utf-8').read()
old1 = 'static HRESULT mf_out(Movie *m, uint8_t *dst, int w, int h, int *got) {'
new1 = 'static int mf_dbg_n;   // the first few ProcessOutput results are logged once, to pin down the contract\nstatic HRESULT mf_out(Movie *m, uint8_t *dst, int w, int h, int *got) {'
assert t.count(old1) == 1
t = t.replace(old1, new1)
old2 = '        HRESULT hr = m->mf->lpVtbl->ProcessOutput(m->mf, 0, 1, &ob, &st);'
new2 = '''        HRESULT hr = m->mf->lpVtbl->ProcessOutput(m->mf, 0, 1, &ob, &st);\n        if (mf_dbg_n < 12) {\n            mf_dbg_n++;\n            rt_log(\"movie: ProcessOutput -> %#lx status %#lx flags %#lx cbSize %lu sample %p\", (unsigned long)hr,\n                   (unsigned long)st, (unsigned long)oi.dwFlags, (unsigned long)oi.cbSize, (void *)ob.pSample);\n        }'''
assert t.count(old2) == 1
t = t.replace(old2, new2)
open(path, 'w', encoding='utf-8').write(t)
print('probe in')