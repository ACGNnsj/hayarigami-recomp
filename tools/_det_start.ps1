$env:PATH = 'C:\msys64\ucrt64\bin;' + $env:PATH
$env:XC2_ROMFS = 'D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs'
$env:XC2_INPUT_FORCE = '1'
Start-Process -FilePath 'D:\consoles\ns\hayarigami-recomp\build\v0\haya.exe' -ArgumentList '--seconds','300','--shot','build/v0/det_shot.png' -RedirectStandardOutput 'D:\consoles\ns\hayarigami-recomp\build\v0\run.log' -RedirectStandardError 'D:\consoles\ns\hayarigami-recomp\build\v0\run.err' -WorkingDirectory 'D:\consoles\ns\hayarigami-recomp'
Write-Output 'started'
