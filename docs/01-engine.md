# 01 引擎与代码面

## 1. 引擎身份

字符串里直接写明了构建来源：

```
D:/NMPL_rev1475_hayarigami/NMPL/source/SysUtil/SoftwareKeyboard/nx/SoftwareKeyboardNx.cpp
C:/Users/PC-009/Documents/HAYARIGAMI/ps123/program/game/src/Old/FOAF3/System/Util/NisTaskList.cpp
C:/Users/PC-009/Documents/HAYARIGAMI/ps123/program/game/src/Old/FOAF3/Game/GameData.cpp(%d)
C:\Users\PC-009\Documents\HAYARIGAMI\ps123\program\game\NX64\FOAF123\Tfoaf3_NX64_FOAF123.nss
```

- **NMPL**（Nippon Multi Platform Library），rev **1475** 的 `hayarigami` 定制分支 —— Nippon Ichi 自研跨平台引擎。
- 命名空间证据：`Nmpl::Core::CJob`（任务/线程池）、`Nmpl::Gra::CGraShaderMgrBase`、
  `Nmpl::Gra::CGraShaderBase`（`s_instanceFormat`/`s_instanceBuffer`/`s_instanceNum`）、
  `Nmpl::Gra::Renderer::CGraRendererBase`（`s_tlsRenderStateId_` 线程局部渲染状态）。
- 游戏侧目录：`src/Old/FOAF`+部号，说明三部共用一套 NMPL 代码、以 `FOAF1/2/3` 数据目录区分。
- 图形不走 Unity/中间件，**直接调 NVN**：`nv::InitializeGraphics`、`nv::SetGraphicsAllocator`、
  `nvnBootstrapLoader`，以及 `nvnQueueBuilder*`/`nvnTextureBuilder*`/`nvnSamplerBuilder*`/
  `nvnProgram*`/`nvnCommandBuffer*` 等一整组 NVN 名字（这些名字出现在 main 的字符串里，是 NVN 装载器
  按名字解析导出表用的）。音频走 `nn::audio` 的 **audout**（`OpenDefaultAudioOut`、
  `AppendAudioOutBuffer`…）。视频走 `libmovie` + Android media 栈（`movie::Extractor`、
  `movie::Decoder`、`android::*` 一大批），由系统库 `multimedia.nss` 提供。

## 2. 模块与规模（实测）

提取自合并树 `build/extracted/latest/exefs`（更新版 main）：

| 模块 | NSO 文件大小 | .text | 函数数（lifter 发现） | 抬升出的 C | 依赖模块 |
|---|---:|---:|---:|---:|---|
| main（游戏） | 2,248,368 | 2,925,696 | **18,897** | 51 MB | multimedia.nss, nnSdk.nss |
| subsdk0（引擎） | 3,385,994 | 3,402,784 | **13,635** | 59 MB | — |
| sdk（任天堂 SDK） | 6,025,528 | 6,145,344 | **39,477** | 106 MB | — |
| rtld（加载器） | 7,207 | 5,968 | 不抬升（宿主替代） | — | — |
| **合计** | | **12,479,792** | **72,009** | **216 MB** | |

抬升统计（`recomp/gen.py`，14 进程）：

```
main:    18897 functions, 311 jump tables, 1 all-label fallback, 436 br via dispatch, 6423 traps (0 unsupported)
subsdk0: 13635 functions, 335 jump tables, 0 all-label fallback, 3961 br via dispatch, 5592 traps (0 unsupported)
sdk:     39477 functions, 676 jump tables, 16 all-label fallback, 10278 br via dispatch, 20370 traps (0 unsupported)
total 11s
```

**0 unsupported** 是关键结论：这台 lifter 认识我们这三个模块里出现的全部 AArch64 指令，包括
NEON/SIMD、LDXP/STXP、CRC32 等。`traps` 是 lifter 归为 `trap` 类的指令数（AArch64 的 `udf`/`brk`，
多半是代码段里的填充/数据或 SDK 的 panic 桩），不是“翻译不了”。

对比：XC2 的 main 是几十 MB 级代码、TotK 更甚；本作 12.5 MB 代码里还有 6.1 MB 是原封不动的 SDK。
真正要理解/打补丁的游戏+引擎代码 ≈ 6.3 MB / 32,532 个函数 —— 而且是 2D 文字冒险。

