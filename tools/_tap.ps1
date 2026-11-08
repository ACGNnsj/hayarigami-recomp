Add-Type -Namespace W9 -Name K -MemberDefinition @'
[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, System.UIntPtr dwExtraInfo);
'@
function Tap([int]$vk) {
  [W9.K]::keybd_event([byte]$vk, 0, 0, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 150
  [W9.K]::keybd_event([byte]$vk, 0, 2, [System.UIntPtr]::Zero)
}
Start-Sleep -Seconds 9
Tap 0x45
Start-Sleep -Seconds 2
Tap 0x45
