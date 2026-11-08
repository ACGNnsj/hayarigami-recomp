#!/bin/bash
cd /d/consoles/ns/hayarigami-recomp || exit 1
bash tools/_one.sh 100 build/v0/shot_menu100.png '9:0x45,13:0x45'
cp build/v0/run.log build/v0/run_menu100.log
bash tools/_one.sh 60 build/v0/shot_iso2.png '9:0x45,13:0x45' XC2_DRAW_ONLY=2:15
cp build/v0/run.log build/v0/run_iso2.log
sha256sum build/v0/shot_menu100.png build/v0/shot_iso2.png
echo TESTDONE
