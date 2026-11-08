# 工具链（2026-11-09 实测）

宿主机：Windows，MSYS2 在 `C:\msys64`，目标三元组 `x86_64-w64-mingw32`（UCRT64）。

## 已装并验证

| 组件 | 版本/路径 | 证据 |
|---|---|---|
| clang | 23.1.5，`C:\msys64\ucrt64\bin\clang.exe` | `build/pacman.log` exit 0 |
| lld | 随 clang 包 | `-fuse-ld=lld` 链接通过 |
| llvm-ar | `C:\msys64\ucrt64\bin\llvm-ar.exe`（来自 `mingw-w64-ucrt-x86_64-llvm`） | `build/rtlib2.log`：AR 成功，`libxc2rt.a` 18.7 MiB |
| ninja | 1.13.2 | `build/rtlib2.log` |
| gcc / make / pkgconf | UCRT64 | — |
| SDL3 | `ucrt64` 包 | 运行时 `-lSDL3` |
| opus / libvpx / zstd | `ucrt64`（libvpx、zstd 静态用 `-l:libvpx.a`、`-l:libzstd.a`） | 运行时源码 `ov_media.c`、`resolution.c` |
| Vulkan | `vulkan-devel` + `vulkan-memory-allocator` + `vulkan-validation-layers` | 运行时 `vk_*.c` |
| shaderc / spirv-tools | `ucrt64` | 着色器翻译链 |
| .NET SDK | 10.0.403 | `dotnet --list-sdks` |

**缺（会卡 P4 第一帧）**：VS BuildTools 2026 的 `link.exe`。NativeAOT 编译镜像要求 MSVC 链接器；
没有它 `tools/build_xlate.py` 出不了 `xc2_xlate.exe`，而没有翻译器 = 所有着色器失败 = 黑屏有声。

## 常用命令（本机可直接跑）

```bash
# 1) 抬升（11 秒）
ns/xc2-recomp/recomp/gen.py --exefs ns/hayarigami-recomp/build/extracted/latest/exefs \
  --out ns/hayarigami-recomp/build/gen-all --modules main,subsdk0,sdk --jobs 14

# 2) 编译运行时静态库（101 个 .o）
cd ns/hayarigami-recomp/framework/tools
../../.venv/Scripts/python.exe build_game.py --make-runtime-lib \
  --expected ../../data/expected-latest.json --out ../../build/rtlib --jobs 12

# 3) 编译全部生成的 C（216 MB，见 tools/_compile_gen.sh）
bash ns/hayarigami-recomp/tools/_compile_gen.sh
```

## 注意
- 传给 `clang.exe` 的 `-I` 必须是 Windows 或相对路径；`/d/consoles/...` 这种 MSYS 路径 clang 不认
  （会报 `fatal error: 'cpu.h' file not found`）。
- `ops_bash` 的后台作业偶发 `EXECUTOR_UNAVAILABLE: Niubash execution tree link count mismatch`，
  重试一次即过；不影响构建本身。
