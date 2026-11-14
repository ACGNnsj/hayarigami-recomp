export PATH=/c/msys64/ucrt64/bin:$PATH
export HAYA_ROMFS=D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs HAYA_INPUT_FORCE=1
rm -f build/v0/run.log build/v0/run.err build/v0/av3_taps.log
./build/v0/haya.exe --seconds 640 --shot build/v0/av3_shot.png > build/v0/run.log 2> build/v0/run.err & HPID=$!
echo $HPID > build/v0/av3.pid
sleep 15
powershell.exe -NoProfile -File tools/_tap_seq.ps1 "100:0x45,140:0x45,180:0x45,220:0x45,260:0x45,300:0x45,340:0x45,380:0x45,420:0x45,460:0x45,500:0x45,540:0x45,580:0x45" > build/v0/av3_taps.log 2>&1
wait $HPID
echo "EXIT:$?" >> build/v0/av3_taps.log
