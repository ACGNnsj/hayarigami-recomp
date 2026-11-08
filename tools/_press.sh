cd /d/consoles/ns/hayarigami-recomp
export PATH=/c/msys64/ucrt64/bin:$PATH XC2_ROMFS=D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs
./build/v0/haya.exe --seconds 30 --shot build/v0/shot3.png > build/v0/run22.log 2>&1 &
PID=$!
sleep 9
powershell.exe -NoProfile -Command "\$p = Get-Process haya -ErrorAction SilentlyContinue | Select-Object -First 1; if (\$p) { \$w = New-Object -ComObject WScript.Shell; [void]\$w.AppActivate(\$p.Id); Start-Sleep -Milliseconds 800; \$w.SendKeys('{ENTER}'); Start-Sleep -Milliseconds 400; \$w.SendKeys(' '); Write-Output ('sent to ' + \$p.Id) } else { Write-Output 'no process' }"
sleep 3
powershell.exe -NoProfile -Command "\$p = Get-Process haya -ErrorAction SilentlyContinue | Select-Object -First 1; if (\$p) { \$w = New-Object -ComObject WScript.Shell; [void]\$w.AppActivate(\$p.Id); Start-Sleep -Milliseconds 500; \$w.SendKeys('{ENTER}') }"
wait $PID
echo exit=$?
ls -la build/v0/shot3.png