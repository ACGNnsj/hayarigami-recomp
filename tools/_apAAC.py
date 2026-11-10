"AAC host decoder (LATM/LOAS -> ADTS -> MF): patch ov_movie.c + movie.h."
import sys
def rep(path, old, new):
    t = open(path, encoding='utf-8').read()
    assert t.count(old) == 1, (path, old[:60], t.count(old))
    open(path, 'w', encoding='utf-8', newline='').write(t.replace(old, new))
    print('ok:', old[:50].replace(chr(10), '\\n'))
M = base + 'framework/runtime/ov_movie.c'
H = base + 'framework/runtime/movie.h'
