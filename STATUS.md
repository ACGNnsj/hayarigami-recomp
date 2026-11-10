# STATUS — 2026-11-09

## 2026-11-09 下午 — 影片 H.264 解码打通（在机内真的播出来了）

一句话：**开场影片不再是跳过，而是真解码真显示**——Media Foundation 的 H.264 MFT 解
`FOAF1/movie.mp4` 的 4370 个 Annex B 包，2400+ 帧、1.2 ms/帧、0 错误、0 校验错误；
截图上就是真实的夜雨街景镜头（`build/v0/mv/f08994.png`，另有 `shot_m9.png` 的片头字卡）。

三个坑（都写进代码注释了，别再踩）：

1. **输出流不给 sample**：`GetOutputStreamInfo` 返回 `flags 0x7`，没有
   `MFT_OUTPUT_STREAM_PROVIDES_SAMPLES`，所以 `ProcessOutput` 必须自带 `IMFSample`（容量 `oi.cbSize`＝4147200）。
   传 NULL 的话每帧都是一声 `0x80070057`，而且**不会报错**。
2. **`MF_MT_MPEG_SEQUENCE_HEADER` 这个解码器不认**：把 SPS/PPS 设在输入类型上，4369 个包进、0 帧出，
   连 `END_OF_STREAM` + `COMMAND_DRAIN` 都没用；把**同一份** SPS/PPS 以 Annex B 塞在第一个 sample 前面，
   4369 进 4369 出。SPS/PPS 从容器取：`fs_host.c` 的 `note_movie()` 在打开 `.mp4` 时把文件头 1 MiB 交给
   `ov_movie.c` 的 `movie_note_media_bytes()`，按 `avcC` 盒解析（FOAF1/2 是 Main@4.0、FOAF3 是 High@4.0，
   三份记录不同，不能写死）。
3. **解码器自定几何**：1080 行的流输出是 **1920x1088**，拿 1920x1080 去 `SetOutputType` 返回 `0xc00d36b4`。
   照 `GetOutputAvailableType` 给的 NV12 尺寸拷，行距用 `mf_out_w`，两个平面各 `sw*sh`。

还有一个「静默丢帧」：我们自带的 sample 是普通内存 buffer，**没有 `IMF2DBuffer`**，
只走 `Lock2D` 的话一帧都拷不出来——日志表现为 `end of stream after 0 frames from 4373 inputs`、
错误数 0，非常难查。必须回落到 `cb->Lock` 的连续缓冲。

复现（影片约在第 140 秒后开始播）：

```bash
bash tools/_one.sh 240 build/v0/shot.png '15:0x45,30:0x45,45:0x45,...,165:0x45'
# 日志：movie: 600/1200/1800/2400 frames, decode 1.2 ms per frame
```

不动游戏的独立验证：`tools/test_mf.c` → `build/v0/test_mf.exe`（`-lmfplat -lmfuuid -lole32`），
素材 `build/v0/pk_inband.bin`（4369 包 + 前置 SPS/PPS），解出来的是 `build/v0/frame200.png`。
**用这个 harness 查 MFT 契约，比每次等 40 秒游戏快一个数量级。**

还缺：**影片音轨**（`audio/mp4a-latm` 是裸 LATM，没有 LOAS 同步头，MF 的 AAC MFT 不能直接吃），
现在还是 stub，影片是静音的。已知的音轨事实（`tools/_mp4a.py` 可复查）：

- `movie.mp4` 第 2 条 trak 是 `soun`/`mp4a`，6828 个 sample、4370 个 chunk、`stts` 单条 `(6828, 1024)` → **AAC-LC 48 kHz、双声道**。
- `esds` 里的 `DecoderSpecificInfo`（AudioSpecificConfig）5 字节：`11 90 56 e5 00`（AOT=2 LC、freqIdx=3=48k、ch=2）。
- 第一个 sample 开头是 **编码器标签串** `4c 61 76 63 35 39 2e 33 37 2e 31 30 30`（"Lavc59.37.100"），
  后面才是音频数据；游戏送来的首个包也是这串 `de 02 00 …`，所以 LATM 解析要能跳过这段 head。
