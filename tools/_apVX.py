import io, sys
p = 'D:/consoles/ns/hayarigami-recomp/framework/runtime/vk_exec_draw.c'
s = io.open(p, encoding='utf-8', newline='').read()
old = '                         hi[2], zero, bad);\n        }\n    }\n    vkCmdDrawIndexed(ex->cb,'
assert s.count(old) == 1
add = [
'            // The color (location 1, RGBA8) and UV (location 2, 2 floats) the draw reads: first vertex, whether',
'            // the color is uniform, and the UV span. A highlight pulse shows up as the color changing across',
'            // frames; sampled-twice UVs show up as a span twice the sprite size.',
'            va_st va1, va2;',
'            memcpy(&va1, &ex->pipe.vattr[1], sizeof va1);',
'            memcpy(&va2, &ex->pipe.vattr[2], sizeof va2);',
'            uint32_t vs1 = va1.stream < 16 ? ex->pipe.vstream[va1.stream].stride : 0;',
'            uint64_t vb1 = va1.stream < 16 ? ex->vbuf[va1.stream].address : 0;',
'            uint32_t vs2 = va2.stream < 16 ? ex->pipe.vstream[va2.stream].stride : 0;',
'            uint64_t vb2 = va2.stream < 16 ? ex->vbuf[va2.stream].address : 0;',
'            if (va1.fmt == 0x25 && vs1 >= 4 && vb1 && va2.fmt == 0x16 && vs2 >= 8 && vb2 &&',
'                !nvn_gpu_only(vb1) && !nvn_gpu_only(vb2)) {',
'                uint8_t c0[4] = {0};',
'                int cuni = 1;',
'                float u0 = 0, v0 = 0, ulo = INFINITY, uhi = -INFINITY, vlo = INFINITY, vhi = -INFINITY;',
'                int uvbad = 0;',
'                for (int k = 0; k < n; k++) {',
'                    uint32_t jx = d->itype == NVN_INDEX_TYPE_UNSIGNED_SHORT ? ((const uint16_t *)(uintptr_t)d->ibuf)[k]',
'                                                                        : ((const uint32_t *)(uintptr_t)d->ibuf)[k];',
'                    jx += (uint32_t)d->base_vertex;',
'                    uint8_t cb[4];',
'                    memcpy(cb, (const void *)(uintptr_t)(vb1 + (uint64_t)jx * vs1 + va1.offset), 4);',
'                    float uv[2];',
'                    memcpy(uv, (const void *)(uintptr_t)(vb2 + (uint64_t)jx * vs2 + va2.offset), 8);',
'                    if (k == 0) { memcpy(c0, cb, 4); u0 = uv[0]; v0 = uv[1]; }',
'                    else if (memcmp(c0, cb, 4)) cuni = 0;',
'                    if (!isfinite(uv[0]) || !isfinite(uv[1])) { uvbad++; continue; }',
'                    if (uv[0] < ulo) ulo = uv[0];',
'                    if (uv[0] > uhi) uhi = uv[0];',
'                    if (uv[1] < vlo) vlo = uv[1];',
'                    if (uv[1] > vhi) vhi = uv[1];',
'                }',
'                vk_dump_note("vx12 of draw prog %llu: color0 [%u %u %u %u] uniform %d, uv0 (%g %g) u %g..%g v %g..%g bad %d",',
'                             (unsigned long long)(ex->prog ? ex->prog->serial : 0),',
'                             c0[0], c0[1], c0[2], c0[3], cuni, u0, v0, ulo, uhi, vlo, vhi, uvbad);',
'            }',
]
new = '                         hi[2], zero, bad);\n' + '\n'.join(add) + '\n        }\n    }\n    vkCmdDrawIndexed(ex->cb,'
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')