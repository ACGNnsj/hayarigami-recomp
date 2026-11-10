Add-Type -Namespace W9 -Name K3 -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool PostMessage(System.IntPtr hWnd, uint Msg, System.IntPtr wParam, System.IntPtr lParam);
[DllImport("user32.dll")] public static extern uint MapVirtualKey(uint uCode, uint uMapType);
'@
function TapWin([System.IntPtr]$hwnd, [int]$vk) {
  $sc = [W9.K3]::MapVirtualKey([uint32]$vk, 0)
  $dn = ([int]1) -bor ([int]$sc -shl 16)
  $up = ([int]1) -bor ([int]$sc -shl 16) -bor (3 -shl 30)
  [W9.K3]::PostMessage($hwnd, 0x0100, [System.IntPtr]$vk, [System.IntPtr]$dn) | Out-Null
  Start-Sleep -Milliseconds 150
  [W9.K3]::PostMessage($hwnd, 0x0101, [System.IntPtr]$vk, [System.IntPtr]$up) | Out-Null
}
$seq = $args[0]
$start = Get-Date
try {
  $p = Get-Process haya -ErrorAction Stop | Select-Object -First 1
  $hwnd = $p.MainWindowHandle
  if ($hwnd -eq 0) { Write-Output 'focus: no main window'; exit 1 }
  Write-Output ("focus: haya hwnd={0}" -f $hwnd)
} catch { Write-Output 'focus: no haya process'; exit 1 }
$events = @()
foreach ($item in $seq.Split(',')) {
  $pp = $item.Split(':')
  $vk = if ($pp[1].StartsWith('0x')) { [Convert]::ToInt32($pp[1], 16) } else { [int]$pp[1] }
  $events += [pscustomobject]@{at = [double]$pp[0]; vk = $vk}
}
foreach ($e in ($events | Sort-Object at)) {
  $wait = $e.at - ((Get-Date) - $start).TotalSeconds
  if ($wait -gt 0) { Start-Sleep -Milliseconds ([int]($wait * 1000)) }
  try { $p.Refresh() } catch {}
  if ($p.HasExited) { Write-Output 'game exited'; break }
  $h = $p.MainWindowHandle
  if ($h -ne 0) { $hwnd = $h }
  Write-Output ("tap 0x{0:X} at {1}s" -f $e.vk, [int]((Get-Date) - $start).TotalSeconds)
  TapWin $hwnd $e.vk
}