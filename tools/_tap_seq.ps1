Add-Type -Namespace W9 -Name K2 -MemberDefinition @'
[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, System.UIntPtr dwExtraInfo);
'@
function Tap([int]$vk) {
  [W9.K2]::keybd_event([byte]$vk, 0, 0, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 150
  [W9.K2]::keybd_event([byte]$vk, 0, 2, [System.UIntPtr]::Zero)
}
# sequence: "seconds:vk,seconds:vk,..."  vk in hex or decimal
$seq = $args[0]
$start = Get-Date
# Make sure the taps land in the game: bring the haya window to the front (once; logs if missing).
try {
  $p = Get-Process haya -ErrorAction Stop | Select-Object -First 1
  $ws = New-Object -ComObject WScript.Shell
  if (-not $ws.AppActivate($p.Id)) { Write-Output 'focus: AppActivate refused' }
  else { Write-Output 'focus: haya activated' }
} catch { Write-Output 'focus: no haya process' }
# Items are taps "t:vk" or holds "t1Ht2:vk" (down at t1, up at t2); vk hex or decimal.
$events = @()
foreach ($item in $seq.Split(',')) {
  $p = $item.Split(':')
  $vk = if ($p[1].StartsWith('0x')) { [Convert]::ToInt32($p[1], 16) } else { [int]$p[1] }
  if ($p[0].Contains('H')) {
    $h = $p[0].Split('H')
    $events += [pscustomobject]@{at = [double]$h[0]; op = 'down'; vk = $vk}
    $events += [pscustomobject]@{at = [double]$h[1]; op = 'up'; vk = $vk}
  } else {
    $events += [pscustomobject]@{at = [double]$p[0]; op = 'tap'; vk = $vk}
  }
}
foreach ($e in ($events | Sort-Object at)) {
  $wait = $e.at - ((Get-Date) - $start).TotalSeconds
  if ($wait -gt 0) { Start-Sleep -Milliseconds ([int]($wait * 1000)) }
  try { (New-Object -ComObject WScript.Shell).AppActivate(((Get-Process haya -ErrorAction Stop | Select-Object -First 1).Id)) | Out-Null } catch {}
  if ($e.op -eq 'tap') {
    Write-Output ("tap 0x{0:X} at {1}s" -f $e.vk, [int]((Get-Date) - $start).TotalSeconds)
    Tap $e.vk
  } else {
    Write-Output ("{0} 0x{1:X} at {2}s" -f $e.op, $e.vk, [int]((Get-Date) - $start).TotalSeconds)
    $fl = 0; if ($e.op -eq 'up') { $fl = 2 }; [W9.K2]::keybd_event([byte]$e.vk, 0, $fl, [System.UIntPtr]::Zero)
  }
}
