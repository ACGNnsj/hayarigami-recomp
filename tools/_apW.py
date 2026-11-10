p = 'D:/consoles/ns/hayarigami-recomp/tools/test_sr.c'
t = open(p, encoding='utf-8').read()
t = t.replace('#include <mfreadwrite.h>', '#include <mfidl.h>\n#include <mfreadwrite.h>')
open(p, 'w', encoding='utf-8').write(t)
print('inc ok')