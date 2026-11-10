#!/bin/bash
# Build build/v0/haya.exe from the lifted modules and the forked runtime.
set -e
cd /d/consoles/ns/hayarigami-recomp 2>/dev/null || cd "$(dirname "$0")/.."
CL=/c/msys64/ucrt64/bin/clang.exe
INC='-Iframework/runtime -Ibuild/gen-all -Ibuild/v0 -I/c/msys64/ucrt64/include -I/c/msys64/ucrt64/include/vma -Iframework/runtime/third_party/imgui -Iframework/runtime/third_party/imgui/backends'
# 1. runtime objects for this title (boot/ro overrides applied)
(cd framework/tools && ../../.venv/Scripts/python.exe build_game.py --make-runtime-lib --expected ../../data/expected-latest.json --out ../../build/rtlib --jobs 12 >/dev/null)
# 2. platform, menu and Dear ImGui objects (the library holds none of them)
mkdir -p build/rtobj2/platform build/rtobj2/ui build/rtobj2/imgui build/rtobj2/backends
for f in framework/runtime/platform/common.c framework/runtime/platform/win32.c; do $CL -c -O2 -g -Wall -fno-strict-aliasing -march=x86-64-v3 $INC $f -o build/rtobj2/platform/$(basename $f .c).o; done
for f in framework/runtime/ui/*.cpp; do b=$(basename $f .cpp); case $b in *_sdl) continue;; esac; $CL -c -O2 -g -Wall -fno-strict-aliasing -march=x86-64-v3 -std=c++20 $INC $f -o build/rtobj2/ui/$b.o; done
for f in framework/runtime/third_party/imgui/*.cpp; do $CL -c -O2 -g -Wall -fno-strict-aliasing -march=x86-64-v3 -std=c++20 $INC $f -o build/rtobj2/imgui/$(basename $f .cpp).o; done
$CL -c -O2 -g -Wall -fno-strict-aliasing -march=x86-64-v3 -std=c++20 $INC framework/runtime/third_party/imgui/backends/imgui_impl_vulkan.cpp -o build/rtobj2/backends/imgui_impl_vulkan.o
# 3. patches.c, romfs.c and ov_zstd.c are outside the library's set
for f in patches romfs ov_zstd; do $CL -c -O2 -g -Wall -fno-strict-aliasing -march=x86-64-v3 $INC framework/runtime/$f.c -o build/rtobj2/$f.o; done
# 4. RomFS index + module glue
.venv/Scripts/python.exe framework/tools/romfs_index.py --romfs build/extracted/v0/romfs --out build/v0 >/dev/null
.venv/Scripts/python.exe tools/gen_modules.py >/dev/null
$CL -c -O1 -fno-strict-aliasing -march=x86-64-v3 -Iframework/runtime -Ibuild/gen-all build/v0/modules.c -o build/v0/modules.o
# 5. link
$CL -fuse-ld=lld -Wl,--stack,16777216 -o build/v0/haya.exe \
  build/rtlib/obj/runtime/*.o build/rtobj2/*.o build/rtobj2/platform/*.o build/rtobj2/ui/*.o build/rtobj2/imgui/*.o build/rtobj2/backends/*.o \
  $(find build/genobj -name '*.o') build/v0/modules.o \
  -lpsapi -lbcrypt -lvulkan-1 -luser32 -lgdi32 -ldwmapi -lwinmm -lSDL3 -lopus -l:libvpx.a -lmfplat -lmfuuid -lole32 -l:libzstd.a -l:libstdc++.a -l:libwinpthread.a
ls -l build/v0/haya.exe