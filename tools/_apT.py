p = 'D:/consoles/ns/hayarigami-recomp/tools/test_mf.c'
t = open(p, encoding='utf-8').read()
t = t.replace('        if (fread(d, 1, n, f) != n) { free(d); break; }', '        size_t rd2 = fread(d, 1, n, f);\n        if (fed == 0) printf("n=%u rd2=%zu feof=%d ferror=%d\\n", n, rd2, feof(f), ferror(f));\n        if (rd2 != n) { free(d); break; }')
open(p, 'w', encoding='utf-8').write(t)
print('patched2')