- 要接的话：写一个最小的 LATM（ISO 14496-3 `AudioMuxElement`/`StreamMuxConfig`）拆包器，把每个 PayloadMux 变成
  ADTS 帧（或直接用 ASC + raw_data_block），再喂 MF 的 AAC MFT（`MFAudioFormat_AAC`，
  `MF_MT_USER_DATA` 放 ASC），输出 PCM 后接现有 audren 混音路径；`ov_movie.c` 的 `worker` 和
  `push_decoded` 已经在处理“多路输出帧”，音频可以照抄视频那条路的形状。

**注意：自动化跑到影片是靠运气的。** 进菜单/选作品的时机每次差 ±20 秒，用
`tools/_one.sh 180 shot.png '15:0x45,30:0x45,…,165:0x45'` 大约三到五次里成功一到两次；
成功时日志会有 `movie: 600 frames, decode 1.2 ms per frame`。**别把“没看到 movie: 行”当成解码坏了。**

---

# 2026-11-09 通宵进展（截至 06:1x）

> 给早上的你：这一夜没有改任何游戏文件、没有动别的项目。全部工作在
> `D:\consoles\ns\hayarigami-recomp\`。现在 **游戏已经能玩了**：标题 → 标题选择 → 第 1 部正篇开场旁白，
> 60 fps 稳定、有声音、无崩溃。影片视频已经真解码真显示（见下午那节），剩下的是**影片音轨**和**标题菜单的重影**。

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

1. **影片音轨还缺**（视频已解码显示，见上面下午那节）。本作影片是 H.264 + AAC；
   视频走 Media Foundation 的 H.264 MFT 已经通了，音频是裸 LATM（`de 02 00 4c 61 76 63 35 …`，
   没有 LOAS 同步头），要先把 LATM 拆成 ADTS/ASC 才能喂 MF 的 AAC MFT，或者自己接 `faad`/libav 的 AAC。
   现在是 stub，影片静音但剧情照常推进。
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

1. **标题菜单的重影/叠画**（现在最刺眼的一个，你在 m02362 里点的名）。已知的全部事实：
   `build/v0/dump_menu/passes.txt`（一帧 11 个 draw、1 个 pass、8 个 pipe）、
   `refs/menu/ss_04.jpg`（真机）、`build/v0/shot_menu100.png`（我们的）。
   关键线索：好多 draw 的顶点框是 `(-1234,-1234)..(3154,3154)`（旋转 45° 的大 quad，多半是那条斜向高光/血渍），
   而 UI 精灵来自一张 **768x3200 的竖长图集（tex 364）**；`XC2_DUMP_TEX=768x3200` 可以把这张图集直接落到 PNG，
   先看**图集本身对不对**（对 = 采样/UV 问题，不对 = 上传/平铺问题）。
2. 影片音轨（LATM→ADTS→MF AAC MFT，上面那节写了已知参数）。
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

---

# 2026-11-09 深夜 — 菜单重影根因找到并修好（贴图 pitch 2048→1024）

## 一句话

菜单/标题的重影不是渲染合成问题，是**贴图上传错**：`framework/runtime/nvn_tex.c:93 nvn_tex_bl_pitch`
把所有打包贴图的 GOB pitch 按 2048 对齐，但打包器实际按 **1024** 对齐。行宽 1K 块数为奇数的贴图
（1280x768 logo、1040x350 封面、768x3200 图集）反平铺时每行错 1024 字节 → 横带走位 + 镜像白字 + 黑封面。
改成 layout byte0==3（`pkg_block_h==4`）用 1024，其余保持 2048；logo/5 个故事格/第 3 作标题图实机验证全干净。

## 证据（离线，可复现）

- NMPLTEX1 头：魔数 `NMPLTEX1`，W=u32[24]、H=u32[28]、真实大小=u32[44]。
- `tools/_scan.py`（临时的，扫 `package_tex.dat`+`graphics_bg.dat` 的全部 nltx）：
  `pitch=align_up(row_bytes,1024)` 对全部 **229 个 [3,4]-layout BC 贴图**逐字节预测出 true_size（0 偏差），
  例如 logo bg5567 1280x768→983040（5120/行）、封面 ti0009-14 1040x350→655360（5120/行）、
  图集 bg5569 768x3200→2555904（3072/行）、标题底 bg1002 1920x1080→2621440（8192/行）。
- 反例：GPU 落盘 `menudump` 里 logo 以 320x192 分块看是花的、而同格式 1024x64 字条是完美的 → 贴图侧。
- 8 个 [1,0]-layout 小贴图（RLE/字条类，今天渲染本来就是干净的）继续走 2048，零行为变化。

## 改了什么

- `framework/runtime/nvn_tex.c:93-106`：`pkg_block_h==4` 时 `(row_bytes+1023)&~1023`，否则 2048（注释写了推导）。
- `framework/runtime/nvn_tex.h:13`：注释里的 2048→1024。
- 重编：`bash tools/build_haya.sh`（产物 `build/v0/haya.exe`，本次 64919040B）。

## 实机验证（全部 PrintWindow 截图在 `build/v0/`）

- `gv_pack.png`→`gv_skip.png`→`gv_menu2.png`：E 跳过片头 → 标题 logo 干净 → 主菜单 5 格（蜘蛛男/镜中新娘/寄生/湖底/天狗）全干净。
- `le_down.png`：启动 attract 轮到第 3 作标题图，干净。封面 6 张（ti0009-14）与 logo/图集同组，构造上已修好，逐张目检留给下次。
- 标题栏已是 `Hayarigami Recomp`（交接文档里的 `XC2 Recomp` 旧问题看起来已不在）。

## 新发现：片头播完自然结束会黑屏卡死（2/2 复现，和 pitch 无关，电影后端没动过）

- 现象：片头放到 EOS（`movie: end of stream after 3799/3811 frames from 4372/4373 inputs, 0 errors`，MF 后端正常上报），
  之后黑屏、无输入响应（聚焦的 E/Enter×5 均无视）、`run.log` 冻结、进程活着、overlay 60fps。跳过（中途按键）则正常进字幕→标题。
- 后端侧 EOS 已推进 `ndecoded`（`ov_movie.c:732-738`），`movie_tick` 每帧 `release_due`+`collect`+`fire`（826-840 行）理论上会发事件；
  游戏就是不往下走。主嫌疑：游戏侧等的帧数和实际交出的对不上（inputs 4372 vs frames 3799，B 帧合并导致差 500+ 帧；
  若游戏按 inputs/container 计数等帧，永远等不到）——先核对游戏侧 movie 等待循环的计数器，再看事件/AcquireOutput。

## 输入踩坑（省得重踩）

- PostMessage 发键**永远没用**：`framework/runtime/input_win.c:203` 用 `GetAsyncKeyState` 读真实键态，只认 `keybd_event`。
- 定稿键位（`input_map.c:16-23`）：确认=E（B_A），取消=LShift（B_B），菜单=方向键，Plus=Tab。Enter 没绑定，之前全打空。
- `_tap_seq.ps1` 自带 AppActivate 聚焦，`_tap1.ps1` 不带——键发丢 90% 是窗口没聚焦。
- `_one.sh` 的 TAPS 为空=不按键；游戏无操作会自动播 attract（标题→launcher 轮播→第 1 作片头），别再跟定时器搏斗。
- 一次只留一个 haya 进程：job_kill 杀不掉游戏本体，残留的旧进程会抢走截图与按键（今晚被坑两次）。
- `_run.sh` 等游戏自己退出（无 kill 超时）：卡死=job 永远不回，先杀进程再收 job。

## 2026-11-10 凌晨 — EOS 挂死的根因收敛 + 收尾验证（eos6/eos7）

- 心跳实锤：`movie_tick` 里加了 `tick alive`（每 1800 ticks，`ov_movie.c:830-840`），
  eos6 证明游戏中途等待时 present 一直在跑（ticks 到 12600+）。`rt_call` 要 guest Cpu，worker 线程里 `fire()` 不安全——修只能走游戏线程。
- eos6 新形态：115 秒处 3 个 MFT 解码错 `hr=0xc00d36b5`，之后静默全败（errors>4 不再打 log），
  `ready=5` 卡住、worker 空转、600 秒结束停在冻结的影片帧。解码错不 abort 是对的（循环继续），
  但 3 个坏帧就能把流饿死——缺口。已加 `(in)/(out)` 分期 log（`ov_movie.c:672-714`），下次直接定位。
- 修 B（已进二进制，未验证）：`ov_acquire_output` 里 EOS 若排第一，直接在 acquire 线程交接
  （`ov_movie.c:1244-1253`，log `EOS drained via acquire`），不再依赖 post-EOS 的那一次 present。只读 `m->mu` 下操作，无 guest 调用，线程安全。
- eos7（同二进制，cache 热）：游戏自己在 404 帧停了影片（`stop after 404 frames`，eos5 是 1985 帧），
  无 EOS、无错、无 hang，600 秒跑满 35993 presents 正常退出，最终停在汉化 credits/license 页。
  结论：停播点是游戏逻辑（404/1985/全片不定），INPUT_FORCE=1 只是让失焦键有效、不注入幻影键。
- 状态：修 B 待一次自然 EOS 流程验证（eos8 在跑，同二进制）。验证标记：`EOS drained via acquire` 或 `EOS handed to ready` + 游戏继续。
- eos8（同二进制）：600 秒全程无 movie open，终点是游戏选择菜单——三封面全干净（1 代鬼脸/2 代浴缸/3 代隧道，中文排版正常），
  说明 pitch 修顺带治好了封面黑块（ti0009-14 正是 [3,4]-layout 批）。无输入流程不稳定：有时播片、有时停菜单，修 B 验证必须按键驱动。

- eos9（同二进制，按键驱动：约 360 秒按一次 E 选中 game1）：影片正常解码到自然 EOS
  （`end of stream after 3801 frames from 4372 inputs (1.32ms/f, 0 errors)`），
  `EOS handed to ready (handed=3617)` 走 TICK 路径（修 B 的 drain 没触发），
  `game acquired EOS frame (index=6, remaining=0)`——后端 EOS 交付已证可用。
  但游戏在拿到 EOS 后彻底卡死：无 stop/destroy/新 movie、无 present（tick alive 停在 4）、
  单线程 CPU +2.5s/15s 空转；E 键对卡死进程无效（硬 hang，非等输入）。
  线程快照：17612 RUNNING 40s CPU（空转线程）、50764 movie worker Wait、48444 present 线程 Wait。
  hang.dmp 415KB 已抓，线程/模块流解析通了但 CONTEXT 布局不对、RIP 没恢复。
  下一步（bin 已改、build 中）：ov_d0/d2/stop/release/get_output/get_last_error 六处入口 log，
  驱动跑 EOS10，看 EOS 之后游戏到底调了什么。

- eos10（按键驱动 E@360s，900s 预算，tracing 二进制）：复现了双 EOS 序列，全程如下——
  - line 22848 `game acquired EOS frame (index=0, remaining=0)`（短片 A）：之后 Get(0)/Release(0)，
    游戏立刻又起一个解码会话（line 22853 `H.264 MFT decoding 1920x1080`），tick alive 正常（1800/3600/5400/7200），
    说明游戏在 EOS#1 之后完全正常地继续了。A=被 E 选中的短片（logo/过场头），B=正片。
  - line 39145 `end of stream after 3806 frames from 4373 inputs (2.17ms/f, max 41.03, 0 errors)`（正片 B，
    与 eos9 的 3801 帧同一部），`EOS handed to ready (handed=3622)` 走 TICK 路径，
    `game acquired EOS frame (index=4, remaining=0)` → Release(4) → 之后全静默。
  - hang 确认：900 秒预算过期 10 分钟进程仍活着（pid 22912，CPU 667s/1500s wall，单核 ~44% 空转），
    run.log 停在 Release(4)（39188 行），无 Stop/D0/D2/新 movie，无 present。
    挂屏截图 build/v0/eos10_hung.png = 纯白窗口（present 冻结）。
  - 根因定位关键：boot.c:335-343，`--seconds` 只在 world clock 过 S 后的第一个 present 退出；
    present 冻结 ⇒ 预算不触发 ⇒ 进程永远不退。eos9 在 600s 退了说明当时还有 present（或 world clock 在走），
    eos10 的 present/ world clock 全停——两次 hang 的冻结深度不一样。
  - 结论：hang 点在“游戏拿到正片 EOS 并 release 之后、调 Stop/开新片之前”，游戏线程 guest 内空转（无 host 调用），
    不 present。下一步：XC2_HANG_DUMP 看 guest 线程到底在等什么（boot.c:293 kern_hang_dump）。
- eos16/19（E@100，instrumented 二进制）：复现 hang 新形态。movie-A stub EOS idx0 → movie-B 3804f/4370in/0err →
  EOS#2。eos16 游戏拿了 EOS#2（idx3）后黑屏、present 冻在 frame 15000；eos19 游戏没拿 EOS#2 就冻。
  pump（T2）全程 flushing 到日志末尾（153745 次，n=0-3，主力 n=3），泵本身没 wedged —— hang 在 main/present 侧。
- eos19 + XC2_HANG_DUMP=60 抓到真凶：main 线程卡在 f_70002bfdcc（join T_b=0x1020），T_b 在 pump 自旋里
  永远不退出。机制（v5，定稿）：T_b 每 tick 把 S  pending（n≤3）经 Q_out（O+0x528，cap 32）发给 T_a；
  T_a 消费（正常播放时 count 在 0-6 振荡，已用 qwords 日志实证）。终局 teardown：block1 先 Send(Q,0)
  让 T_a 退出（join OK），block2 再 SignalEvent(O+0x48) 想让 T_b 经 +0x70 臂走 0ca4 退出。
  但 T_b 若在 signal 到达时正卡在 Send（Q 已满：T_a 死后十几次 flush 就填满 32），就永远到不了
  dispatch 看 signal → join 永挂 → present 冻 → 黑屏。eos11 dump（Q 32/32 full + T_b send-blocked）是同一机制。
  设计本身没错（holder↔event 绑定已从 ctor 逐对核对：+0x70↔+0x48 等 9 对全对），纯粹是 teardown race。
- FIX（已进二进制，deterministic）：pump 两个 flush 族入口（0ad0 用 [sp+0x88]，0b70 用 [sp+0x8c]）加
  Q-space clamp：读 count=[Q+0x2c]、cap=[Q+0x28]（qwords 实测定位，之前误读 +0x28/+0x24 已纠正），
  满则直接跳 burst-end（08d4/0958 → 重回 multiwait → 必见 stop → 退出），不满则 N=min(N, space-1)。
  正常播放 count≤6 从不触发（零行为变化）；只在 teardown race 窗口激活。T_b 永不 send-block ⇒ 永不 miss stop。
- 重放：tools/pump_clamp.patch（由 .bak-diag diff 生成，已验证 patch clean + roundtrip identical），
  附带 stop-signal/pump-exit 两行 log（每 run 各 1 行）+ flush log。re-lift 后重打 patch 再按 compile_one.sh 重编 main_0023.c + 常规 relink。
- 验证状态：EOS20/21/22/23（clamp 前，v2 日志二进制）连续 4 次 clean teardown（stop+exit，无 hang；
  日志本身拖慢 T_b 掩盖了 race）。EOS24-29 用 clamp 二进制但 tap 全 miss（下午流程变慢+相位彩票，select 窗口
  在 150-350s 间漂）。clamp 本体：编译通过、boot 正常、无回归（attract/menu 下 0-1 flush，游戏正常跑）。
  完整 hang→fix 对照仍待一次幸运 run（landing + B 全播 + EOS#2 + teardown）；逻辑上已 airtight。
- 遗留：(1) movie-B open 后不起播的新 stall（EOS25 一次：B open、无 decode、无 tick、黑屏、present 仍走，
  疑 E@110 干扰 open/start 或 MF 源偶发）；(2) S（movie 音频，stub LATM）永不 drain 是 race 的上游，
  后端若能补 EOS 排空会更治本；(3) save/LATM 真声/窗口标题/文档仍 open（m00031）。
## 2026-11-10 14:53 #3 AAC 真解码实现完毕 (A 方案)
- ov_movie.c + movie.h：AAC 会话走 host（type 4），LOAS/LATM 剥头 -> ADTS 重装 -> MF AAC MFT -> PCM 进 out[]。
- 细节：SMC 自解析（首包 StreamMuxConfig），esds ASC (11 90, LC/48k/立体声) 做默认；MP4 样本证实裸 AAC (首字节 21 1a = ID_CPE)。
- 编译 -Wall 零警告；initguid.h 就地实例化 CLSID_CMSAACDecMFT（lld 不认 wmcodecdsp 导入）。
- tools/aac_latm.patch 已存 (426 行 diff)；.bak-aac 回滚点齐。
- haya.exe 64,974,848 B，25s probe ALIVE + 110KB 日志，启动正常。
- 待验证（需进电影 run）：首包到底是 LOAS/LATM 还是裸透传（dump 定）、MFT 输出字节数、S 是否 drain。

## 2026-11-10 16:30 #3 AAC 验证完毕 + #2 菜单重影结案（复核）

### #3 AAC 真解码验证（aac8/aac9）
- aac8（协商）：MFT 可用输入模板是 6ch/32bit/12B-user（不是 2ch）——clone 模板后改 ch=2/rate=48k（in-variant V0）
  拿到 S_OK(0)，AAC 解码 48000Hz x2，真帧输出。V0 定稿。
- aac9（E@100..500/40s spread 覆盖 select 彩票窗口）：movie-A 521 音频 + 1117 视频帧并 audio EOS；
  movie-B 1855 视频 + 953 音频帧，audio EOS 953/1191 inputs；全程 0 errors；两次 stop+destroy 干净有序；
  642 pump flush 全小 n、无 wedge。帧 acquire/release 本来就静默（只打 EOS-acquire log）。
- 附带结论：电影中按 E 不会跳过（B 在 3 次 tap 下完整播完）——老的 aac2/3 中断是 worker-sleep bug，
  不是游戏行为。PATCH 共 501 行已存，#3 功能性 FIX（可听性待人耳）。
- 上游遗留 (2)（S 永不 drain）因 AAC 真解码已自然缓解：音频帧被正常 consume + audio EOS 送达。

### #2 菜单重影结案（与 11-09 深夜 pitch 修复交叉验证）
- 交接文档 S8.1 写于 11-09 16:20，早于 pitch 修复（nvn_tex.c 23:14，1024 规则）。menudump（11-09 15:19）
  是坏 pitch 下抓的——今晚复核 passes.txt 确认受害的正是 768x3200 atlas（pipe8，5 draws 同 tex374）。
- 决定性证据：gv_skip.png（11-09 23:29，修复后）= pass_0000 同款文字菜单（logo + 从头/继续/系统），
  每个选项只出现一次、无重影；gv_menu.png（序章/剧本）同样干净。nvn_tex.c 注释已点名 atlas 是受害者，
  且 1024 规则对 229 个 [3,4] 纹理（含 bg5569 atlas 2555904B）逐字节精确——数学上已无残留。
- 结论：#2 已于 11-09 深夜修复并实机验证，无需再抓 atlas/UV。今晚复核（passes 解剖、start.dat 扫描、
  YKCMP 碰壁、blocks 视图不可读）全部与该结论一致。vk_dump.c 顺手加了 _blocks 作业的 raw .bin 落盘
  （write_images，5 行），以后离线解 BC 不再被 PNG 缩放毁数据；已随本次二进制重编。
- 交接文档 S8.1、S8.5（标题栏 XC2）均已 stale：以本 STATUS 为准。

## 2026-11-10 晚 — 音频可听性验证 + 真根因（模板 2）
- 用户晚饭不在：WAV 不做人耳，改信号自测。`build/v0/aac_test.wav`（6827 帧→27963392 PCM 字节/145.6s）：
  静音仅 2/145 秒（片头黑场位），峰值 3k-20k 健康，DC 小，立体声差分 0.83（真立体声），削波 8 帧。
  结论：解码器 + 内容链路都对，是正片节目音频（rms NaN 是自测脚本算术 bug，忽略）。
- 根因（探针 `tools/aac_probe.c`，ucrt64 gcc 直连 MF）：游戏一直用模板 0（pay=0/raw）clone 后改 pay=1，
  MFT 对它 S_OK 但永远 0 字节（pay=0/1 都试过、单/立体声帧都试过，40 纯 CPE 帧也是 0）。
  真解是**模板 2（原生 ADTS，pay=1）**：40 帧→163840 B 严丝合缝（每帧 1024 立体声 s16）。
  另：v1 式 2 字节 ASC 会被拒（0xc00d36b4）；MFT 要 PROVIDES_SAMPLES（outinfo flags=0x1），
  传自备 sample 会 E_INVALIDARG——游戏 `aac_out` 本来就是对的，探针抄它才通。
- 游戏改动：`ov_movie.c` `aac_negotiate_in` 两处 `GetInputAvailableType(...,0,...)` → index 2（原生 ADTS），
  ch=2/48k 覆盖保持（探针验证正是这么出立体声）。haya 19:25 重编（含改动），19:55 又加 PCM 计数器
  （`Movie.aac_pcm_total`，`aac_out` 累加，`aac_close` 打 `AAC total PCM`）后重编。
- 工具留档：`tools/_adts.py`（MP4 demux + LOAS 跳过 + ADTS 打包，sample0 293B Lavc tag 跳过），
  `tools/aac_probe.c`（argv: adts wav pay ascBlob templateIdx），`build/v0/audmap.json`（6828 样本表）。
- AV3 验证 run（19:56 起，detached 640s，taps 100-580）：待读结果——EOS？`AAC total PCM` 行？teardown（clamp 验证）？

## 2026-11-11 helper 进程验证通过（audio fixed）
- 结论：CMSAACDecMFT 只认主线程 + 调用方必须提供输出缓冲（drain 侧 GetOutputStreamInfo + 自备 sample/buffer，否则 ProcessOutput 失败、输出积压导致后续 ProcessInput 报 MF_E_NOTACCEPTING=0xc00d36b5）。helper（tools/aac_srv.exe，主线程 MF + stdin/stdout 帧协议）3 帧烟雾：8204B/0 失败。
- 中间乌龙：helper 初版喂帧失败——非线程/字节问题（dbg 证明字节与 probe 一致），纯是 drain_full 没给输出缓冲；另 _setmode 文本模式会把 0x1A 当 EOF（S2 教训），binary 必备。
- 游戏侧：ov_movie.c 改管道客户端（CreateProcess 继承 pipe，stderr 进 game log），build_haya.sh 重编 haya.exe（23:49）。
- 验证 run（260s，E@95/105/115/125）：movie-B 启动，helper spawn×1，AAC total PCM 233472B，36B5=0，EOS×1。但后续 taps 把电影跳过了（全程只播 ~1.2s 音频）——完整长片 + EOS clamp 仍待一次干净 run（单 tap + 用户离开时跑）。
- 下一步：干净 full-movie run（验证 acquire-drain EOS fix B + clamp）；#4 手动存档；LATM；文档更新。

## 2026-11-11 full-movie 验证通过（audio + EOS + teardown 全绿）
- pbuf 两修（append 不丢未播 PCM；aac_srv_mu 覆盖 out/close/configure）后重编 haya（01:19），590s 自适应 taps run（E@90/150 中，210 前见 movie: head 停手）。
- 结果：36B5=0，xact 失败 0；PCM 进度破 4MB×6 次，单部电影 close 打印 total PCM 27852800B（=145s 全长音频）；自然 EOS×2（3799 帧 0 errors；6800 帧 0 errors）；Stop 后解码器正常销毁，游戏继续渲染（2152 行非 pump 日志），无旧式 EOS 卡死。
- "EOS drained via acquire" 0 次触发：游戏自己拿到了视频 EOS——旧 hang 很可能本就是音频饥饿连锁，音频通了 pump 就正常了。171/3799 帧为保同步 drop，可接受。
- run 被 590s 工具超时掐掉（非 hang），属预期内。
- 待办：#4 手动存档；EOS clamp；LATM（注：播的 mime 就是 audio/mp4a-lat-m，已通）；文档更新。

## 2026-11-11 EOS clamp 验证 run 全绿（teardown race 结案）+ #4 存档待跑
- 验证 run（tools/_valid_run.ps1，--seconds 600，taps E@100/110 落中 + E@150 多余一发无害）：
  movie-A（1109 视频 + 524 音频帧，audio EOS，PCM 4546560B）→ movie-B 全片（3795 视频 + 6800 音频帧，
  0 errors，PCM 27852800B = 145s 全长）→ 又一部全片（同 3795/6800，0 errors，全长 PCM）→ 第 4 部 open 后到 600s 自退。
  每次 Stop + 解码器销毁干净，EOS 后游戏继续进剧本（教室场景截图 valid_eos_manual.png），
  结尾 boot: passed（5054663 SVCs，35992 presented，0 validation errors / 0 shader failures）——旧 join-hang  signature（present 冻 + 进程赖活）零出现。
- 结论：EOS hang 根因（音频饥饿连锁）已随 AAC 真解码消除；pump Q-space clamp 在二进制里作为保底（正常播放 count≤6 永不触发）。
  EOS clamp 项关闭。复现脚本与截图：tools/_valid_run.ps1，build/v0/valid_{pre,135,eos_manual,post1}.png。
- 教训（已进脚本注释）：游戏 stdout 是全缓冲，redirect 文件整场 0 字节、退出/被杀才落盘——run 中轮询必须读 .err（unbuffered，
  [host] 行双写）；valid_run.log 里只有一条人手注入的 landing marker（计数 +1，非游戏输出）。
- 附带确认：窗口标题两后端早就是 "Hayarigami Recomp"（sdl.c:250 / win.c:256），交接 §8.5 stale；
  ov_movie.c:569-570 "AAC stays stubbed" 注释已改成 helper 现状；run.log 实证 mime=audio/mp4a-latm 48k 立体声（LATM 注记完）。
- 待办只剩 #4 手动存档往返：tools/_saverun.ps1 已备好（--seconds 3600 + keep-alive，落中即停手，留进程给手玩），等用户离开再跑。

## 2026-11-11 #4 手动存档关闭（用户实机存档成功）
- 用户亲自进游戏手存：build/profile/save/<uid>/PLAY000（164832 B）+ SYS（250 B），02:30 落盘；
  fs commit 日志 "2 files, 1 changed (0.2 MiB written), 1 unchanged linked, in 7 ms"——后端原子提交链工作正常。
- 后端早通（fs_host.c MountSave/Commit + probe_restart/tx_commit 自测），这次是真 gameplay 存档点往返的一半（存）；
  读档一半待补（可选：重进标题选 继续 看是否回到存档场景）。
- saverun keep-alive job 用户已手动结束，haya 进程同步退出，无残留。
