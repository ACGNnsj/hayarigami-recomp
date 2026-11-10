Add-Type -Namespace R9 -Name Rip -MemberDefinition @'
[DllImport("kernel32.dll")] public static extern System.IntPtr OpenThread(int access, bool inherit, int tid);
[DllImport("kernel32.dll")] public static extern int SuspendThread(System.IntPtr h);
[DllImport("kernel32.dll")] public static extern int ResumeThread(System.IntPtr h);
[DllImport("kernel32.dll")] public static extern bool GetThreadContext(System.IntPtr h, byte[] ctx);
[DllImport("kernel32.dll")] public static extern bool CloseHandle(System.IntPtr h);
'@
$tid = [int]$args[0]; $n = [int]$args[1]
$h = [R9.Rip]::OpenThread(0x1a, $false, $tid)
if ($h -eq [System.IntPtr]::Zero) { Write-Output 'open-fail'; exit 1 }
for ($i = 0; $i -lt $n; $i++) {
  [R9.Rip]::SuspendThread($h) | Out-Null
  $ctx = New-Object byte[] 2048
  [BitConverter]::GetBytes([uint32]0x10001).CopyTo($ctx, 0)
  $ok = [R9.Rip]::GetThreadContext($h, $ctx)
  [R9.Rip]::ResumeThread($h) | Out-Null
  if ($ok) { $rip = [BitConverter]::ToUInt64($ctx, 264); Write-Output ("RIP=0x{0:X}" -f $rip) } else { Write-Output 'ctx-fail' }
  Start-Sleep -Milliseconds 400
}
[R9.Rip]::CloseHandle($h) | Out-Null
