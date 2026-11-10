p = 'D:/consoles/ns/hayarigami-recomp/tools/test_mf.c'
t = open(p, encoding='utf-8').read()
t = t.replace('if (frames == 0) { FILE *g = fopen("build/v0/frame0.nv12", "wb");', 'if (frames == 200) { FILE *g = fopen("build/v0/frame200.nv12", "wb");')
open(p, 'w', encoding='utf-8').write(t)
print('dump 200')