Add-Type -AssemblyName System.Drawing
Add-Type -Namespace W9 -Name Cap -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool GetWindowRect(System.IntPtr hWnd, out RECT r);
[DllImport("user32.dll")] public static extern System.IntPtr GetDC(System.IntPtr hWnd);
[DllImport("user32.dll")] public static extern int ReleaseDC(System.IntPtr hWnd, System.IntPtr hDC);
[DllImport("gdi32.dll")] public static extern System.IntPtr CreateCompatibleDC(System.IntPtr hdc);
[DllImport("gdi32.dll")] public static extern System.IntPtr CreateCompatibleBitmap(System.IntPtr hdc, int w, int h);
[DllImport("gdi32.dll")] public static extern System.IntPtr SelectObject(System.IntPtr hdc, System.IntPtr h);
[DllImport("gdi32.dll")] public static extern bool BitBlt(System.IntPtr hd, int x, int y, int cx, int cy, System.IntPtr hs, int x1, int y1, int rop);
[DllImport("gdi32.dll")] public static extern bool DeleteDC(System.IntPtr hdc);
[DllImport("gdi32.dll")] public static extern bool DeleteObject(System.IntPtr h);
public struct RECT { public int L, T, R, B; }
'@
$p = Get-Process haya -ErrorAction Stop | Select-Object -First 1
$rc = New-Object W9.Cap+RECT
[W9.Cap]::GetWindowRect($p.MainWindowHandle, [ref]$rc) | Out-Null
$w = $rc.R - $rc.L; $hh = $rc.B - $rc.T
$sdc = [W9.Cap]::GetDC([System.IntPtr]::Zero)
$mdc = [W9.Cap]::CreateCompatibleDC($sdc)
$bmp = [W9.Cap]::CreateCompatibleBitmap($sdc, $w, $hh)
[W9.Cap]::SelectObject($mdc, $bmp) | Out-Null
[W9.Cap]::BitBlt($mdc, 0, 0, $w, $hh, $sdc, $rc.L, $rc.T, 0x00CC0020) | Out-Null
$img = [System.Drawing.Image]::FromHbitmap($bmp)
$img.Save($args[0], [System.Drawing.Imaging.ImageFormat]::Png)
[W9.Cap]::DeleteObject($bmp) | Out-Null
[W9.Cap]::DeleteDC($mdc) | Out-Null
[W9.Cap]::ReleaseDC([System.IntPtr]::Zero, $sdc) | Out-Null
Write-Output ("screen-shot done " + $w + "x" + $hh)
