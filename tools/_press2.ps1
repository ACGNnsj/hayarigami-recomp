$ErrorActionPreference='Stop'
$env:PATH='C:\msys64\ucrt64\bin;'+$env:PATH
$env:XC2_ROMFS='D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs'
$dir='D:/consoles/ns/hayarigami-recomp'
$p = Start-Process -FilePath "$dir/build/v0/haya.exe" -ArgumentList '--seconds','22','--shot',"$dir/build/v0/shot_menu.png" -PassThru -NoNewWindow
Start-Sleep -Seconds 9
Add-Type -Namespace W -Name K -MemberDefinition @'
[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, System.UIntPtr dwExtraInfo);
'@
function Tap([int]$vk) {
  [W.K]::keybd_event([byte]$vk, 0, 0, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 120
  [W.K]::keybd_event([byte]$vk, 0, 2, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 400
}
Write-Host "sending Enter"
Tap 0x0D
Start-Sleep -Seconds 2
Tap 0x0D
Start-Sleep -Seconds 2
Tap 0x20
$p.WaitForExit()
Write-Host "exit $($p.ExitCode)"
