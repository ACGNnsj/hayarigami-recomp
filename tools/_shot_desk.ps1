Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$b = New-Object Drawing.Bitmap(973, 576)
$g = [Drawing.Graphics]::FromImage($b)
$g.CopyFromScreen(500, 200, 0, 0, $b.Size)
$b.Save('build/v0/idle_check.png')
$g.Dispose()
$b.Dispose()
Write-Output 'desktop grabbed'