## 3. 导入面（HLE 工作面）

main + subsdk0 去重后 **892 个导入符号**（main 328 / subsdk0 661，有重叠）。按命名空间：

| 命名空间 | 个数 | 说明 |
|---|---:|---|
| libc / C++ / NVN / movie / multimedia / NvOs | 357 | libc、`std::__1`、NVN 导出、libmovie、Android 栈 |
| nn::audio | 82 | **audout**（不是 audren）：打开/追加缓冲、混音、音量 |
| nn::os | 65 | 线程、互斥、信号量、TLS、Tick、多等待 |
| nn::hid | 19 | 手柄/Npad 状态 |
| nn::fs | 15 | RomFS 挂载、文件读写、存档挂载/提交 |
| nn::sf | 12 | hipc IPC 客户端（服务解析） |
| nn::oe | 10 | 运行模式、焦点、性能配置、显示分辨率 |
| nn::vi | 5 | Display/Layer/NativeWindow、vsync |
| nn::ro | 6 | 模块加载/符号查找（sdk/subsdk0 的装载） |
| nn::web | 6 | 打开网页（帮助/版权页，可能可选） |
| nn::account | 6 | 用户选择、昵称 |
| nn::swkbd | 6 | 软键盘（输入名字） |
| nn::mem / lmem | 9 | `StandardAllocator`、`CreateExpHeap` |
| nn::util / diag / time / codec / nifm / err | 12 | UTF 转换、断言、时间、**Opus 解码**、网络初始化 |

其中 `android::*` 约 100 个（`VectorImpl`、`BBinder`、`Parcel`、`GraphicBuffer`、
`SurfaceComposerClient`…）全部来自视频播放路径，由 `multimedia.nss` 提供。

## 4. 这对移植意味着什么

1. **代码可以整段抬升，不需要逆向游戏逻辑**。NMPL 自己的 `.dat` 解析器、脚本解释器、渲染提交都在
   subsdk0/main 里，抬升后原样运行；我们只需要 HLE 它脚下的 Horizon 系统调用。
2. **不需要解析 `.dat` 资源格式**（除非以后要做 mod）。`graphics_bg.dat`、`graphics_ci.dat`、
   `start.dat`、`sound_*.dat`、`database.dat`、`package_tex.dat` 都由游戏自己的代码读，
   宿主只要把 `nn::fs` 映射到本地目录即可。
3. **图形是“最小 NVN”**：2D 四边形 + 精灵 + 文本，没有复杂 3D、没有大型 G 缓冲。NVN→Vulkan 层
   只需覆盖 engine 实际用到的那部分 API 与 shader 形态。
4. **三处真活**：视频（libmovie/Android）、音频（audout + Opus 语音）、线程（`Nmpl::Core::CJob`
   多线程 + `nn::os` 抢占）。这三块决定了“能不能玩”，图形反而不是最大风险。
5. **sdk 模块 39,477 个函数**是任天堂 SDK 的静态库，里面有大量用不到的分支；HLE 到 `nn::*` 符号层，
   sdk 里真正被调用的入口是少数，先跑起来再逐个补。

## 5. 数据格式（RomFS）

| 文件 | 用途（推断依据） |
|---|---|
| `FOAF{1,2,3}/database.dat` | 条目数据库（46 KB–55 KB，随部不同） |
| `FOAF{1,2,3}/start.dat` | 启动脚本/场景入口（28–148 MB） |
| `FOAF{1,2,3}/graphics_bg.dat` | 背景图（401 MB / 682 MB / 423 MB） |
| `FOAF{1,2,3}/graphics_ci.dat` | 立绘（337 MB / 318 MB / 388 MB） |
| `FOAF{1,2,3}/sound/sound_bgm.dat`、`sound_se.dat` | BGM / 音效 |
| `FOAF1/movie.mp4`、`ed1.mp4`、`ed2.mp4` | 开场/ED 影片 |
| `FOAF2/movie.mp4`、`FOAF3/movie.mp4`、`FOAF3/{1,2,5}.mp4` | 影片 |
| `package_tex.dat` | 共享贴图包（字体、UI） |
| `database.dat`、`sound/sound_{bgm,se}.dat`（根） | 三部共享 |
