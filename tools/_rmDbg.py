path = 'D:/consoles/ns/hayarigami-recomp/framework/runtime/ov_movie.c'
t = open(path, encoding='utf-8').read()
a1 = 'static int mf_dbg_n;   // the first few ProcessOutput results are logged once, to pin down the contract\n'
assert t.count(a1) == 1
t = t.replace(a1, '')
a2 = '''        if (mf_dbg_n < 12) {\n            mf_dbg_n++;\n            rt_log(\"movie: ProcessOutput -> %#lx status %#lx flags %#lx cbSize %lu sample %p\", (unsigned long)hr,\n                   (unsigned long)st, (unsigned long)oi.dwFlags, (unsigned long)oi.cbSize, (void *)ob.pSample);\n        }\n'''
assert t.count(a2) == 1, t.count(a2)
t = t.replace(a2, '')
open(path, 'w', encoding='utf-8').write(t)
print('probe removed')