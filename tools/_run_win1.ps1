cd D:/consoles/ns/hayarigami-recomp
Add-Type -Namespace W9 -Name KX -MemberDefinition '[DllImport("user32.dll")] public static extern bool PostMessage(System.IntPtr h, uint m, System.IntPtr w, System.IntPtr l); [DllImport("user32.dll")] public static extern uint MapVirtualKey(uint c, uint t);'
function TapWin([System.IntPtr]$h, [int]$vk) {
  $scc = [W9.KX]::MapVirtualKey([uint32]$vk, 0)
  $dn = 1 -bor ($scc -shl 16)
  $up = (1 -bor ($scc -shl 16)) -bor (3 -shl 30)
  [W9.KX]::PostMessage($h, 0x0100, [System.IntPtr]$vk, [System.IntPtr]$dn) | Out-Null
  Start-Sleep -Milliseconds 150
  [W9.KX]::PostMessage($h, 0x0101, [System.IntPtr]$vk, [System.IntPtr]$up) | Out-Null
}
Get-Process haya -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 1
$log = 'build/v0/run_win1.log'
Remove-Item $log -ErrorAction SilentlyContinue
Remove-Item ($log + '.err') -ErrorAction SilentlyContinue
$p = Start-Process ./build/v0/haya.exe -ArgumentList '--seconds','75','--shot','build/v0/test_win.png' -PassThru -RedirectStandardOutput $log
Write-Output ("game pid={0}" -f $p.Id)
foreach ($t in @(12, 22, 32, 42, 52)) {
  $wait = $t - ((Get-Date) - $p.StartTime).TotalSeconds
  if ($wait -gt 0) { Start-Sleep -Milliseconds ([int]($wait * 1000)) }
  if ($p.HasExited) { Write-Output 'game exited early'; break }
  $p.Refresh(); $h = $p.MainWindowHandle
  Write-Output ("tap E at {0}s hwnd={1}" -f $t, $h)
  if ($h -ne 0) { TapWin $h 0x45 } else { Write-Output 'no hwnd yet' }
}
$p.WaitForExit(90000) | Out-Null
Write-Output ("exited={0} code={1}" -f $p.HasExited, $p.ExitCode)
ls build/v0/test_win.png 2>&1 | Select-Object Name, Length
Select-String 'boot: frames|boot: passed|FATAL|movie:' $log | Select-Object -Last 6