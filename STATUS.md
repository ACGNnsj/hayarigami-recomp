# STATUS — 2026-11-09 通宵进展（截至 06:1x）

> 给早上的你：这一夜没有改任何游戏文件、没有动别的项目。全部工作在
> `D:\consoles\ns\hayarigami-recomp\`。现在 **游戏已经能玩了**：标题 → 标题选择 → 第 1 部正篇开场旁白，
> 60 fps 稳定、有声音、无崩溃。剩下的是影片解码和标题菜单的视觉问题。

## 一句话

从「一个跑不起来的 fork」推进到「**能进正篇读旁白**」：修好了打包纹理的行 pitch（标题逐像素正确）、
打通了键盘输入、补上了 `movie::Decoder` 的 5 参构造签名并用 stub 跳过了 H.264/AAC 影片、
确认了 audren 混音→SDL 设备这条音频链在出声。

## 今晚做了什么（按时间，全部可复现）

| 时间 | 事情 | 证据 |
|---|---|---|
| 04:56 | packaged 纹理行 pitch 向上对齐到 2048 字节，标题画面与官方 key art 逐像素一致 | `build/v0/shot_pitch.png` |
| 05:20 | 输入打通：`ikb_foreground` 前台判断改为 `XC2_INPUT_FORCE`，波纹即可进菜单（**Enter 没绑定，E 才是 A 键**） | `build/v0/shot_stub.png`、`run.log` |
| 05:35 | 影片层：`movie::Decoder` 本作是 5 参构造（含 DecoderMode+int），补 `need_any()` 多签名表 + 4 条 HOST_OVERRIDE | `run.log` 的 `movie: decoder type 1 format 4` |
| 05:36 | 影片是 **H.264(avc) + AAC**，库路径会 `svc #0x26` abort；改为 stub 解码器（读 4 包就报 EOS） | `XC2_MOVIE_STUB`（默认开） |
| 05:49 | 标题选择画面正确：三作封面竖排 + 「タイトルを選んでください。」 | `build/v0/shot_t30.png` |
| 05:57 | **进正篇**：暗室壁面 + 旁白「ここは暗い。暗い部屋のようだ。」 | `build/v0/shot_story.png` |
| 06:00 | 稳定性：连续 300 秒、17,997 帧、mean 60.0 fps、1% low 58.8 fps、0 未实现 NVN 调用、无 FATAL | `run.log` 的 `boot: passed` |
| 06:07 | 音频取证：`XC2_TRACE=audio` → `first nonzero output after 342 frames`，rms 0.03–0.11、peak 0.96、underruns 0 | `run.log` |

## 现在怎么自己跑一遍

```bash
cd /d/consoles/ns/hayarigami-recomp
export PATH=/c/msys64/ucrt64/bin:$PATH
export XC2_ROMFS=D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs
export XC2_INPUT_FORCE=1          # 窗口拿不到前台时也要能按键
./build/v0/haya.exe --seconds 120 --shot build/v0/shot.png
```

- 重新构建：`bash tools/build_haya.sh > build/v0/build.log 2>&1`（约 1 分钟，改了几个文件就只重编那些）。
- 按键（`framework/runtime/input_map.c` 默认表）：**E = A**、空格 = X、左 Shift = B、Z/F = ZR、Q = L、R = R、
  WASD = 左摇杆、方向键 = 右摇杆、1/2/3/4 = 十字键、Tab = +、M = −。
- 调试开关：`XC2_MOVIE_STUB=0` 关影片 stub、`XC2_DRAW_ONLY=<first>:<last>` 只画本帧第几个 draw（查分层用它）、
  `XC2_AUDIO_STATS=1` 打音频峰值、`XC2_TRACE=audio` 打电平表、`XC2_DUMP=<frame>` + `XC2_DUMP_DIR` 落帧取证。

## 已知问题（按优先级）

1. **影片不能播**（唯一的“真缺件”）。本作影片是 H.264/AAC，现在被 stub 跳过（剧情照常推进，只是看不到动画）。
   要真解码：Windows 上最省事是 Media Foundation（`MFCreateSourceReader`，系统自带、无 GPL），
   或 `openh264` + `fdk-aac`/`faad`。host 侧接到 `ov_movie.c` 的 `worker` 线程即可，接口已经现成。
2. **第 1 部标题菜单叠了两套**：正确的一套（初めから 橙色、続きから、特典、オプション設定、
   他タイトルへ移動 斜排、権利表記）**加上**一套约 2 倍大、错位的灰色重影（巨大 logo 带黑底方块、
   続き/オプション/特典/シナリオ 的大字），15 个 draw 在同一 pass 里。证据 `build/v0/shot_menu100.png`，
   正确样子见官方手册 `refs/menu/ss_04.jpg`。dump 里 blend 是 SRC_ALPHA/ONE_MINUS_SRC_ALPHA、
   depth func = ALWAYS，所以不是混合/深度问题，更像**同一批 UI 被画了第二遍**（缩放/半分辨率错），
   或者 1・2・3 パック 的启动器界面还留在下面。
   排查工具：`XC2_DRAW_ONLY=<first>:<last>`（`vk_exec.c`，按 draw 序号过滤）。**注意它现在跑出来恒黑**
   （`build/v0/layer_*.png`、`shot_iso2.png` 都是纯黑，帧数正常），所以先用它之前得先修掉——
   怀疑跳过 draw 之后接续的 pass 状态没恢复。这是明天第一件小事。
3. **存档**：还没走过保存/读取流程（菜单里没点进去）。需要确认 `nn::fs` 的 save data 目录映射。
4. **文本窗口偏亮**：旁白窗口是半透明白框，需要和官方截图再对一次是不是本该更暗/更透明。

## 明天从哪继续

1. 先修标题菜单重叠（视觉上最刺眼，且用 `XC2_DRAW_ONLY` 已经能逐层定位，1 小时内能定性）。
2. 接 H.264/AAC 解码（Media Foundation 优先），让 `XC2_MOVIE_STUB` 默认关掉。
3. 菜单导航 + 存档读写。
4. 收尾：把 `xc2.ini` 里本作专属的默认值、键位说明、以及 `docs/` 的引擎笔记补齐。

## 环境事实（省得重新踩）

- 工具链：MSYS2 **UCRT64**（clang 23.1.5、lld、ninja 1.13.2、SDL3、opus、libvpx、zstd、vulkan-devel）；
  ×64 native clang 不能吃 `/d/...` 这种 MSYS 路径（`-I` 必须给 `D:/...`）。
- .NET 10（10.0.403）在 `C:\Program Files\dotnet`，着色器翻译器靠它 + MSVC 的 link.exe 构建；
  产物要拷到 `build/xlate/` 才会被运行时找到。
- GPU：RTX 4080 Laptop（Vulkan 1.4.357）。运行 exe 必须 `export PATH=/c/msys64/ucrt64/bin:$PATH`，否则 0xC0000135。
- 长跑一律用后台作业（`ops_bash run_in_background`），前台 120 秒超时会**杀掉整个进程树**。

## 没动的文件

- `ns/hr-bcjna.xci`、`ns/010095B01AF94000/`：只读，未修改。
- `build/extracted/*`：只读的游戏数据，所有产物都在 `build/v0/` 下。
