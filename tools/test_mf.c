#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>
#include <mfapi.h>
#include <mftransform.h>
#include <mferror.h>
#include <mfidl.h>
#include <wmcodecdsp.h>

static const GUID CLSID_H264 = {0x62ce7e72,0x4c71,0x4d20,{0xb1,0x5d,0x45,0x28,0x31,0xa8,0x7d,0x9d}};

static IMFMediaType *make_in(int w, int h, const unsigned char *seq, unsigned n) {
    IMFMediaType *t = NULL;
    if (FAILED(MFCreateMediaType(&t))) return NULL;
    HRESULT hr = t->lpVtbl->SetGUID(t, &MF_MT_MAJOR_TYPE, &MFMediaType_Video);
    if (SUCCEEDED(hr)) hr = t->lpVtbl->SetGUID(t, &MF_MT_SUBTYPE, &MFVideoFormat_H264);
    if (SUCCEEDED(hr)) hr = t->lpVtbl->SetUINT64(t, &MF_MT_FRAME_SIZE, ((unsigned long long)w << 32) | (unsigned)h);
    if (SUCCEEDED(hr)) hr = t->lpVtbl->SetUINT32(t, &MF_MT_INTERLACE_MODE, MFVideoInterlace_Progressive);
    if (SUCCEEDED(hr) && n) hr = t->lpVtbl->SetBlob(t, &MF_MT_MPEG_SEQUENCE_HEADER, seq, n);
    if (FAILED(hr)) { printf("in type set failed %#lx\n", (unsigned long)hr); t->lpVtbl->Release(t); return NULL; }
    return t;
}

static IMFMediaType *make_out(int w, int h) {
    IMFMediaType *t = NULL;
    if (FAILED(MFCreateMediaType(&t))) return NULL;
    HRESULT hr = t->lpVtbl->SetGUID(t, &MF_MT_MAJOR_TYPE, &MFMediaType_Video);
    if (SUCCEEDED(hr)) hr = t->lpVtbl->SetGUID(t, &MF_MT_SUBTYPE, &MFVideoFormat_NV12);
    if (SUCCEEDED(hr)) hr = t->lpVtbl->SetUINT64(t, &MF_MT_FRAME_SIZE, ((unsigned long long)w << 32) | (unsigned)h);
    if (SUCCEEDED(hr)) hr = t->lpVtbl->SetUINT32(t, &MF_MT_INTERLACE_MODE, MFVideoInterlace_Progressive);
    if (FAILED(hr)) { printf("out type set failed %#lx\n", (unsigned long)hr); t->lpVtbl->Release(t); return NULL; }
    return t;
}

