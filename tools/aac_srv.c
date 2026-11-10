#include <windows.h>
#include <mfapi.h>
#include <mfidl.h>
#include <mftransform.h>
#include <mferror.h>
#include <initguid.h>
#include <wmcodecdsp.h>
#include <mmreg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <io.h>
#include <fcntl.h>

/* AAC decode helper: Media Foundation's AAC MFT wedges with MF_E_NOTACCEPTING
   when driven from any non-main thread, so the game (which decodes on worker
   threads) talks to this tiny single-purpose process instead. Protocol on
   stdin/stdout, all integers little-endian:
     request:  u32 len | len bytes (ADTS frame). len == 0: flush decoder, discard.
     reply:    u32 pcm_len | pcm_len bytes (16-bit stereo PCM, full drain).
   stdin EOF or len == 0xFFFFFFFF: exit. stderr is inherited (lands in game log). */

static IMFTransform *M;

/* pipes may return short reads; loop until complete */
static size_t full_read(void *dst, size_t n) {
    size_t off = 0;
    while (off < n) {
        size_t got = fread((uint8_t *)dst + off, 1, n - off, stdin);
        if (got == 0) break;
        off += got;
    }
    return off;
}

static int drain_full(FILE *out) {
    uint32_t total = 0;
    static uint8_t pcm[65536];
    long wpos = 0;
    MFT_OUTPUT_STREAM_INFO oi; memset(&oi, 0, sizeof oi);
    M->lpVtbl->GetOutputStreamInfo(M, 0, &oi);
    { static int once = 0; if (!once) { once = 1; fprintf(stderr, "aac_srv: outstream flags=%#lx size=%lu\n", (unsigned long)oi.dwFlags, (unsigned long)oi.cbSize); } }
    for (int i = 0; i < 64; i++) {
        MFT_OUTPUT_DATA_BUFFER ob; DWORD st = 0;
        memset(&ob, 0, sizeof ob);
        IMFSample *os = NULL; IMFMediaBuffer *obf = NULL;
        if (!(oi.dwFlags & MFT_OUTPUT_STREAM_PROVIDES_SAMPLES)) {
            DWORD need = oi.cbSize ? oi.cbSize : 32768;
            if (SUCCEEDED(MFCreateSample(&os)) && SUCCEEDED(MFCreateMemoryBuffer(need, &obf)) &&
                SUCCEEDED(os->lpVtbl->AddBuffer(os, obf))) ob.pSample = os;
        }
        HRESULT hr = M->lpVtbl->ProcessOutput(M, 0, 1, &ob, &st);
        if (hr == MF_E_TRANSFORM_NEED_MORE_INPUT) break;
        if (FAILED(hr) || !ob.pSample) { if (ob.pSample) ob.pSample->lpVtbl->Release(ob.pSample); break; }
        IMFMediaBuffer *g = NULL;
        ob.pSample->lpVtbl->ConvertToContiguousBuffer(ob.pSample, &g);
        if (g) {
            DWORD cl = 0; BYTE *p = NULL;
            g->lpVtbl->GetCurrentLength(g, &cl);
            if (cl && wpos + (long)cl <= (long)sizeof pcm) {
                g->lpVtbl->Lock(g, &p, NULL, NULL);
                memcpy(pcm + wpos, p, cl); wpos += cl;
                g->lpVtbl->Unlock(g);
            }
            g->lpVtbl->Release(g);
        }
        if (os) { os->lpVtbl->Release(os); obf->lpVtbl->Release(obf); }
        else if (ob.pSample) ob.pSample->lpVtbl->Release(ob.pSample);
    }
    total = (uint32_t)wpos;
    fwrite(&total, 1, 4, out);
    if (total) fwrite(pcm, 1, total, out);
    fflush(out);
    return 0;
}

