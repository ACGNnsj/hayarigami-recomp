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
foreach ($item in $seq.Split(',')) {
  $p = $item.Split(':')
  $at = [int]$p[0]
  $vk = if ($p[1].StartsWith('0x')) { [Convert]::ToInt32($p[1], 16) } else { [int]$p[1] }
  $wait = $at - ((Get-Date) - $start).TotalSeconds
  if ($wait -gt 0) { Start-Sleep -Milliseconds ([int]($wait * 1000)) }
  Write-Output ("tap " + $p[1] + " at " + [int]((Get-Date) - $start).TotalSeconds + "s")
  Tap $vk
}
