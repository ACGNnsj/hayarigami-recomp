$env:XC2_ROMFS = 'D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs'
$env:XC2_INPUT_FORCE = '1'
$exe = 'D:\consoles\ns\hayarigami-recomp\build\v0\haya.exe'
$arg = '--seconds 240 --shot build/v0/wmi_shot.png'
$cmd = '"' + $exe + '" ' + $arg
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = 'D:\consoles\ns\hayarigami-recomp' }
Write-Output ('wmi pid=' + $r.ProcessId + ' rc=' + $r.ReturnValue)