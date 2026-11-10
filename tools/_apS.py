p = 'D:/consoles/ns/hayarigami-recomp/tools/test_mf.c'
t = open(p, encoding='utf-8').read()
t = t.replace('f = fopen("build/v0/packets.bin", "rb");', 'f = fopen("build/v0/pk_annexb.bin", "rb");\n    printf("packets fopen %p\\n", (void *)f);')
t = t.replace('        if (fread(&n, 4, 1, f) != 1) break;', '        size_t rd = fread(&n, 4, 1, f);\n        if (rd != 1) { if (fed == 0) printf("first read=%zu feof=%d ferror=%d\\n", rd, feof(f), ferror(f)); break; }')
open(p, 'w', encoding='utf-8').write(t)
print('patched test')