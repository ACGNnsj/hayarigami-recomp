Add-Type -AssemblyName System.Drawing
Add-Type -Namespace W9 -Name Shot -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool PrintWindow(System.IntPtr hWnd, System.IntPtr hdcBlt, int nFlags);
[DllImport("user32.dll")] public static extern bool GetWindowRect(System.IntPtr hWnd, out RECT r);
public struct RECT { public int L, T, R, B; }
'@
$p = Get-Process haya -ErrorAction Stop | Select-Object -First 1
$h = $p.MainWindowHandle
if ($h -eq 0) { Write-Output 'no hwnd'; exit 1 }
$rc = New-Object W9.Shot+RECT
[W9.Shot]::GetWindowRect($h, [ref]$rc) | Out-Null
$w = $rc.R - $rc.L; $hh = $rc.B - $rc.T
if ($w -le 0 -or $hh -le 0) { Write-Output 'zero rect'; exit 1 }
$bmp = New-Object System.Drawing.Bitmap($w, $hh)
$gfx = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $gfx.GetHdc()
[W9.Shot]::PrintWindow($h, $hdc, 0) | Out-Null
$gfx.ReleaseHdc($hdc)
$gfx.Dispose()
$out = $args[0]
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output ("shot {0} {1}x{2}" -f $out, $w, $hh)
