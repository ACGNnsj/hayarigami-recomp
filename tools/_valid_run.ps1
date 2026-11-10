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
    if (-not $ws.AppActivate($p.Id)) { Write-Output 'focus: AppActivate refused'; return $false }
    return $true
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
function MovieSeen { return (Select-String 'movie: head of' build/v0/valid_run.log -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0 }
function EosCount { return (Select-String 'movie: end of stream' build/v0/valid_run.log -ErrorAction SilentlyContinue | Measure-Object).Count }
Get-Process haya -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
Remove-Item build/v0/valid_run.log -ErrorAction SilentlyContinue
Remove-Item build/v0/valid_run.log.err -ErrorAction SilentlyContinue
$p = Start-Process ./build/v0/haya.exe -ArgumentList '--seconds','600','--shot','build/v0/valid_shot.png' -PassThru -RedirectStandardOutput build/v0/valid_run.log -RedirectStandardError build/v0/valid_run.log.err
$t0 = Get-Date
Write-Output ("game pid={0}" -f $p.Id)
function WaitUntil($sec) {
  $wait = $sec - ((Get-Date) - $t0).TotalSeconds
  if ($wait -gt 0) { Start-Sleep -Milliseconds ([int]($wait * 1000)) }
}
# pre-tap state
WaitUntil 95
Shot 'valid_pre.png'
# paired taps + adaptive stop
$landed = $false
foreach ($t in @(100, 110)) { WaitUntil $t; if ($p.HasExited) { break }; if (MovieSeen) { $landed = $true; break }; TapE ("w1-$t") }
WaitUntil 135
if (MovieSeen) { $landed = $true } else { Shot 'valid_135.png' }
if (-not $landed) {
  foreach ($t in @(150, 160)) { WaitUntil $t; if ($p.HasExited) { break }; if (MovieSeen) { $landed = $true; break }; TapE ("w2-$t") }
  WaitUntil 185
  if (MovieSeen) { $landed = $true } else { Shot 'valid_185.png' }
}
if (-not $landed) {
  WaitUntil 210
  if (-not $p.HasExited) { TapE 'last-210'; Shot 'valid_215.png' }
}
Write-Output ("landed(movie seen)={0}" -f (MovieSeen))
# wait for EOS x2 (or timeout): poll every 10s up to 540s
$eosShot1 = $false
while (((Get-Date) - $t0).TotalSeconds -lt 540) {
  if ($p.HasExited) { Write-Output 'game exited during wait'; break }
  $n = EosCount
  if ($n -ge 1 -and -not $eosShot1) { Start-Sleep -Seconds 15; Shot 'valid_eos.png'; $eosShot1 = $true; Write-Output 'eos screenshot taken' }
  if ($n -ge 2) { Write-Output 'EOS x2 seen'; break }
  Start-Sleep -Seconds 10
}
Write-Output ("eos count={0}" -f (EosCount))
if (-not $p.HasExited) { Shot 'valid_post1.png' }
Start-Sleep -Seconds 60
if (-not $p.HasExited) {
  Shot 'valid_post2.png'
  $n1 = (Get-Item build/v0/valid_run.log).Length; Start-Sleep -Seconds 20
  $n2 = (Get-Item build/v0/valid_run.log).Length
  Write-Output ("log growing={0} (+{1}B/20s)" -f ($n2 -gt $n1), ($n2 - $n1))
}
$p.WaitForExit(120000) | Out-Null
Write-Output ("exited={0} code={1}" -f $p.HasExited, $(if ($p.HasExited) { $p.ExitCode } else { 'n/a' }))
if (-not $p.HasExited) { Shot 'valid_end.png'; $p | Stop-Process -Force }
Write-Output '--- markers ---'
Select-String 'movie: end of stream|movie: stop after|AAC total PCM|EOS drained|movie: stop signal|FATAL|boot: passed' build/v0/valid_run.log | Select-Object -Last 15
