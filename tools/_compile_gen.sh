#!/bin/bash
cd /d/consoles/ns/hayarigami-recomp || exit 1
rm -f build/gencompile.fail build/gencompile.err
for mod in main subsdk0 sdk; do echo "== $mod"; ls build/gen-all/$mod/*.c | xargs -P 12 -n 1 bash tools/compile_one.sh; done
echo "objects: $(find build/genobj -name '*.o' | wc -l)"