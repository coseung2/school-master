$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $args[0]).Path
$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    $opened = $hwp.Open($source, '', '')
    Write-Output ('opened=' + $opened)
    if ($opened) { Write-Output ('pages=' + $hwp.PageCount) }
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
