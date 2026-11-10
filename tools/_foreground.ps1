$p = Get-Process haya -ErrorAction Stop | Select-Object -First 1
$h = $p.MainWindowHandle
Add-Type -Namespace W9 -Name Fg -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(System.IntPtr hWnd);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(System.IntPtr hWnd);
[DllImport("user32.dll")] public static extern bool ShowWindow(System.IntPtr hWnd, int nCmd);
'@
Write-Output ("hwnd=" + $h)
Write-Output ("visible=" + [W9.Fg]::IsWindowVisible($h))
[W9.Fg]::ShowWindow($h, 9) | Out-Null
[W9.Fg]::SetForegroundWindow($h) | Out-Null
Write-Output "foregrounded"
