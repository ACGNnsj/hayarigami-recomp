Add-Type -Namespace W9 -Name K1 -MemberDefinition @'
[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, System.UIntPtr dwExtraInfo);
'@
$vk = 0x45
if ($args.Count -ge 1) { $vk = if ($args[0].StartsWith('0x')) { [Convert]::ToInt32($args[0], 16) } else { [int]$args[0] } }
$hold = 150
if ($args.Count -ge 2) { $hold = [int]$args[1] }
[W9.K1]::keybd_event([byte]$vk, 0, 0, [System.UIntPtr]::Zero)
Start-Sleep -Milliseconds $hold
[W9.K1]::keybd_event([byte]$vk, 0, 2, [System.UIntPtr]::Zero)
Write-Output ("tapped 0x{0:X}" -f $vk)
