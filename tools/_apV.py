p = 'D:/consoles/ns/hayarigami-recomp/tools/test_mf.c'
t = open(p, encoding='utf-8').read()
old = '    fclose(f);'
new = '    fclose(f);\n    printf("draining\\n");\n    mft->lpVtbl->ProcessMessage(mft, MFT_MESSAGE_NOTIFY_END_OF_STREAM, 0);\n    mft->lpVtbl->ProcessMessage(mft, MFT_MESSAGE_COMMAND_DRAIN, 0);\n    for (int k = 0; k < 400; k++) {\n        MFT_OUTPUT_DATA_BUFFER ob; DWORD st = 0;\n        IMFSample *own = NULL; IMFMediaBuffer *ownb = NULL;\n        memset(&ob, 0, sizeof ob);\n        MFCreateSample(&own);\n        MFCreateMemoryBuffer(oi.cbSize, &ownb);\n        own->lpVtbl->AddBuffer(own, ownb);\n        ob.pSample = own;\n        HRESULT o = mft->lpVtbl->ProcessOutput(mft, 0, 1, &ob, &st);\n        if (o == MF_E_TRANSFORM_NEED_MORE_INPUT) { printf("drain %d: need more input\\n", k); own->lpVtbl->Release(own); ownb->lpVtbl->Release(ownb); break; }\n        if (FAILED(o)) { printf("drain %d: %#lx\\n", k, (unsigned long)o); own->lpVtbl->Release(own); ownb->lpVtbl->Release(ownb); break; }\n        frames++;\n        own->lpVtbl->Release(own); ownb->lpVtbl->Release(ownb);\n    }'
assert t.count(old) == 1
t = t.replace(old, new)
open(p, 'w', encoding='utf-8').write(t)
print('drain added')