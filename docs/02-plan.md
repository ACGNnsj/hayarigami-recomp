# 02 路线与阶段计划

## 1. 为什么走静态重编译

| 路线 | 可行性 | 说明 |
|---|---|---|
| **静态重编译**（选） | ✅ | ARM64 → C 抬升，宿主直接执行 x86-64；Horizon 系统调用用 HLE 顶替；NVN → Vulkan。已有同血统项目跑通 3A 级游戏（TotK/XC2/XCX），本作规模只有它们的 1/10 |
| 模拟器打包 | ❌ 不算移植 | 还是模拟器，性能/输入/窗口都是别人的 |
| 重写引擎 | ❌ | NMPL 引擎 + 三部作品 + 剧本/资源格式全部要逆向，工作量是重编译的十倍 |
| 混合（关键函数手写） | 可选补充 | 抬升后个别热函数/异常路径用 C 重写，属于优化手段，不是路线 |

依据：本作代码 12.5 MB（其中 6.1 MB 是原封 SDK），lifter 已把 72,009 个函数全部抬升、**0 条不支持的指令**，
理论上“代码侧没有墙”，剩下全是系统边界。

## 2. 框架：fork XC2 Recomp（MIT）

已在本机 ns/xc2-recomp 里验证：这套 recomp/gen.py 直接把我们三个模块抬成了 216 MB 的 C（11 秒），
说明抬升器本身对 NMPL 代码无适配成本。运行时（runtime/）的能力与本作需要的边界高度吻合：

| 本作需要 | xc2-recomp runtime 现状 | 证据 |
|---|---|---|
| NVN 设备/窗口/命令缓冲/纹理/采样器/Program | 有，NVN 层 HLE + Vulkan 后端 | runtime/nvn_api_core.c、nvn_api_cmd.c、nvn_api_obj.c、nvn_ext.c、vk_*.c |
| nn::audio **audout** | 有 | runtime/ov_audio_out.c（OpenDefaultAudioOut/AudioOutBuffer） |
| Opus 语音解码 | 有 | runtime/ov_media.c |
| movie::Decoder 宿主替代（视频） | 有，按 vtable 20 个槽位覆盖 | runtime/movie.h、ov_movie.c（MOVIE_CTOR … MOVIE_ENTRIES） |
| nn::swkbd 软键盘 | 有（Win32/SDL 两套前端） | runtime/swkbd.c、swkbd_win.c |
| nn::fs（RomFS/存档） | 有 | runtime/fs.h、fs_host.c、romfs.c |
| 内核/线程/IPC | 有 | kernel.c、svc.c、ipc.c、loader.c |
| 输入（手柄/键鼠） | 有 | input*.c、input_map.c |
| 许可证 | **MIT** | LICENSE（Copyright 2026 Valiantsin Dzerakh） |

对比 Metroid-Dread-Recomp 的 runtime：它是 OpenGL + nvdrv/command-buffer 级仿真（gpu_engines.c、
host1x.c），更“模拟器”，且 runtime 是 GPL-3.0；视频走 libvpx 内置（vp9video.inc）。我们不需要
command-buffer 级仿真，NVN 层 HLE 更省事、更贴近原引擎。

**结论**：把 ns/xc2-recomp 的 recomp/ + runtime/ + tools/（去掉 XC2 专属的 tools）fork 进
本工程作为 framework/，再把 XC2 专属代码替换成本作配置与补丁。这一步是后续所有阶段的地基。

## 3. 阶段

### P0 输入（✅ 已完成）
产出：build/extracted/v0（本体）、build/extracted/latest（本体+更新）、data/expected-latest.json。
验收：IVFC 六级通过；合并树 30 文件 4,423,579,523 B；逐文件 hash 入库。

### P1 全量抬升（✅ 已完成）
产出：build/gen-all/（三个模块 → 216 MB C，89 个 chunk + 三张 dispatch 表）。
验收：main 18,897 / subsdk0 13,635 / sdk 39,477 函数，0 unsupported。

### P2 骨架与第一次编译（⏳ 下一步，通宵继续）
1. fork 框架，改标题配置（010095B01AF94000、模块表、RomFS 路径、版本号）。
2. 用 UCRT64 clang 编译“空运行时 + 抬升 C”，先求 exe 能链接出来（不要求跑）。
3. 写 tools/build_game.py 的本作版本（XC2 的 63 KB 脚本要大幅删减）。
验收：out/hayarigami.exe 链接成功；启动后能打印第一句 guest 日志。

