$ErrorActionPreference='Stop'
$env:PATH='C:\msys64\ucrt64\bin;'+$env:PATH
$env:XC2_ROMFS='D:/consoles/ns/hayarigami-recomp/build/extracted/v0/romfs'
$dir='D:/consoles/ns/hayarigami-recomp'
Add-Type -Namespace W -Name K -MemberDefinition @'
[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, System.UIntPtr dwExtraInfo);
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(System.IntPtr h);
[DllImport("user32.dll")] public static extern bool BringWindowToTop(System.IntPtr h);
[DllImport("user32.dll")] public static extern bool ShowWindow(System.IntPtr h, int c);
[DllImport("user32.dll")] public static extern System.IntPtr GetForegroundWindow();
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(System.IntPtr h, out uint pid);
[DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool f);
[DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
'@
$p = Start-Process -FilePath "$dir/build/v0/haya.exe" -ArgumentList '--seconds','26','--shot',"$dir/build/v0/shot_menu2.png" -PassThru
$hwnd=[IntPtr]::Zero
for($i=0;$i -lt 40 -and $hwnd -eq [IntPtr]::Zero;$i++){ Start-Sleep -Milliseconds 500; $p.Refresh(); $hwnd=$p.MainWindowHandle }
Write-Host "hwnd=$hwnd"
for($i=0;$i -lt 6;$i++){
  $fg=[W.K]::GetForegroundWindow()
  if($fg -eq $hwnd){ Write-Host "foreground ok at try $i"; break }
  [void][W.K]::ShowWindow($hwnd,9)
  [void][W.K]::BringWindowToTop($hwnd)
  [void][W.K]::SetForegroundWindow($hwnd)
  $tid=[W.K]::GetWindowThreadProcessId($hwnd,[ref]([uint32]0))
  Start-Sleep -Milliseconds 400
}
Write-Host ("fg=" + [W.K]::GetForegroundWindow() + " hwnd=" + $hwnd)
Start-Sleep -Seconds 3
function Tap([int]$vk,[string]$name) {
  Write-Host "tap $name"
  [W.K]::keybd_event([byte]$vk, 0, 0, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 150
  [W.K]::keybd_event([byte]$vk, 0, 2, [System.UIntPtr]::Zero)
  Start-Sleep -Milliseconds 700
}
Tap 0x45 'E'    # A button
Start-Sleep -Seconds 1
Tap 0x45 'E'
Start-Sleep -Seconds 2
Tap 0x28 'Down'
Tap 0x45 'E'
$p.WaitForExit()
Write-Host "exit $($p.ExitCode)"
