#include <windows.h>
#include <mfapi.h>
#include <mftransform.h>
#include <initguid.h>
#include <wmcodecdsp.h>
#include <stdio.h>
#define LOG(m, x) do { fprintf(stderr, m ": %#lx\n", (unsigned long)(x)); fflush(stderr); } while (0)
int main() {
    setvbuf(stderr, NULL, _IONBF, 0);
    fprintf(stderr, "start\n");
    HRESULT hr = CoInitializeEx(NULL, COINIT_MULTITHREADED); LOG("coinit", hr);
    hr = MFStartup(MF_VERSION, MFSTARTUP_FULL); LOG("mfstartup", hr);
    IMFTransform *m = NULL;
    hr = CoCreateInstance(&CLSID_CMSAACDecMFT, NULL, CLSCTX_INPROC_SERVER, &IID_IMFTransform, (void**)&m);
    LOG("create", hr);
    if (SUCCEEDED(hr)) {
        IMFMediaType *t = NULL;
        hr = m->lpVtbl->GetInputAvailableType(m, 0, 0, &t); LOG("getin", hr);
    }
    fprintf(stderr, "done\n");
    return 0;
}
