
import sys
sys.path.insert(0, 'framework')
from recomp.nso import Nso
n = Nso('build/extracted/v0/exefs/subsdk0')
e = n.exports()
names = [t[0] for t in e]
print("total", len(names))
for nm in sorted(names):
    if nm.startswith('_ZN5movie7Decoder') or nm.startswith('_ZNK5movie7Decoder') or nm.startswith('_ZTVN5movie7Decoder'):
        print(nm)
