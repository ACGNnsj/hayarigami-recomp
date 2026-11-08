#!/bin/bash
# usage: compile_one.sh <generated .c file>
f="$1"
m=$(basename "$(dirname "$f")")
b=$(basename "$f" .c)
mkdir -p "build/genobj/$m"
/c/msys64/ucrt64/bin/clang.exe -c -O1 -fno-strict-aliasing -Wno-return-type -Wno-unused-label -fvisibility=hidden -march=x86-64-v3 -Iframework/runtime -Ibuild/gen-all "$f" -o "build/genobj/$m/$b.o" 2>>build/gencompile.err || echo "FAIL $f" >>build/gencompile.fail