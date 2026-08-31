Get-CimInstance Win32_Process |
    Where-Object { $_.Name -match '^(Hwp|HOffice|Hnc).*' } |
    Select-Object Name, ProcessId, ParentProcessId, CreationDate, ExecutablePath, CommandLine |
    Format-List
