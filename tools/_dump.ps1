Add-Type -Namespace D9 -Name Dump -MemberDefinition @'
[DllImport("dbghelp.dll")] public static extern bool MiniDumpWriteDump(System.IntPtr hProc, int pid, System.IntPtr hFile, int type, System.IntPtr excp, System.IntPtr user, System.IntPtr cb);
[DllImport("kernel32.dll")] public static extern System.IntPtr OpenProcess(int access, bool inherit, int pid);
[DllImport("kernel32.dll")] public static extern bool CloseHandle(System.IntPtr h);
'@
$pid_ = [int]$args[0]; $path = $args[1]
$h = [D9.Dump]::OpenProcess(0x410, $false, $pid_)
if ($h -eq [System.IntPtr]::Zero) { Write-Output 'open-fail'; exit 1 }
$fs = [System.IO.File]::Create($path)
$ok = [D9.Dump]::MiniDumpWriteDump($h, $pid_, $fs.SafeFileHandle.DangerousGetHandle(), 0, [System.IntPtr]::Zero, [System.IntPtr]::Zero, [System.IntPtr]::Zero)
$fs.Close()
[D9.Dump]::CloseHandle($h) | Out-Null
Write-Output ("dump-ok={0}" -f $ok)
