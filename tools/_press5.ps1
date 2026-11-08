$ErrorActionPreference='Stop'
$env:PATH='C:\msys64\ucrt64\bin;'+$env:PATH
$env:XC2_ROMFS='D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs'
$env:XC2_INPUT_FORCE='1'
$dir='D:/consoles/ns/hayarigami-recomp'
Add-Type -Namespace W3 -Name K -MemberDefinition @'
[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, System.UIntPtr dwExtraInfo);
'@
$p = Start-Process -FilePath "$dir/build/v0/haya.exe" -ArgumentList '--seconds','60','--shot',"$dir/build/v0/shot_load60.png" -PassThru -RedirectStandardOutput "$dir/build/v0/run60.log" -RedirectStandardError "$dir/build/v0/run60.err"
Start-Sleep -Seconds 10
function Tap([int]$vk) {
  [W3.K]::keybd_event([byte]$vk, 0, 0, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 150
  [W3.K]::keybd_event([byte]$vk, 0, 2, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 800
}
Tap 0x45
Start-Sleep -Seconds 15
Tap 0x45
$p.WaitForExit()
Write-Host "exit $($p.ExitCode)"
