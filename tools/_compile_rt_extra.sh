#!/bin/bash
cd /d/consoles/ns/hayarigami-recomp || exit 1
CL=/c/msys64/ucrt64/bin/clang.exe
O=build/rtobj2
mkdir -p $O/platform $O/ui $O/imgui $O/backends
COMMON="-c -O2 -g -Wall -fno-strict-aliasing -march=x86-64-v3 -Iframework/runtime -Ibuild/gen-all -I$O -I/c/msys64/ucrt64/include -I/c/msys64/ucrt64/include/vma -Iframework/runtime/third_party/imgui -Iframework/runtime/third_party/imgui/backends"
rc=0
for f in framework/runtime/platform/common.c framework/runtime/platform/win32.c; do
  b=$(basename $f .c); echo "CC $f"; $CL $COMMON $f -o $O/platform/$b.o 2>>build/rt2.err || rc=1
done
for f in framework/runtime/ui/*.cpp; do
  b=$(basename $f .cpp); case $b in *_sdl) continue;; esac; echo "CXX $f"; $CL $COMMON -std=c++20 $f -o $O/ui/$b.o 2>>build/rt2.err || rc=1
done
for f in framework/runtime/third_party/imgui/*.cpp; do
  b=$(basename $f .cpp); echo "CXX $f"; $CL $COMMON -std=c++20 $f -o $O/imgui/$b.o 2>>build/rt2.err || rc=1
done
for b in imgui_impl_win32 imgui_impl_vulkan imgui_impl_sdl3; do
  f=framework/runtime/third_party/imgui/backends/$b.cpp
  [ -f $f ] || { echo "missing $f"; continue; }
  echo "CXX $f"; $CL $COMMON -std=c++20 $f -o $O/backends/$b.o 2>>build/rt2.err || rc=1
done
echo rc=$rc; ls $O/platform $O/ui $O/imgui $O/backends 2>/dev/null | head -30