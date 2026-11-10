#include <windows.h>
#include <mfapi.h>
#include <mftransform.h>
#include <mferror.h>
#include <initguid.h>
#include <wmcodecdsp.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
static int G_MODE = 0;
static int feedN(IMFTransform *M, const uint8_t *d, long N, int nframes, int drain, long *pcm) {
    long q = 0; int nf = 0; LONGLONG tt = 0;
    for (; q + 7 <= N && nf < nframes; nf++) {
        if (d[q] != 0xFF || (d[q+1] & 0xF6) != 0xF0) return -99;
        int ln = ((d[q+3] & 3) << 11) | (d[q+4] << 3) | (d[q+5] >> 5);
        IMFMediaBuffer *bb = NULL; IMFSample *ss = NULL;
        HRESULT hx = MFCreateMemoryBuffer((DWORD)ln, &bb);
        BYTE *pp = NULL;
        if (SUCCEEDED(hx)) hx = bb->lpVtbl->Lock(bb, &pp, NULL, NULL);
        if (SUCCEEDED(hx)) { memcpy(pp, d + q, ln); hx = bb->lpVtbl->Unlock(bb); }
        if (SUCCEEDED(hx)) hx = bb->lpVtbl->SetCurrentLength(bb, (DWORD)ln);
        if (SUCCEEDED(hx)) hx = MFCreateSample(&ss);
        if (SUCCEEDED(hx)) hx = ss->lpVtbl->AddBuffer(ss, bb);
        if (SUCCEEDED(hx) && G_MODE >= 1) hx = ss->lpVtbl->SetSampleTime(ss, tt);
        if (SUCCEEDED(hx) && G_MODE >= 2) hx = ss->lpVtbl->SetSampleDuration(ss, 213333);
        if (SUCCEEDED(hx)) hx = M->lpVtbl->ProcessInput(M, 0, ss, 0);
        if (ss) ss->lpVtbl->Release(ss);
        if (bb) bb->lpVtbl->Release(bb);
        if (FAILED(hx)) { fprintf(stderr, "frame %d hr=%#lx\n", nf, (unsigned long)hx); return -1000 - nf; }
        q += ln; tt += 213333;
        if (drain) {
            for (int dd = 0; dd < 8; dd++) {
                MFT_OUTPUT_DATA_BUFFER ob; memset(&ob, 0, sizeof ob); DWORD stx = 0;
                HRESULT hx2 = M->lpVtbl->ProcessOutput(M, 0, 1, &ob, &stx);
                if (hx2 == MF_E_TRANSFORM_NEED_MORE_INPUT) break;
                if (FAILED(hx2)) break;
                if (ob.pSample) {
                    IMFMediaBuffer *gg = NULL;
                    ob.pSample->lpVtbl->ConvertToContiguousBuffer(ob.pSample, &gg);
                    if (gg) { DWORD cl = 0; gg->lpVtbl->GetCurrentLength(gg, &cl); *pcm += cl; gg->lpVtbl->Release(gg); }
                    ob.pSample->lpVtbl->Release(ob.pSample);
                } else break;
            }
        }
    }
    return nf;
}
static IMFTransform *mkMFT(void) {
    IMFTransform *M = NULL;
    if (FAILED(CoCreateInstance(&CLSID_CMSAACDecMFT, NULL, CLSCTX_INPROC_SERVER, &IID_IMFTransform, (void**)&M))) return NULL;
    for (int ei = 0; ei < 6; ei++) { IMFMediaType *et = NULL; if (SUCCEEDED(M->lpVtbl->GetInputAvailableType(M, 0, ei, &et)) && et) et->lpVtbl->Release(et); }
    IMFMediaType *t = NULL;
    M->lpVtbl->GetInputAvailableType(M, 0, 2, &t);
    t->lpVtbl->SetUINT32(t, &MF_MT_AUDIO_NUM_CHANNELS, 2);
    t->lpVtbl->SetUINT32(t, &MF_MT_AUDIO_SAMPLES_PER_SECOND, 48000);
    t->lpVtbl->SetUINT32(t, &MF_MT_AAC_PAYLOAD_TYPE, 0);
    if (FAILED(M->lpVtbl->SetInputType(M, 0, t, 0))) { t->lpVtbl->Release(t); M->lpVtbl->Release(M); return NULL; }
    t->lpVtbl->Release(t);
    IMFMediaType *o = NULL; MFCreateMediaType(&o);
    o->lpVtbl->SetGUID(o, &MF_MT_MAJOR_TYPE, &MFMediaType_Audio);
    o->lpVtbl->SetGUID(o, &MF_MT_SUBTYPE, &MFAudioFormat_PCM);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_NUM_CHANNELS, 2);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_SAMPLES_PER_SECOND, 48000);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_BITS_PER_SAMPLE, 16);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_BLOCK_ALIGNMENT, 4);
    o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_AVG_BYTES_PER_SECOND, 48000 * 4);
    if (FAILED(M->lpVtbl->SetOutputType(M, 0, o, 0))) { o->lpVtbl->Release(o); M->lpVtbl->Release(M); return NULL; }
    o->lpVtbl->Release(o);
    M->lpVtbl->ProcessMessage(M, MFT_MESSAGE_NOTIFY_BEGIN_STREAMING, 0);
    M->lpVtbl->ProcessMessage(M, MFT_MESSAGE_NOTIFY_START_OF_STREAM, 0);
    return M;
}
int main(int argc, char **argv) {
    if (argc > 2) G_MODE = atoi(argv[2]);
    setvbuf(stderr, NULL, _IONBF, 0);
    FILE *f = fopen(argv[1], "rb");
    fseek(f, 0, SEEK_END); long N = ftell(f); fseek(f, 0, SEEK_SET);
    uint8_t *d = malloc(N); fread(d, 1, N, f); fclose(f);
    CoInitializeEx(NULL, COINIT_MULTITHREADED);
    MFStartup(MF_VERSION, MFSTARTUP_FULL);
    long pcm1 = 0;
    fprintf(stderr, "mode=%d\n", G_MODE);
    IMFTransform *M1 = mkMFT();
    if (!M1) { printf("M1 create failed\n"); return 1; }
    int r1 = feedN(M1, d, N, 40, 1, &pcm1);
    printf("M1 fed=%d pcm=%ld\n", r1 >= 0 ? r1 : r1, pcm1);
    M1->lpVtbl->Release(M1); M1 = NULL;
    fprintf(stderr, "M1 released\n");
    long pcm2 = 0;
    IMFTransform *M2 = mkMFT();
    if (!M2) { printf("M2 create failed\n"); return 1; }
    int r2 = feedN(M2, d, N, 10, 1, &pcm2);
    printf("M2 fed=%d pcm=%ld\n", r2, pcm2);
    M2->lpVtbl->Release(M2);
    MFShutdown(); CoUninitialize();
    return 0;
}
