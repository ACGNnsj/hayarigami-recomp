#!/bin/bash
# Isolate the layers of the game-1 title menu (frame ~3000): _iso2.sh
cd /d/consoles/ns/hayarigami-recomp || exit 1
for r in 1:5 6:10 11:15; do
  n=$(echo $r | tr ':' '_')
  XC2_DRAW_ONLY=$r bash tools/_one.sh 50 "build/v0/layer_$n.png" '9:0x45,13:0x45'
done
echo ISODONE
