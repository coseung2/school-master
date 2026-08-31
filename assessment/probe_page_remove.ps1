$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $args[0]).Path
$output = [System.IO.Path]::GetFullPath($args[1])

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    if (-not $hwp.Open($source, '', '')) { throw 'Open failed' }
    Write-Output ('before=' + $hwp.PageCount)
    [void]$hwp.HAction.Run('MoveDocBegin')
    [void]$hwp.HAction.Run('MovePageDown')
    [void]$hwp.HAction.Run('MovePageBegin')
    foreach ($action in @('PageRemove', 'DeletePage', 'PageDelete')) {
        try {
            $result = $hwp.HAction.Run($action)
            Write-Output ($action + '=' + $result + ';pages=' + $hwp.PageCount)
            if ($result) { break }
        } catch {
            Write-Output ($action + '_ERROR=' + $_.Exception.Message)
        }
    }
    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'Save failed' }
    Write-Output ('output=' + $output)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
