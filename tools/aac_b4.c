#include <windows.h>
#include <mfapi.h>
#include <mftransform.h>
#include <mferror.h>
#include <initguid.h>
#include <wmcodecdsp.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
static IMFTransform *M;
static long long feedOneTs(const uint8_t *d, int len, LONGLONG ts) {
    IMFMediaBuffer *b = NULL; IMFSample *s = NULL;
    HRESULT hr = MFCreateMemoryBuffer((DWORD)len, &b);
    BYTE *p = NULL;
    if (SUCCEEDED(hr)) hr = b->lpVtbl->Lock(b, &p, NULL, NULL);
    if (SUCCEEDED(hr)) { memcpy(p, d, len); hr = b->lpVtbl->Unlock(b); }
    if (SUCCEEDED(hr)) hr = b->lpVtbl->SetCurrentLength(b, (DWORD)len);
    if (SUCCEEDED(hr)) hr = MFCreateSample(&s);
    if (SUCCEEDED(hr)) hr = s->lpVtbl->AddBuffer(s, b);
    if (SUCCEEDED(hr)) hr = s->lpVtbl->SetSampleTime(s, ts);
    if (SUCCEEDED(hr)) hr = M->lpVtbl->ProcessInput(M, 0, s, 0);
    if (s) s->lpVtbl->Release(s);
    if (b) b->lpVtbl->Release(b);
    return (long long)hr;
}
static long long feedOne(const uint8_t *d, int len) {
    IMFMediaBuffer *b = NULL; IMFSample *s = NULL;
    HRESULT hr = MFCreateMemoryBuffer((DWORD)len, &b);
    BYTE *p = NULL;
    if (SUCCEEDED(hr)) hr = b->lpVtbl->Lock(b, &p, NULL, NULL);
    if (SUCCEEDED(hr)) { memcpy(p, d, len); hr = b->lpVtbl->Unlock(b); }
    if (SUCCEEDED(hr)) hr = b->lpVtbl->SetCurrentLength(b, (DWORD)len);
    if (SUCCEEDED(hr)) hr = MFCreateSample(&s);
    if (SUCCEEDED(hr)) hr = s->lpVtbl->AddBuffer(s, b);
    if (SUCCEEDED(hr)) hr = M->lpVtbl->ProcessInput(M, 0, s, 0);
    if (s) s->lpVtbl->Release(s);
    if (b) b->lpVtbl->Release(b);
    return (long long)hr;
}
static int drainOne(FILE *w, long *pcm) {
    MFT_OUTPUT_STREAM_INFO oi; memset(&oi, 0, sizeof oi);
    M->lpVtbl->GetOutputStreamInfo(M, 0, &oi);
    MFT_OUTPUT_DATA_BUFFER ob; memset(&ob, 0, sizeof ob); DWORD st = 0;
    IMFSample *os = NULL; IMFMediaBuffer *obf = NULL;
    if (!(oi.dwFlags & MFT_OUTPUT_STREAM_PROVIDES_SAMPLES)) {
        DWORD need = oi.cbSize ? oi.cbSize : 32768;
        if (SUCCEEDED(MFCreateSample(&os)) && SUCCEEDED(MFCreateMemoryBuffer(need, &obf)) &&
            SUCCEEDED(os->lpVtbl->AddBuffer(os, obf))) ob.pSample = os;
    }
    HRESULT hr = M->lpVtbl->ProcessOutput(M, 0, 1, &ob, &st);
    int got = 0;
    if (hr == MF_E_TRANSFORM_NEED_MORE_INPUT) got = -1;
    else if (SUCCEEDED(hr)) {
        IMFMediaBuffer *g = NULL;
        if (os) ob.pSample->lpVtbl->GetBufferByIndex(ob.pSample, 0, &g);
        else if (ob.pSample) ob.pSample->lpVtbl->ConvertToContiguousBuffer(ob.pSample, &g);
        if (g) {
            BYTE *p = NULL; DWORD cur = 0;
            if (SUCCEEDED(g->lpVtbl->Lock(g, &p, NULL, NULL))) {
                g->lpVtbl->GetCurrentLength(g, &cur);
                if (cur && w) { fwrite(p, 1, cur, w); *pcm += cur; }
                got = (int)cur;
                g->lpVtbl->Unlock(g);
            }
            g->lpVtbl->Release(g);
        }
    } else got = -2;
    if (os) { os->lpVtbl->Release(os); obf->lpVtbl->Release(obf); }
    else if (ob.pSample) ob.pSample->lpVtbl->Release(ob.pSample);
    return got;
}
#include <processthreadsapi.h>
typedef struct { const uint8_t *d; long N; int id; long *fed; long *pcm; } TH;
static DWORD WINAPI thfn(LPVOID p) {
    TH *t = (TH*)p;
    CoInitializeEx(NULL, COINIT_MULTITHREADED);
    IMFTransform *M = NULL;
    CoCreateInstance(&CLSID_CMSAACDecMFT, NULL, CLSCTX_INPROC_SERVER, &IID_IMFTransform, (void**)&M);
    IMFMediaType *it = NULL; M->lpVtbl->GetInputAvailableType(M, 0, 2, &it);
    it->lpVtbl->SetUINT32(it, &MF_MT_AUDIO_NUM_CHANNELS, 2);
    it->lpVtbl->SetUINT32(it, &MF_MT_AUDIO_SAMPLES_PER_SECOND, 48000);
    it->lpVtbl->SetUINT32(it, &MF_MT_AAC_PAYLOAD_TYPE, 1);
    M->lpVtbl->SetInputType(M, 0, it, 0); it->lpVtbl->Release(it);
    IMFMediaType *o = NULL; MFCreateMediaType(&o);
    o->lpVtbl->SetGUID(o, &MF_MT_MAJOR_TYPE, &MFMediaType_Audio);
    o->lpVtbl->SetGUID(o, &MF_MT_SUBTYPE, &MFAudioFormat_PCM);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_NUM_CHANNELS, 2);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_SAMPLES_PER_SECOND, 48000);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_BITS_PER_SAMPLE, 16);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_BLOCK_ALIGNMENT, 4);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_AVG_BYTES_PER_SECOND, 192000);
    M->lpVtbl->SetOutputType(M, 0, o, 0); o->lpVtbl->Release(o);
    M->lpVtbl->ProcessMessage(M, MFT_MESSAGE_NOTIFY_BEGIN_STREAMING, 0);
    M->lpVtbl->ProcessMessage(M, MFT_MESSAGE_NOTIFY_START_OF_STREAM, 0);
    long q = 0, nf = 0; LONGLONG tt = 213333;
    while (q + 7 <= t->N && nf < 12) {
        if (t->d[q] != 0xFF || (t->d[q+1] & 0xF6) != 0xF0) break;
        int ln = ((t->d[q+3] & 3) << 11) | (t->d[q+4] << 3) | (t->d[q+5] >> 5);
        IMFMediaBuffer *b = NULL; IMFSample *s = NULL;
        HRESULT hx = MFCreateMemoryBuffer((DWORD)ln, &b);
        BYTE *pp = NULL;
        if (SUCCEEDED(hx)) hx = b->lpVtbl->Lock(b, &pp, NULL, NULL);
        if (SUCCEEDED(hx)) { memcpy(pp, t->d + q, ln); hx = b->lpVtbl->Unlock(b); }
        if (SUCCEEDED(hx)) hx = b->lpVtbl->SetCurrentLength(b, (DWORD)ln);
        if (SUCCEEDED(hx)) hx = MFCreateSample(&s);
        if (SUCCEEDED(hx)) hx = s->lpVtbl->AddBuffer(s, b);
        if (SUCCEEDED(hx)) hx = s->lpVtbl->SetSampleTime(s, tt);
        if (SUCCEEDED(hx)) hx = M->lpVtbl->ProcessInput(M, 0, s, 0);
        if (s) s->lpVtbl->Release(s);
        if (b) b->lpVtbl->Release(b);
        if (FAILED(hx)) { fprintf(stderr, "T%d frame %ld hr=%#lx\n", t->id, nf, (unsigned long)hx); break; }
        nf++; q += ln; tt += 213333;
        for (int dd = 0; dd < 8; dd++) {
            MFT_OUTPUT_DATA_BUFFER ob; memset(&ob, 0, sizeof ob); DWORD stx = 0;
            HRESULT hx2 = M->lpVtbl->ProcessOutput(M, 0, 1, &ob, &stx);
            if (hx2 == MF_E_TRANSFORM_NEED_MORE_INPUT) break;
            if (FAILED(hx2) || !ob.pSample) { if (ob.pSample) ob.pSample->lpVtbl->Release(ob.pSample); break; }
            IMFMediaBuffer *gg = NULL;
            ob.pSample->lpVtbl->ConvertToContiguousBuffer(ob.pSample, &gg);
            if (gg) { DWORD cl = 0; gg->lpVtbl->GetCurrentLength(gg, &cl); *(t->pcm) += cl; gg->lpVtbl->Release(gg); }
            ob.pSample->lpVtbl->Release(ob.pSample);
        }
    }
    *t->fed = nf;
    M->lpVtbl->Release(M);
    return 0;
}
int main(int argc, char **argv) {
    setvbuf(stderr, NULL, _IONBF, 0);
    const char *in = argv[1], *out = argv[2];
    int pay = argc > 3 ? atoi(argv[3]) : 0;
    FILE *f = fopen(in, "rb");
    fseek(f, 0, SEEK_END); long N = ftell(f); fseek(f, 0, SEEK_SET);
    uint8_t *d = malloc(N); fread(d, 1, N, f); fclose(f);
    CoInitializeEx(NULL, COINIT_MULTITHREADED);
    MFStartup(MF_VERSION, MFSTARTUP_FULL);
    if (argc > 7 && atoi(argv[7]) == 1) {
        IMFTransform *h264 = NULL;
        const GUID CLSID_H264 = {0x62CE7E72, 0x4C71, 0x4D20, {0xB1,0x5D,0x45,0x28,0x31,0xA8,0x7D,0x9D}};
        HRESULT hh = CoCreateInstance(&CLSID_H264, NULL, CLSCTX_INPROC_SERVER, &IID_IMFTransform, (void**)&h264);
        fprintf(stderr, "h264first %#lx\n", (unsigned long)hh);
        (void)h264;
    }
    HRESULT hr = CoCreateInstance(&CLSID_CMSAACDecMFT, NULL, CLSCTX_INPROC_SERVER, &IID_IMFTransform, (void**)&M);
    if (FAILED(hr)) { printf("MFT create %#lx\n", (unsigned long)hr); return 1; }
    IMFMediaType *t = NULL;
    for (int i = 0; i < 6; i++) {
        IMFMediaType *tt = NULL; HRESULT hh = M->lpVtbl->GetInputAvailableType(M, 0, i, &tt);
        if (FAILED(hh) || !tt) { fprintf(stderr, "avail[%d]: %#lx\n", i, (unsigned long)hh); continue; }
        GUID sub = {0}; UINT32 pay = 99, ch = 0, rate = 0, bits = 0;
        tt->lpVtbl->GetGUID(tt, &MF_MT_SUBTYPE, &sub);
        tt->lpVtbl->GetUINT32(tt, &MF_MT_AAC_PAYLOAD_TYPE, &pay);
        tt->lpVtbl->GetUINT32(tt, &MF_MT_AUDIO_NUM_CHANNELS, &ch);
        tt->lpVtbl->GetUINT32(tt, &MF_MT_AUDIO_SAMPLES_PER_SECOND, &rate);
        tt->lpVtbl->GetUINT32(tt, &MF_MT_AUDIO_BITS_PER_SAMPLE, &bits);
        uint8_t *ub = NULL; UINT32 usz = 0;
        if (SUCCEEDED(tt->lpVtbl->GetAllocatedBlob(tt, &MF_MT_USER_DATA, &ub, &usz))) { CoTaskMemFree(ub); }
        fprintf(stderr, "avail[%d]: sub=%08lx pay=%u ch=%u rate=%u bits=%u user=%u\n", i, (unsigned long)sub.Data1, pay, ch, rate, bits, usz);
        tt->lpVtbl->Release(tt);
    }
    { int ti = argc > 5 ? atoi(argv[5]) : 0; M->lpVtbl->GetInputAvailableType(M, 0, ti, &t); fprintf(stderr, "template=%d\n", ti); }
    t->lpVtbl->SetUINT32(t, &MF_MT_AUDIO_NUM_CHANNELS, 2);
    t->lpVtbl->SetUINT32(t, &MF_MT_AUDIO_SAMPLES_PER_SECOND, 48000);
    t->lpVtbl->SetUINT32(t, &MF_MT_AAC_PAYLOAD_TYPE, (UINT32)pay);
    { uint8_t *ub = NULL; UINT32 usz = 0;
      if (SUCCEEDED(t->lpVtbl->GetAllocatedBlob(t, &MF_MT_USER_DATA, &ub, &usz))) {
        fprintf(stderr, "userdata %u bytes: ", usz);
        for (UINT32 i = 0; i < usz; i++) fprintf(stderr, "%02x", ub[i]);
        fprintf(stderr, "\n"); CoTaskMemFree(ub);
      } }
    if (argc > 4 && atoi(argv[4]) == 1) { uint8_t asc[2] = {0x11, 0x90}; t->lpVtbl->SetBlob(t, &MF_MT_USER_DATA, asc, 2); fprintf(stderr, "ASC-blob\n"); }
    hr = M->lpVtbl->SetInputType(M, 0, t, 0); t->lpVtbl->Release(t);
    if (FAILED(hr)) { printf("in %#lx\n", (unsigned long)hr); return 1; }
    IMFMediaType *o = NULL; MFCreateMediaType(&o);
    o->lpVtbl->SetGUID(o, &MF_MT_MAJOR_TYPE, &MFMediaType_Audio);
    o->lpVtbl->SetGUID(o, &MF_MT_SUBTYPE, &MFAudioFormat_PCM);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_NUM_CHANNELS, 2);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_SAMPLES_PER_SECOND, 48000);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_BITS_PER_SAMPLE, 16);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_BLOCK_ALIGNMENT, 4);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_AVG_BYTES_PER_SECOND, 48000 * 4);
    hr = M->lpVtbl->SetOutputType(M, 0, o, 0); o->lpVtbl->Release(o);
    if (FAILED(hr)) { printf("out %#lx\n", (unsigned long)hr); return 1; }
    M->lpVtbl->ProcessMessage(M, MFT_MESSAGE_NOTIFY_BEGIN_STREAMING, 0);
    M->lpVtbl->ProcessMessage(M, MFT_MESSAGE_NOTIFY_START_OF_STREAM, 0);
    FILE *w = fopen(out, "wb");
    uint8_t hdr[44] = {0};
    memcpy(hdr, "RIFF", 4); memcpy(hdr + 8, "WAVEfmt ", 8);
    hdr[16] = 16; hdr[20] = 1; hdr[22] = 2;
    hdr[24] = 0x80; hdr[25] = 0xBB; hdr[28] = 0x00; hdr[29] = 0xEE; hdr[30] = 2;
    hdr[32] = 4; hdr[34] = 16; memcpy(hdr + 36, "data", 4);
    fwrite(hdr, 1, 44, w);
    long fedA = 0, pcmA = 0, fedB = 0, pcmB = 0;
    TH a = {d, N, 0, &fedA, &pcmA}, b = {d, N, 1, &fedB, &pcmB};
    HANDLE ha = CreateThread(NULL, 0, thfn, &a, 0, NULL);
    HANDLE hb = CreateThread(NULL, 0, thfn, &b, 0, NULL);
    WaitForSingleObject(ha, INFINITE); WaitForSingleObject(hb, INFINITE);
    printf("concurrent: A fed=%ld pcm=%ld B fed=%ld pcm=%ld\n", fedA, pcmA, fedB, pcmB);
    free(d); MFShutdown(); CoUninitialize();
    return 0;
}
