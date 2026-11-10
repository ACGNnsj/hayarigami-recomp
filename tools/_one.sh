#!/bin/bash
# One run with a tap sequence: _one.sh <seconds> <shot.png> <tap sequence> [env assignments...]
cd /d/consoles/ns/hayarigami-recomp || exit 1
SECS=$1; SHOT=$2; TAPS=$3; shift 3
if [ $# -gt 0 ]; then export "$@"; fi
bash tools/_run.sh "$SECS" "$SHOT" >/dev/null 2>&1 &
RP=$!
if [ -n "$TAPS" ]; then { command -v pwsh >/dev/null && PSBIN=pwsh || PSBIN=powershell; }; $PSBIN -NoProfile -File tools/_tap_seq.ps1 "$TAPS" >/dev/null 2>&1; fi
wait $RP
echo "EXIT=$? shot=$SHOT"
