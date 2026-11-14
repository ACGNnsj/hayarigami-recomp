#!/bin/bash
# Compare the same launcher menu at two moments: static screen or an animation caught mid-way?
cd /d/consoles/ns/hayarigami-recomp || exit 1
HAYA_DUMP=2600 HAYA_DUMP_DIR=build/v0/dump_m45 bash tools/_one.sh 45 build/v0/shot_m45.png '9:0x45,13:0x45'
HAYA_DUMP=4400 HAYA_DUMP_DIR=build/v0/dump_m75 bash tools/_one.sh 75 build/v0/shot_m75.png '9:0x45,13:0x45'
echo ALDONE
