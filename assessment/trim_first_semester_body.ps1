$ErrorActionPreference = 'Stop'

$source = (Resolve-Path -LiteralPath $args[0]).Path
$output = [System.IO.Path]::GetFullPath($args[1])

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    if (-not $hwp.Open($source, '', '')) { throw 'Open failed' }

    [void]$hwp.HAction.Run('MoveDocBegin')
    [void]$hwp.HAction.Run('MovePageDown')
    $list = 0
    $para = 0
    $pos = 0
    [void]$hwp.GetPos([ref]$list, [ref]$para, [ref]$pos)
    if (-not $hwp.SelectText($list, $para, $pos, -1)) { throw 'SelectText failed' }
    [void]$hwp.HAction.Run('Delete')

    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'Save failed' }
    Write-Output ('pages=' + $hwp.PageCount)
    Write-Output ('output=' + $output)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
