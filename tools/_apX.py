p = 'D:/consoles/ns/hayarigami-recomp/tools/test_mf.c'
t = open(p, encoding='utf-8').read()
t = t.replace('    f = fopen("build/v0/pk_annexb.bin", "rb");', '    f = fopen(argc > 3 ? argv[3] : "build/v0/pk_annexb.bin", "rb");')
t = t.replace('    IMFMediaType *in = make_in(w, h, seq, use_seq ? seqn : 0);', '    IMFMediaType *in = make_in(w, h, seq, use_seq ? seqn : 0);')
open(p, 'w', encoding='utf-8').write(t)
print('argv3 ok')