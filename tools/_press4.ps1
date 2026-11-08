$ErrorActionPreference='Stop'
$env:PATH='C:\msys64\ucrt64\bin;'+$env:PATH
$env:XC2_ROMFS='D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs'
$env:XC2_INPUT_FORCE='1'
$dir='D:/consoles/ns/hayarigami-recomp'
Add-Type -Namespace W2 -Name K -MemberDefinition @'
[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, System.UIntPtr dwExtraInfo);
'@
$p = Start-Process -FilePath "$dir/build/v0/haya.exe" -ArgumentList '--seconds','24','--shot',"$dir/build/v0/shot_menu3.png" -PassThru
Start-Sleep -Seconds 9
function Tap([int]$vk,[string]$name) {
  Write-Host "tap $name"
  [W2.K]::keybd_event([byte]$vk, 0, 0, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 150
  [W2.K]::keybd_event([byte]$vk, 0, 2, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 800
}
Tap 0x45 'E=pad A'
Start-Sleep -Seconds 2
Tap 0x45 'E'
Start-Sleep -Seconds 3
Write-Host "still running: $(-not $p.HasExited)"
$p.WaitForExit()
Write-Host "exit $($p.ExitCode)"
