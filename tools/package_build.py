#!/usr/bin/env python3
"""Assemble a portable release package for Hayarigami 1+2+3 (haya123).

Layout of dist/<name>/ (everything the game resolves next to haya.exe):
  haya.exe, SDL3.dll, libopus-0.dll, libiconv-2.dll,
  Streamline + DLSS/Reflex/FG DLLs (+ nvngx_dlssnr.dll when staged),
  haya_xlate.exe + haya_xlate.id (shader translator service),
  haya.ini (defaults), romfs/ + exefs/ (empty, user provides dump),
  profile/, shader-cache/ (created at runtime), README.txt, RUN.bat.

Usage: python3 tools/package_build.py [--out dist] [--name NAME] [--zip/--no-zip]
       [--with-romfs DIR]   # bundle your own romfs (large; personal archiving only)
"""
import argparse, datetime, os, shutil, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'build')
V0 = os.path.join(BUILD, 'v0')
SL_BIN = os.path.join(BUILD, 'sl-dl', 'sdk', 'bin', 'x64')
XLATE = os.path.join(BUILD, 'xlate')

DLLS_REQUIRED = ['SDL3.dll', 'libopus-0.dll', 'libiconv-2.dll']
DLLS_SL = ['sl.interposer.dll', 'sl.dlss.dll', 'sl.common.dll', 'nvngx_dlss.dll',
           'sl.reflex.dll', 'sl.dlss_g.dll', 'nvngx_dlssg.dll', 'NvLowLatencyVk.dll']
DLLS_OPTIONAL = ['nvngx_dlssnr.dll']  # community Phase-3 NR DLL, manually staged

DEFAULT_INI = """# Hayarigami 1+2+3 default settings. Lines are `key = value`;
# lines starting with # or ; are comments. The game also reads
# HAYA_* environment variables, which override this file.
[display]
# 0 = windowed, 1 = fullscreen (F11 toggles at runtime)
fullscreen = 0
# window size in pixels, e.g. window_size = 1920x1080
#window_size = 1920x1080
[upscaler]
# fsr | bilinear | dlss (dlss needs an NVIDIA RTX GPU)
#upscaler = dlss
# off | dlaa | quality | balanced | performance | ultraperformance
#dlss_mode = quality
"""

README = """Hayarigami 1+2+3 (PC recomp) - portable release
=============================================
1. Place your game dump: copy romfs.bin into the romfs/ folder
   (or point HAYA_ROMFS at your extracted romfs directory).
2. Run haya.exe (or RUN.bat). First boot builds pipelines and may
   take a minute; progress is logged to logs/.
3. Settings live in haya.ini next to haya.exe; HAYA_* env vars
   override it. Press F11 for fullscreen.

Notes:
- DLSS upscaling requires an NVIDIA RTX GPU and works out of the
  box (DLLs bundled). Non-NVIDIA GPUs fall back to FSR.
- nvngx_dlssnr.dll (Neural Rendering, optional) is bundled when
  present; otherwise DLSS_NR stays off.
- exefs/ holds the extracted ExeFS (main, main.npdm, rtld, sdk,
  subsdk0) if your dump ships it; not required when romfs.bin
  is present.
"""

RUN_BAT = '@echo off\r\ncd /d "%~dp0"\r\nstart "" "%~dp0haya.exe" %*\r\n'
ROMFS_README = 'Put your romfs.bin here (or set HAYA_ROMFS to your extracted romfs folder).\n'
EXEFS_README = 'Optional: extracted ExeFS (main, main.npdm, rtld, sdk, subsdk0) goes here.\n'


def cp(src, dst):
    shutil.copy2(src, dst)
    print(' ', os.path.basename(src))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'dist'))
    ap.add_argument('--name', default='hayarigami-123-win64')
    ap.add_argument('--zip', dest='zip', action='store_true', default=True)
    ap.add_argument('--no-zip', dest='zip', action='store_false')
    ap.add_argument('--with-romfs', default=None,
                    help='bundle a romfs dir (personal archiving only; large)')
    a = ap.parse_args()
    pkg = os.path.join(a.out, a.name)
    if os.path.isdir(pkg):
        shutil.rmtree(pkg)
    os.makedirs(pkg)
    missing = []
    exe = os.path.join(V0, 'haya.exe')
    if not os.path.isfile(exe):
        sys.exit('missing build output: run tools/build_haya.sh first')
    cp(exe, pkg)
    for n in DLLS_REQUIRED:
        p = os.path.join(V0, n)
        if os.path.isfile(p):
            cp(p, pkg)
        else:
            missing.append(n)
    for n in DLLS_SL:
        for d in (V0, SL_BIN):
            p = os.path.join(d, n)
            if os.path.isfile(p):
                cp(p, os.path.join(pkg, n))
                break
        else:
            missing.append(n)
    for n in DLLS_OPTIONAL:
        p = os.path.join(V0, n)
        if os.path.isfile(p):
            cp(p, pkg)
    for n in ('haya_xlate.exe', 'haya_xlate.id'):
        p = os.path.join(XLATE, n)
        if os.path.isfile(p):
            cp(p, pkg)
        else:
            missing.append('xlate/' + n)
    with open(os.path.join(pkg, 'haya.ini'), 'w', newline='\n') as f:
        f.write(DEFAULT_INI)
    print('  haya.ini')
    for d in ('romfs', 'exefs', 'profile', 'shader-cache', 'logs', 'mods'):
        os.makedirs(os.path.join(pkg, d), exist_ok=True)
    with open(os.path.join(pkg, 'romfs', 'README.txt'), 'w') as f:
        f.write(ROMFS_README)
    with open(os.path.join(pkg, 'exefs', 'README.txt'), 'w') as f:
        f.write(EXEFS_README)
    with open(os.path.join(pkg, 'README.txt'), 'w', newline='\n') as f:
        f.write(README)
    with open(os.path.join(pkg, 'RUN.bat'), 'w', newline='') as f:
        f.write(RUN_BAT)
    print('  README.txt, RUN.bat')
    if a.with_romfs:
        src = a.with_romfs
        dst = os.path.join(pkg, 'romfs')
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dst, 'romfs.bin'))
        elif os.path.isdir(src):
            for e in os.listdir(src):
                s = os.path.join(src, e)
                if os.path.isfile(s):
                    shutil.copy2(s, os.path.join(dst, e))
        print('  bundled romfs from', src)
    if missing:
        print('WARNING, missing files (package still runs without some):')
        for n in missing:
            print('  !', n)
    else:
        print('all runtime files present')
    zp = pkg + '.zip'
    if a.zip:
        if os.path.isfile(zp):
            os.remove(zp)
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for dp, _, fns in os.walk(pkg):
                for fn in sorted(fns):
                    fp = os.path.join(dp, fn)
                    z.write(fp, os.path.relpath(fp, a.out))
        print('wrote', zp, round(os.path.getsize(zp) / 1e6, 1), 'MB')
    print('package dir:', pkg)


if __name__ == '__main__':
    main()
