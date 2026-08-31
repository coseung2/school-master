$ErrorActionPreference = 'Stop'

$source = (Resolve-Path -LiteralPath $args[0]).Path
$output = [System.IO.Path]::GetFullPath($args[1])

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    if (-not $hwp.Open($source, '', '')) { throw 'Open failed' }

    [void]$hwp.HAction.Run('MoveDocBegin')
    $goto = $hwp.HParameterSet.HGotoE
    $hwp.HAction.GetDefault('Goto', $goto.HSet)
    $goto.SetSelectionIndex = 1
    $goto.HSet.SetItem('DialogResult', 2)
    if (-not $hwp.HAction.Execute('Goto', $goto.HSet)) { throw 'Goto page 2 failed' }
    [void]$hwp.HAction.Run('MovePageBegin')
    [void]$hwp.HAction.Run('MoveSelStart')
    [void]$hwp.HAction.Run('MoveSelDocEnd')
    [void]$hwp.HAction.Run('Delete')

    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'Save failed' }
    Write-Output ('pages=' + $hwp.PageCount)
    Write-Output ('pos=' + ($hwp.KeyIndicator().Item(5)))
    Write-Output ('output=' + $output)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