### P3 起死回生：内核 + fs + vi
1. 宿主内存层/线程层接通，main 的 __nnmusl_init_dso → NMPL 初始化能走完。
2. nn::fs 把 RomFS: 映射到 build/extracted/latest/romfs，能读到 database.dat。
3. nn::vi 建窗口、拿到 NativeWindow。
验收：日志里出现 NMPL 初始化完成、进入首个场景，窗口打开（可以是黑屏）。

### P4 第一帧：NVN + 纹理
1. NVN 设备/队列/命令缓冲接通，Vulkan 后端出第一帧。
2. 纹理格式（NIS 的 graphics_bg.dat 解出来的贴图）经 NVN 采样器正确显示。
验收：标题画面（logo/版权页）出图且不花。

### P5 可玩：音频 + 输入 + 视频
1. audout 出声（BGM/SE）。
2. 输入映射（键盘/手柄）。
3. movie::Decoder 宿主替代播放 op→标题的 mp4。
验收：能过开场动画、进第 1 部标题、读档、玩到第一话。

### P6 三部齐活 + 打磨
1. FOAF2/FOAF3 数据切换与验证。
2. 分辨率/帧率、宽屏、存档路径、设置界面。
3. 三部各自通关一遍作为回归。

## 4. 风险

| 风险 | 等级 | 应对 |
|---|---|---|
| NVN 用法超出 XC2 runtime 已覆盖的子集（如 sRGB、多渲染目标、特殊采样器） | 中 | 2D 引擎用法窄；先跑，遇到缺的 API 按 nvn_api_*.c 现有模式补 |
| 视频：movie::Decoder 的 vtable 槽位/ABI 与本作不同 | 中 | 本作与 XC2 是不同引擎的调用方；用 movie_probe.c 那套“宿主替代 + 探针”先对表，再补 |
| Android android::* 约 100 个符号必须解析 | 中 | 这些符号只在视频路径被调用；先给桩（未调用即安全），movie::* 宿主替代后大概率不会被真正调用 |
| Nmpl::Core::CJob 多线程 + 抢占 | 中 | 抬升后的代码是普通 C，宿主用真线程；nn::os 的 65 个导入覆盖 mutex/event/semaphore/TLS，逐一对上 |
| nn::ro 模块加载（sdk/subsdk0 装载） | 中 | 框架已有 loader.c 处理多模块；本作模块表与 XC2 相同（main/sdk/subsdk0/rtld） |
| SDK 版本差异（本作 sdk 6.1 MB vs XC2 sdk） | 低 | 抬升后 SDK 也是 C，HLE 只在 nn::* 边界 |
| VS BuildTools 缺失（NativeAOT 着色器翻译器需要 link.exe） | 高（环境） | 需装 VS BuildTools 2026 + Windows SDK；或改用非 NativeAOT 的翻译器路径 |

## 5. 工作量（基于本作规模与框架完成度）

| 阶段 | 估计 |
|---|---|
| P2 骨架 + 链接 | 1–2 天 |
| P3 内核/fs/vi | 2–4 天 |
| P4 第一帧 | 3–7 天（NVN/纹理是主要不确定项） |
| P5 可玩 | 1–2 周（音频/视频/输入） |
| P6 三部 + 打磨 | 1–2 周 |
| **合计** | **约 4–7 周**（单人、有本机框架经验；不含不可预见坑） |

对比：TotK 级约 1 人年、XC2 级数月。本作是“2D 文字冒险 + 小代码面 + 现成运行时”，属于最轻的一档。

## 6. 环境现状（2026-11-09 03:4x）

| 组件 | 状态 |
|---|---|
| MSYS2 UCRT64 clang/lld/ninja/gcc + SDL3/opus/libvpx/zstd/vulkan-devel 等 | ⏳ 安装中（build/pacman.log） |
| .NET SDK 10.0.403 | ✅ |
| uv 0.13.0 / Python 3.12 + 3.14 | ✅ |
| Vulkan SDK（validation 层、vulkaninfo） | ❌ 未装（构建可用 MSYS2 vulkan-devel 顶，运行期用显卡驱动自带 loader） |
| Visual Studio BuildTools 2026 | ❌ 未装（NativeAOT 着色器翻译器需要） |
