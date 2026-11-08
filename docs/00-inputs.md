# 00 输入：本体、更新、提取与合并

> 全部数字都是 2026-11-09 在本机实测得到的，不是抄来的。路径相对 `D:\consoles`。

## 1. 输入文件

| 项 | 值 |
|---|---|
| 本体 | `ns/hr-bcjna.xci` — 7,985,954,816 B（2025-07-27） |
| 本体 SHA-256 | `ade5e4395295e433a468687565f91c7754c9a565e585a77013de087167275dfa`（8 GB 文件实测，约 1 分钟） |
| 标题 ID | `010095B01AF94000`（本体 Program NCA `79b44173f492ffb1ce628d9c59bc8cd7.nca`，4,393,074,688 B @ 385,974,784） |
| 更新 | `ns/010095B01AF94000/` — `ExeFs/main`（2,248,368 B）+ `RomFs/`（12 个文件，3,035,427,385 B） |
| keys | `D:\ProdKeys.net-v20.3.0\prod.keys`（v20.3.0 键表；**不进仓库**） |

更新目录名沿用了本体标题 ID（Switch 更新时间包里的 Program NCA 经常保留本体 ID），这不影响提取。

## 2. 本体 ExeFS（`build/extracted/v0/exefs`）

| 模块 | 字节数 | SHA-256 前 16 位 | 说明 |
|---|---:|---|---|
| main | 2,249,333 | `fea8ad41b63c1274` | 游戏主程序（NSO0） |
| sdk | 6,025,528 | `6022d3c89f56ada7` | 任天堂 SDK 静态库 |
| subsdk0 | 3,385,994 | `ad5b29eeefdf4ab0` | **引擎**（NMPL）+ audout 等 |
| rtld | 7,207 | `a3b723feeb3766bb` | 模块加载器 |
| main.npdm | 1,572 | `5391e46d196fa61f` | 权限描述 |

提取器：`tools/extract_exefs.py`（改自 MacNativeGames 的 vendored 提取器，把写死的 XC2 标题 ID 改成
`BASE_TITLE` + `--title-id`）。提取时校验了 NCA 头、FS header 哈希与 PFS0/HFS0 层次结构。

## 3. 本体 RomFS（`build/extracted/v0/romfs`）

- `romfs.bin` 4,372,612,184 B，SHA-256 `c675f6a75cc60ccb450569cae339bf489786f2c56352552f462c79b81cb4bca0`
- IVFC 六级全部逐块校验通过（level 0–3 各 1–2 块，level 4 522 块，level 5 266,884 块）；RSA 签名未校验
- 30 个文件，展开后 4,372,609,872 B（`tools/unpack_romfs.py --verify` 按 index 逐文件 size 校验）

文件结构（30 个，全部列在 `data/expected-latest.json`）：`FOAF1/`、`FOAF2/`、`FOAF3/` 三个部，
每部 `database.dat`、`start.dat`、`graphics_bg.dat`、`graphics_ci.dat`、`sound/sound_bgm.dat`、
`sound/sound_se.dat`（FOAF3 只有前两个音轨文件）、`movie.mp4`（FOAF1 另有 `ed1.mp4`/`ed2.mp4`，
FOAF3 另有 `1.mp4`/`2.mp4`/`5.mp4`），根部 `database.dat`、`package_tex.dat`、`sound/sound_bgm.dat`、
`sound/sound_se.dat`。

## 4. 合并树（`build/extracted/latest`，可构建输入）

本体 ExeFS + 更新 `main` 覆盖；本体 RomFS 树 + 更新 12 个文件覆盖。

| 项 | 值 |
|---|---|
| 合并后 RomFS | **30 个文件，4,423,579,523 B**（比本体多 50,969,651 B） |
| 更新覆盖的文件 | 12 个，合计 3,035,427,385 B（详见下表） |
| 合并后 main | 2,248,368 B，SHA-256 `2b6f3473c1b4f7fdfa68cbad2262ac14fcec6731911e1f80ba3345199fe6118b` |
| 逐文件清单 | `data/expected-latest.json`（path / size / sha256 / from: base\|update） |

更新覆盖清单（`from: update` 的 12 个）：

| 文件 | 更新后大小 | 本体大小 |
|---|---:|---:|
| FOAF1/graphics_bg.dat | 400,972,235 | 401,396,224 |
| FOAF1/graphics_ci.dat | 332,777,923 | 336,550,400 |
| FOAF1/movie.mp4 | 179,067,152 | 177,130,593 |
| FOAF1/sound/sound_bgm.dat | 204,508,056 | 155,753,984 |
| FOAF1/start.dat | 28,966,896 | 28,058,624 |
| FOAF2/graphics_bg.dat | 682,131,222 | 682,249,216 |
| FOAF2/graphics_ci.dat | 315,648,247 | 318,146,048 |
| FOAF2/movie.mp4 | 195,835,972 | 189,630,373 |
| FOAF2/start.dat | 120,776,252 | 119,468,544 |
| FOAF3/graphics_bg.dat | 422,903,747 | 422,910,464 |
| FOAF3/start.dat | 146,765,491 | 148,003,840 |
| package_tex.dat | 5,074,192 | 5,159,424 |

**注意**：更新 RomFS 是按“完整文件”覆盖的（每个文件都是完整大小，不是 BKTR 差分块）。这份更新目录是
别人已经解开的文件树，不是原始 NSP 内的 BKTR NCA；因此合并是逐文件覆盖，不涉及 `tools/xc2_merge_romfs.py`
那套 BKTR/AES-CTR-EX 直读逻辑。若以后要核对“官方更新合并后的 RomFS 哈希”，需要用原版 NSP 的 BKTR 路径另算，
两者不一定逐字节相等（补齐块、对齐不同）。

## 5. 复现

```bash
cd ns/hayarigami-recomp
uv venv .venv314 --python 3.14
uv pip install --python .venv314/Scripts/python.exe cryptography
.venv314/Scripts/python.exe tools/extract_exefs.py ../../ns/hr-bcjna.xci \
    --keys D:/ProdKeys.net-v20.3.0/prod.keys --output build/extracted/v0/exefs
.venv314/Scripts/python.exe tools/extract_romfs.py --keys D:/ProdKeys.net-v20.3.0/prod.keys \
    --manifest build/extracted/v0/extraction-manifest.json --output build/extracted/v0/romfs
.venv314/Scripts/python.exe tools/unpack_romfs.py --romfs build/extracted/v0/romfs \
    --out build/extracted/v0/romfs-tree --verify
.venv314/Scripts/python.exe tools/merge_tree.py --base build/extracted/v0/romfs-tree \
    --update ../../ns/010095B01AF94000/RomFs --out build/extracted/latest \
    --base-exefs build/extracted/v0/exefs --update-exefs ../../ns/010095B01AF94000/ExeFs \
    --manifest data/expected-latest.json
```

磁盘占用：`build/` 约 13 GB（romfs.bin 4.37 + romfs-tree 4.37 + latest 4.42）。
