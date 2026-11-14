#include <stdio.h>
#include <windows.h>
#include <mfapi.h>
#include <mfidl.h>
#include <mfreadwrite.h>
#include <mferror.h>
int main(int argc, char **argv) {
    CoInitializeEx(NULL, COINIT_MULTITHREADED);
    MFStartup(MF_VERSION, MFSTARTUP_FULL);
    IMFSourceReader *rd = NULL;
    const wchar_t *path = L"build\\v0\\test2.264";
    IMFAttributes *at = NULL;
    MFCreateAttributes(&at, 2);
    at->lpVtbl->SetUINT32(at, &MF_SOURCE_READER_ENABLE_VIDEO_PROCESSING, 1);
    HRESULT hr = MFCreateSourceReaderFromURL(path, at, &rd);
    printf("create reader %#lx\n", (unsigned long)hr);
    if (FAILED(hr)) return 1;
    IMFMediaType *t = NULL;
    MFCreateMediaType(&t);
    t->lpVtbl->SetGUID(t, &MF_MT_MAJOR_TYPE, &MFMediaType_Video);
    t->lpVtbl->SetGUID(t, &MF_MT_SUBTYPE, &MFVideoFormat_NV12);
    hr = rd->lpVtbl->SetCurrentMediaType(rd, MF_SOURCE_READER_FIRST_VIDEO_STREAM, NULL, t);
    printf("set type %#lx\n", (unsigned long)hr);
    t->lpVtbl->Release(t);
    int frames = 0;
    for (int i = 0; i < 400; i++) {
        DWORD flags = 0; LONGLONG ts = 0; IMFSample *s = NULL;
        hr = rd->lpVtbl->ReadSample(rd, MF_SOURCE_READER_FIRST_VIDEO_STREAM, 0, NULL, &flags, &ts, &s);
        if (FAILED(hr)) { printf("read %d: %#lx\n", i, (unsigned long)hr); break; }
        if (flags & MF_SOURCE_READERF_ENDOFSTREAM) { printf("eos\n"); break; }
        if (s) { frames++; if (frames <= 3) printf("frame %d ts=%lld\n", frames, (long long)ts); s->lpVtbl->Release(s); }
    }
    printf("frames %d\n", frames);
    return 0;
}