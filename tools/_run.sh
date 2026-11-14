#!/bin/bash
# One instrumented run: env for the forced-input test path, a progress log and the console log.
cd /d/consoles/ns/hayarigami-recomp || exit 1
export PATH=/c/msys64/ucrt64/bin:$PATH
export HAYA_ROMFS=D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs
export HAYA_INPUT_FORCE=1
export HAYA_FS_PROGRESS=1
rm -f fs_progress.log
SECS=${1:-90}
SHOT=${2:-build/v0/shot_run.png}
./build/v0/haya.exe --seconds "$SECS" --shot "$SHOT" > build/v0/run.log 2>&1
echo "EXIT=$?"
