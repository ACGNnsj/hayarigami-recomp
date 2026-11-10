cd D:/consoles/ns/hayarigami-recomp
$env:PATH = 'C:\msys64\ucrt64\bin;' + $env:PATH
$env:XC2_ROMFS = 'D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs'
$env:XC2_INPUT_FORCE = '1'
Add-Type -Namespace W9 -Name K2 -MemberDefinition @'
[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, System.UIntPtr dwExtraInfo);
'@
function Foreground-Haya {
  try {
    $p = Get-Process haya -ErrorAction Stop | Select-Object -First 1
    $ws = New-Object -ComObject WScript.Shell
    return $ws.AppActivate($p.Id)
  } catch { Write-Output 'focus: no haya process'; return $false }
}
function TapE($label) {
  Foreground-Haya | Out-Null
  Start-Sleep -Milliseconds 400
  [W9.K2]::keybd_event([byte]0x45, 0, 0, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 150
  [W9.K2]::keybd_event([byte]0x45, 0, 2, [System.UIntPtr]::Zero)
  Write-Output ("tap E [{0}] at {1}s" -f $label, [int]((Get-Date) - $t0).TotalSeconds)
}
function Shot($name) {
  Foreground-Haya | Out-Null
  Start-Sleep -Milliseconds 500
  & ./tools/_shot_screen.ps1 ("build/v0/{0}" -f $name)
}
function ErrHas($pat) { return (Select-String $pat build/v0/saverun.log.err -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0 }
function EosCount { return (Select-String 'movie: end of stream' build/v0/saverun.log.err -ErrorAction SilentlyContinue | Measure-Object).Count }
Get-Process haya -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
Remove-Item build/v0/saverun.log -ErrorAction SilentlyContinue
Remove-Item build/v0/saverun.log.err -ErrorAction SilentlyContinue
$p = Start-Process ./build/v0/haya.exe -ArgumentList '--seconds','3600','--shot','build/v0/saverun_shot.png' -PassThru -RedirectStandardOutput build/v0/saverun.log -RedirectStandardError build/v0/saverun.log.err
$t0 = Get-Date
Write-Output ("game pid={0}" -f $p.Id)
function WaitUntil($sec) {
  $wait = $sec - ((Get-Date) - $t0).TotalSeconds
  if ($wait -gt 0) { Start-Sleep -Milliseconds ([int]($wait * 1000)) }
}
WaitUntil 95
Shot 'save_pre.png'
foreach ($t in @(100, 110, 150, 160, 210)) {
  WaitUntil $t
  if ($p.HasExited) { Write-Output 'game exited early'; break }
  if (ErrHas 'movie: head of') { Write-Output 'landed, stop tapping'; break }
  TapE ("w-$t")
  if ($t -eq 110 -or $t -eq 160) { Shot ("save_{0}.png" -f $t) }
}
Write-Output ("landed={0}" -f (ErrHas 'movie: head of'))
while (((Get-Date) - $t0).TotalSeconds -lt 1500) {
  if ($p.HasExited) { Write-Output 'game exited during wait'; break }
  if ((EosCount) -ge 4) { Write-Output 'EOS groups seen, waiting 45s for game to settle'; Start-Sleep -Seconds 45; break }
  Start-Sleep -Seconds 15
}
if (-not $p.HasExited) { Shot 'save_ready.png'; Write-Output 'READY for manual play; job keeps process alive' }
while (-not $p.HasExited) { Start-Sleep -Seconds 60 }
Write-Output ("haya exited, job done")
