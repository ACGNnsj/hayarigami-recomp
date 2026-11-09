# Hayarigami Recomp — 真流行之神 1・2・3 合集 → PC

*Shin Hayarigami 1・2・3 Pack* (Nintendo Switch, **010095B01AF94000**) 的静态重编译移植工程：把游戏的
ARM64 代码抬升成 C，在 PC 上用宿主运行时（Horizon HLE + NVN→Vulkan）直接跑，不是模拟器。

> 本仓库不含任何游戏文件。要用自己的正版卡带转储（本体 XCI + 更新）和主机的 `prod.keys`，
> 在你自己的机器上构建出你自己的副本。不要分发构建产物。

## 现状（2026-11-09 06:20）

| 阶段 | 内容 | 状态 |
|---|---|---|
| P0 | 输入核对、本体 ExeFS/RomFS 提取、更新合并 | ✅ 见 [docs/00-inputs.md](docs/00-inputs.md) |
| P1 | 四个模块（main/subsdk0/sdk/rtld）全量抬升成 C（72,009 函数 / 216 MB） | ✅ 见 [docs/01-engine.md](docs/01-engine.md) |
| P2 | 运行时：内核/线程、fs、vi、audren、NVN 设备，60 fps 稳定 | ✅ 见 [STATUS.md](STATUS.md) |
| P3 | NMPL 引擎初始化：输入、音频、movie（H.264/AAC 暂由 stub 跳过） | ✅ 部分 |
| P4 | 进 FOAF1（第 1 部）：标题画面 → 标题选择 → 正篇旁白 | ✅ 部分 |

**能跑到哪**：标题画面与官方 key art 逐像素一致 → 按键进标题选择（三作封面竖排）→ 第 1 部正篇开场旁白，
300 秒 17,997 帧、mean 60.0 fps、1% low 58.8 fps、无 FATAL，audren 混音出声。

**还没通**：影片（H.264/AAC）真解码、标题菜单叠了两套 UI、存档读写。详细进度、构建命令、
按键表与已知问题都在 [STATUS.md](STATUS.md)。

## 这是什么游戏

Nippon Ichi Software 的 `NMPL`（Nippon Multi Platform Library）引擎，rev 1475 的 hayarigami 定制分支。
2D 恐怖文字冒险：预渲染背景（graphics_bg.dat）+ 立绘（graphics_ci.dat）+ 音声 + 全屏 mp4 影片，
图形只用最基本的 NVN 四边形/精灵管线。合集把三部作品放在 RomFS 的 `FOAF1`、`FOAF2`、`FOAF3` 三个目录里。

## 目录

```
build/extracted/v0/          本体（1.0.0）的 ExeFS 与 RomFS
build/extracted/latest/      本体 + 更新合并后的可构建输入（exefs/ romfs/）
data/expected-latest.json    合并树的逐文件 hash 清单（回归基准）
data/imports.json            main/subsdk0 的 892 个导入符号（HLE 工作面）
tools/                       提取与合并脚本（Python）
docs/                        输入、引擎、路线图
```

## 从零复现输入

需要：Python 3.14（`compression.zstd`）、`cryptography`、自己的 `prod.keys`。

```bash
uv venv .venv314 --python 3.14
uv pip install --python .venv314/Scripts/python.exe cryptography
.venv314/Scripts/python.exe tools/extract_exefs.py <本体.xci> --keys <prod.keys> --output build/extracted/v0/exefs
.venv314/Scripts/python.exe tools/extract_romfs.py --keys <prod.keys> \
    --manifest build/extracted/v0/extraction-manifest.json --output build/extracted/v0/romfs
.venv314/Scripts/python.exe tools/unpack_romfs.py --romfs build/extracted/v0/romfs \
    --out build/extracted/v0/romfs-tree --verify
.venv314/Scripts/python.exe tools/merge_tree.py --base build/extracted/v0/romfs-tree \
    --update <更新 RomFS 目录> --out build/extracted/latest \
    --base-exefs build/extracted/v0/exefs --update-exefs <更新 ExeFS 目录> \
    --manifest data/expected-latest.json
```

## 致谢

抬升器与运行时来自 [XC2 Recomp](https://github.com/AksharDP/xc2-recomp) 一系（MIT；原始血统
LAS Recomp → TotK Recomp → XCX Recomp → XC2 Recomp），提取器来自 MacNativeGames（MIT）。
