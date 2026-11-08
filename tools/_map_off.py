import sys, bisect
sys.path.insert(0, r'D:/consoles/ns/xc2-recomp')
import recomp.nso as N
want = {'main':[0x26eeb8], 'sdk':[0x8d8b8,0x8d97c,0x4a5834,0x158b40]}
for f, offs in want.items():
    n = N.Nso(rf'D:/consoles/ns/hayarigami-recomp/build/extracted/latest/exefs/{f}')
    ex = sorted([(s[3], s[4], s[0]) for s in n.exports() if s[4]])
    starts = [e[0] for e in ex]
    for o in offs:
        i = bisect.bisect_right(starts, o) - 1
        if i >= 0:
            st, sz, name = ex[i]
            print(f'{f}+{o:#x} -> {name} +{o-st:#x} (size {sz:#x}, inside={o-st < sz})')
        else: print(f, hex(o), 'before first')