int main(int argc, char **argv) {
    int use_seq = argc < 2 || atoi(argv[1]);
    int use_start = argc < 3 || atoi(argv[2]);
    int w = 1920, h = 1080;
    CoInitializeEx(NULL, COINIT_MULTITHREADED);
    MFStartup(MF_VERSION, MFSTARTUP_FULL);
    unsigned char seq[512]; unsigned seqn = 0;
    FILE *f = fopen("build/v0/spspps.bin", "rb");
    if (f) { seqn = (unsigned)fread(seq, 1, sizeof seq, f); fclose(f); }
    printf("seq %u bytes\n", seqn);
    IMFTransform *mft = NULL;
    HRESULT hr = CoCreateInstance(&CLSID_H264, NULL, CLSCTX_INPROC_SERVER, &IID_IMFTransform, (void **)&mft);
    printf("CoCreate %#lx\n", (unsigned long)hr);
    if (FAILED(hr)) return 1;
    IMFMediaType *in = make_in(w, h, seq, use_seq ? seqn : 0);
    hr = in ? mft->lpVtbl->SetInputType(mft, 0, in, 0) : E_OUTOFMEMORY;
    if (in) in->lpVtbl->Release(in);
    printf("SetInputType %#lx\n", (unsigned long)hr);
    IMFMediaType *out = make_out(w, h);
    HRESULT hro = out ? mft->lpVtbl->SetOutputType(mft, 0, out, 0) : E_OUTOFMEMORY;
    if (out) out->lpVtbl->Release(out);
    printf("SetOutputType %#lx\n", (unsigned long)hro);
    mft->lpVtbl->ProcessMessage(mft, MFT_MESSAGE_NOTIFY_BEGIN_STREAMING, 0);
    if (use_start) mft->lpVtbl->ProcessMessage(mft, MFT_MESSAGE_NOTIFY_START_OF_STREAM, 0);
    MFT_OUTPUT_STREAM_INFO oi;
    memset(&oi, 0, sizeof oi);
    HRESULT hri = mft->lpVtbl->GetOutputStreamInfo(mft, 0, &oi);
    printf("GetOutputStreamInfo %#lx flags %#lx size %lu\n", (unsigned long)hri, (unsigned long)oi.dwFlags, (unsigned long)oi.cbSize);
    f = fopen(argc > 3 ? argv[3] : "build/v0/pk_annexb.bin", "rb");
    if (!f) { printf("no packets\n"); return 1; }
    int frames = 0, fed = 0, fails = 0;
    for (;;) {
        unsigned n = 0;
        if (fread(&n, 4, 1, f) != 1) break;
        if (!n || n > (1u << 22)) break;
        unsigned char *d = malloc(n);
        if (fread(d, 1, n, f) != n) { free(d); break; }
        IMFMediaBuffer *b = NULL; IMFSample *s = NULL;
        MFCreateMemoryBuffer(n, &b);
        BYTE *p = NULL; b->lpVtbl->Lock(b, &p, NULL, NULL);
        memcpy(p, d, n); b->lpVtbl->Unlock(b);
        b->lpVtbl->SetCurrentLength(b, n);
        MFCreateSample(&s);
        s->lpVtbl->AddBuffer(s, b);
        LONGLONG ts = (LONGLONG)fed * 333667;
        s->lpVtbl->SetSampleTime(s, ts);
        s->lpVtbl->SetSampleDuration(s, 333667);
        hr = mft->lpVtbl->ProcessInput(mft, 0, s, 0);
        if (fed < 3 || FAILED(hr)) printf("in[%d] %u bytes -> %#lx\n", fed, n, (unsigned long)hr);
        s->lpVtbl->Release(s); b->lpVtbl->Release(b); free(d);
        fed++;
        for (int k = 0; k < 4; k++) {
            MFT_OUTPUT_DATA_BUFFER ob; DWORD st = 0;
            IMFSample *own = NULL; IMFMediaBuffer *ownb = NULL;
            memset(&ob, 0, sizeof ob);
            if (!(oi.dwFlags & MFT_OUTPUT_STREAM_PROVIDES_SAMPLES)) {
                MFCreateSample(&own);
                MFCreateMemoryBuffer(oi.cbSize ? oi.cbSize : (DWORD)(w * h * 3 / 2), &ownb);
                own->lpVtbl->AddBuffer(own, ownb);
                ob.pSample = own;
            }
            HRESULT o = mft->lpVtbl->ProcessOutput(mft, 0, 1, &ob, &st);
            if (o == MF_E_TRANSFORM_NEED_MORE_INPUT) { if (own) own->lpVtbl->Release(own); if (ownb) ownb->lpVtbl->Release(ownb); break; }
            if (o == MF_E_TRANSFORM_STREAM_CHANGE) {
                if (own) own->lpVtbl->Release(own); if (ownb) ownb->lpVtbl->Release(ownb);
                IMFMediaType *o2 = make_out(w, h);
                HRESULT sr = o2 ? mft->lpVtbl->SetOutputType(mft, 0, o2, 0) : E_FAIL;
                if (o2) o2->lpVtbl->Release(o2);
                printf("stream change -> %#lx\n", (unsigned long)sr);
                continue;
            }
            if (FAILED(o) || !ob.pSample) {
                if (fails++ < 3) printf("out %#lx\n", (unsigned long)o);
                if (own) own->lpVtbl->Release(own); if (ownb) ownb->lpVtbl->Release(ownb);
                break;
            }
            IMFMediaBuffer *cb = NULL;
            if (SUCCEEDED(ob.pSample->lpVtbl->ConvertToContiguousBuffer(ob.pSample, &cb))) {
                BYTE *pp = NULL; DWORD len = 0;
                if (SUCCEEDED(cb->lpVtbl->Lock(cb, &pp, NULL, &len))) {
                    if (frames < 3) printf("frame %d: %lu bytes ts=%lld\n", frames, (unsigned long)len, (long long)ts);
                    if (frames == 200) { FILE *g = fopen("build/v0/frame200.nv12", "wb"); if (g) { fwrite(pp, 1, len, g); fclose(g); } }
                    frames++;
                    cb->lpVtbl->Unlock(cb);
                }
                cb->lpVtbl->Release(cb);
            }
            ob.pSample->lpVtbl->Release(ob.pSample);
            if (ownb) ownb->lpVtbl->Release(ownb);
        }
    }
    fclose(f);
    printf("draining\n");
    mft->lpVtbl->ProcessMessage(mft, MFT_MESSAGE_NOTIFY_END_OF_STREAM, 0);
    mft->lpVtbl->ProcessMessage(mft, MFT_MESSAGE_COMMAND_DRAIN, 0);
    for (int k = 0; k < 400; k++) {
        MFT_OUTPUT_DATA_BUFFER ob; DWORD st = 0;
        IMFSample *own = NULL; IMFMediaBuffer *ownb = NULL;
        memset(&ob, 0, sizeof ob);
        MFCreateSample(&own);
        MFCreateMemoryBuffer(oi.cbSize, &ownb);
        own->lpVtbl->AddBuffer(own, ownb);
        ob.pSample = own;
        HRESULT o = mft->lpVtbl->ProcessOutput(mft, 0, 1, &ob, &st);
        if (o == MF_E_TRANSFORM_NEED_MORE_INPUT) { printf("drain %d: need more input\n", k); own->lpVtbl->Release(own); ownb->lpVtbl->Release(ownb); break; }
        if (FAILED(o)) { printf("drain %d: %#lx\n", k, (unsigned long)o); own->lpVtbl->Release(own); ownb->lpVtbl->Release(ownb); break; }
        frames++;
        own->lpVtbl->Release(own); ownb->lpVtbl->Release(ownb);
    }
    printf("done fed=%d frames=%d\n", fed, frames);
    return 0;
}