int main(void) {
    _setmode(_fileno(stdin), _O_BINARY);
    _setmode(_fileno(stdout), _O_BINARY);
    CoInitializeEx(NULL, COINIT_MULTITHREADED);
    MFStartup(MF_VERSION, MFSTARTUP_FULL);

    LONGLONG ts = 0;
    for (;;) {
        uint32_t len = 0;
        if (full_read(&len, 4) != 4) break;                    /* EOF -> exit */
        if (len == 0xFFFFFFFF) break;
        static uint8_t fr[8192];
        if (len > sizeof fr) { fprintf(stderr, "aac_srv: frame too big %u\n", len); break; }
        if (len > 0 && full_read(fr, len) != len) break;
        if (len == 0) {                                     /* flush */
            if (M) M->lpVtbl->ProcessMessage(M, MFT_MESSAGE_COMMAND_FLUSH, 0);
            uint32_t z = 0; fwrite(&z, 1, 4, stdout); fflush(stdout);
            continue;
        }
        if (!M) {                                           /* configure from first ADTS header */
            int fi = (fr[2] >> 2) & 15, ch = ((fr[2] & 1) << 2) | ((fr[3] >> 6) & 3);
            if (ch < 1 || ch > 6) ch = 2;
            int rates[16] = {96000,88200,64000,48000,44100,32000,24000,22050,16000,12000,11025,8000,7350,0,0,0};
            int rate = (fi < 16 && rates[fi]) ? rates[fi] : 48000;
            CoCreateInstance(&CLSID_CMSAACDecMFT, NULL, CLSCTX_INPROC_SERVER, &IID_IMFTransform, (void**)&M);
            IMFMediaType *t = NULL;
            M->lpVtbl->GetInputAvailableType(M, 0, 2, &t);
            t->lpVtbl->SetUINT32(t, &MF_MT_AUDIO_NUM_CHANNELS, ch);
            t->lpVtbl->SetUINT32(t, &MF_MT_AUDIO_SAMPLES_PER_SECOND, rate);
            t->lpVtbl->SetUINT32(t, &MF_MT_AAC_PAYLOAD_TYPE, 1);
            HRESULT hi = M->lpVtbl->SetInputType(M, 0, t, 0); t->lpVtbl->Release(t);
            IMFMediaType *o = NULL; MFCreateMediaType(&o);
            o->lpVtbl->SetGUID(o, &MF_MT_MAJOR_TYPE, &MFMediaType_Audio);
            o->lpVtbl->SetGUID(o, &MF_MT_SUBTYPE, &MFAudioFormat_PCM);
            o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_NUM_CHANNELS, (UINT32)ch);
            o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_SAMPLES_PER_SECOND, (UINT32)rate);
            o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_BITS_PER_SAMPLE, 16);
            o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_BLOCK_ALIGNMENT, (UINT32)(ch * 2));
            o->lpVtbl->SetUINT32(o, &MF_MT_AUDIO_AVG_BYTES_PER_SECOND, (UINT32)(rate * ch * 2));
            HRESULT ho = M->lpVtbl->SetOutputType(M, 0, o, 0); o->lpVtbl->Release(o);
            if (FAILED(hi) || FAILED(ho)) { fprintf(stderr, "aac_srv: setup %#lx/%#lx\n", (unsigned long)hi, (unsigned long)ho); break; }
            M->lpVtbl->ProcessMessage(M, MFT_MESSAGE_NOTIFY_BEGIN_STREAMING, 0);
            M->lpVtbl->ProcessMessage(M, MFT_MESSAGE_NOTIFY_START_OF_STREAM, 0);
            fprintf(stderr, "aac_srv: decoding %d Hz x%d (hi=%#lx ho=%#lx)\n", rate, ch, (unsigned long)hi, (unsigned long)ho);
            { IMFMediaType *ck = NULL; M->lpVtbl->GetInputCurrentType(M, 0, &ck);
              if (ck) { UINT32 c=0,r=0,p=0; ck->lpVtbl->GetUINT32(ck, &MF_MT_AUDIO_NUM_CHANNELS, &c); ck->lpVtbl->GetUINT32(ck, &MF_MT_AUDIO_SAMPLES_PER_SECOND, &r); ck->lpVtbl->GetUINT32(ck, &MF_MT_AAC_PAYLOAD_TYPE, &p);
                fprintf(stderr, "aac_srv: cur-in ch=%u rate=%u pay=%u\n", c, r, p); ck->lpVtbl->Release(ck); } }
        }
        IMFMediaBuffer *b = NULL; IMFSample *s = NULL;
        HRESULT hr = MFCreateMemoryBuffer(len, &b);
        BYTE *p = NULL;
        if (SUCCEEDED(hr)) hr = b->lpVtbl->Lock(b, &p, NULL, NULL);
        if (SUCCEEDED(hr)) { memcpy(p, fr, len); hr = b->lpVtbl->Unlock(b); }
        if (SUCCEEDED(hr)) hr = b->lpVtbl->SetCurrentLength(b, len);
        if (SUCCEEDED(hr)) hr = MFCreateSample(&s);
        if (SUCCEEDED(hr)) hr = s->lpVtbl->AddBuffer(s, b);
        if (SUCCEEDED(hr)) hr = s->lpVtbl->SetSampleTime(s, ts);
        if (SUCCEEDED(hr)) hr = M->lpVtbl->ProcessInput(M, 0, s, 0);
        if (s) s->lpVtbl->Release(s);
        if (b) b->lpVtbl->Release(b);
        if (FAILED(hr)) { fprintf(stderr, "aac_srv: input failed %#lx, flushing\n", (unsigned long)hr); M->lpVtbl->ProcessMessage(M, MFT_MESSAGE_COMMAND_FLUSH, 0); }
        else ts += 213333;
        drain_full(stdout);
    }
    if (M) M->lpVtbl->Release(M);
    MFShutdown(); CoUninitialize();
    return 0;
}
