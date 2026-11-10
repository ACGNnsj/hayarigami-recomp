p = 'D:/consoles/ns/hayarigami-recomp/tools/test_mf.c'
t = open(p, encoding='utf-8').read()
old = '    int frames = 0, fed = 0;'
new = '''    MFT_OUTPUT_STREAM_INFO oi;\n    memset(&oi, 0, sizeof oi);\n    HRESULT hri = mft->lpVtbl->GetOutputStreamInfo(mft, 0, &oi);\n    printf("GetOutputStreamInfo %#lx flags %#lx size %lu\n", (unsigned long)hri, (unsigned long)oi.dwFlags, (unsigned long)oi.cbSize);\n    int frames = 0, fed = 0;'''
assert t.count(old) == 1
t = t.replace(old, new)
old2 = '''            MFT_OUTPUT_DATA_BUFFER ob; DWORD st = 0;\n            memset(&ob, 0, sizeof ob);'''
new2 = '''            MFT_OUTPUT_DATA_BUFFER ob; DWORD st = 0;\n            memset(&ob, 0, sizeof ob);\n            IMFMediaBuffer *own = NULL; IMFSample *owns = NULL;\n            if (!(oi.dwFlags & MFT_OUTPUT_STREAM_PROVIDES_SAMPLES)) {\n                MFCreateSample(&owns);\n                MFCreateMemoryBuffer(oi.cbSize ? oi.cbSize : 3110400, &own);\n                owns->lpVtbl->AddBuffer(owns, own);\n                ob.pSample = owns;\n            }'''
assert t.count(old2) == 1
t = t.replace(old2, new2)
old3 = '''            if (FAILED(o) || !ob.pSample) { printf("out %#lx\\n", (unsigned long)o); break; }'''
new3 = '''            if (FAILED(o) || !ob.pSample) { printf("out %#lx\\n", (unsigned long)o); if (owns) owns->lpVtbl->Release(owns); if (own) own->lpVtbl->Release(own); break; }'''
assert t.count(old3) == 1
t = t.replace(old3, new3)
open(p, 'w', encoding='utf-8').write(t)
print('output-info patch ok')