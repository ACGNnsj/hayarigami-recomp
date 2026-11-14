#!/bin/bash
# Isolate layers of the launcher menu: render only draws <first>:<last> of each frame and screenshot the result.
cd /d/consoles/ns/hayarigami-recomp || exit 1
run_one() {
  local only=$1 name=$2
  HAYA_DRAW_ONLY=$only bash tools/_run.sh 24 "build/v0/iso_$name.png" >/dev/null 2>&1 &
  local rp=$!
  pwsh -NoProfile -File tools/_tap_seq.ps1 '9:0x45' >/dev/null 2>&1
  wait $rp
  echo "done $name ($only)"
}
run_one 1:5 a
run_one 6:10 b
run_one 11:15 c
