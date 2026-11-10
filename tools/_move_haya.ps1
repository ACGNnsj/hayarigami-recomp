$p = Get-Process haya -ErrorAction Stop | Select-Object -First 1
$h = $p.MainWindowHandle
Add-Type -Namespace W9 -Name Mv -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetWindowPos(System.IntPtr hWnd, System.IntPtr hAfter, int X, int Y, int cx, int cy, uint uFlags);
'@
[W9.Mv]::SetWindowPos($h, [System.IntPtr]::Zero, 950, 450, 973, 576, 0x0040) | Out-Null
Write-Output "moved"