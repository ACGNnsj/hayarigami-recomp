// Sparse textures: the guest asks a builder for the tile layout a sparse texture of that shape would use. This port's
// textures live in ordinary pools and nothing is sparse, so the query answers a zero layout (no tiles) and the caller
// falls back to a non-sparse allocation. Same answer as power-moon-recomp's nvnTextureBuilderGetSparseTileLayout.
#include <string.h>

#include "nvn_api.h"

// The sparse tile layout is an opaque SDK struct. Hayarigami's texture loader keeps it 0x20 bytes below the
// NVNtextureBuilder on the stack (main+0x2819dc: layout at sp+0x20, builder at sp+0x40), so a wider clear would overwrite
// the builder's device, description and flags: every packaged texture then initialized empty (0x0x1, format 0) and the
// screen stayed black. 0x20 is that reservation and matches the struct's size in the SDKs this port targets.
#define SPARSE_LAYOUT_SIZE 0x20

// void nvnTextureBuilderGetSparseTileLayout(NVNtextureBuilder *b, NVNtextureSparseTileLayout *out)
NVN_API(nvnTextureBuilderGetSparseTileLayout) {
    NVN_LOG("sparse tile layout: builder %p out %p", arg_p(c, 0), arg_p(c, 1));
    void *out = (void *)(uintptr_t)arg_x(c, 1);
    if (out) memset(out, 0, SPARSE_LAYOUT_SIZE);
    ret_x(c, 0);
}

// void nvnTextureGetSparseTileLayout(NVNtexture *t, NVNtextureSparseTileLayout *out)
NVN_API(nvnTextureGetSparseTileLayout) {
    (void)c;
    void *out = (void *)(uintptr_t)arg_x(c, 1);
    if (out) memset(out, 0, SPARSE_LAYOUT_SIZE);
    ret_x(c, 0);
}
