cd D:/consoles/ns/hayarigami-recomp
$env:PATH = 'C:\msys64\ucrt64\bin;' + $env:PATH
$env:XC2_ROMFS = 'D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs'
$env:XC2_INPUT_FORCE = '1'
$env:XC2_UPSCALER = 'dlss'
$env:XC2_DLSS_MODE = 'dlaa'
$env:XC2_DLSS_G = 'on'
$env:XC2_REFLEX = 'on'
$env:SystemDrive = 'C:'
$env:SystemRoot = 'C:/Windows'
$env:windir = 'C:/Windows'
$env:PROGRAMDATA = 'C:/ProgramData'
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class W9K2 { [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, UIntPtr dwExtraInfo); }'
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class FG2W { [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n); [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h); }'
function Foreground-Haya {
  try {
    $p = Get-Process haya -ErrorAction Stop | Select-Object -First 1
    [FG2W]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
    [FG2W]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
    return $true
  } catch { return $false }
}
Get-Process haya -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
Remove-Item build/v0/fg_route.log -ErrorAction SilentlyContinue
Remove-Item build/v0/fg_route.log.err -ErrorAction SilentlyContinue
$p = Start-Process ./build/v0/haya.exe -ArgumentList '--seconds','330' -PassThru -RedirectStandardOutput build/v0/fg_route.log -RedirectStandardError build/v0/fg_route.log.err
$t0 = Get-Date
Write-Output ("game pid={0}" -f $p.Id)
function WaitUntil($sec) { $w = $sec - ((Get-Date) - $t0).TotalSeconds; if ($w -gt 0) { Start-Sleep -Milliseconds ([int]($w * 1000)) } }
foreach ($t in @(100, 110)) {
  WaitUntil $t; if ($p.HasExited) { break }
  Foreground-Haya | Out-Null; Start-Sleep -Milliseconds 400
  [W9K2]::keybd_event([byte]0x45, 0, 0, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 150
  [W9K2]::keybd_event([byte]0x45, 0, 2, [System.UIntPtr]::Zero)
  Write-Output ("tap E at {0}s" -f $t)
}
WaitUntil 320
if (-not $p.HasExited) { Foreground-Haya | Out-Null; Start-Sleep -Milliseconds 500; & ./tools/_shot_screen.ps1 'build/v0/fg_route_shot.png' }
WaitUntil 330
if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force; Write-Output 'killed at 330s' } else { Write-Output 'exited on its own' }
