base = "D:/consoles/ns/hayarigami-recomp/"
p = base + "framework/runtime/ov_movie.c"
t = open(p, encoding="utf-8").read()
def rep(old, new):
    global t
    assert t.count(old) == 1, (repr(old[:64]), t.count(old))
    t = t.replace(old, new)
rep('#include <wmcodecdsp.h>', '// CLSID_CMSH264DecoderMFT ({62CE7E72-4C02-4ADB-A8FD-DFB5439C09D6}), defined here: the GUID is absent from\n// libmfuuid.a (which holds only the older CLSID_MSH264DecoderMFT).\nstatic const GUID MF_CLSID_H264_DECODER = { 0x62ce7e72, 0x4c02, 0x4adb, { 0xa8, 0xfd, 0xdf, 0xb5, 0x43, 0x9c, 0x09, 0xd6 } };')
rep('&CLSID_CMSH264DecoderMFT', '&MF_CLSID_H264_DECODER')
open(p, 'w', encoding='utf-8').write(t)
print('guid localized')