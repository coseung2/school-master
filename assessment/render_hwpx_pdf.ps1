$ErrorActionPreference = 'Stop'

$source = (Resolve-Path -LiteralPath $args[0]).Path
$target = [System.IO.Path]::GetFullPath($args[1])

New-Item -ItemType Directory -Path ([System.IO.Path]::GetDirectoryName($target)) -Force | Out-Null

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    try { $hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule') | Out-Null } catch {}
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    $opened = $hwp.Open($source, 'HWPX', 'forceopen:true;versionwarning:false;suspendpassword:true')
    if (-not $opened) { throw "Failed to open $source" }
    $saved = $hwp.SaveAs($target, 'PDF', '')
    if (-not $saved) { throw "Failed to save PDF to $target" }
    Write-Output ('pages=' + $hwp.PageCount)
    Write-Output ('pdf=' + $target)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
