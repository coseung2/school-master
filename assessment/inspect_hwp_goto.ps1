$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $args[0]).Path
$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    if (-not $hwp.Open($source, '', '')) { throw 'Open failed' }
    $goto = $hwp.HParameterSet.HGotoE
    [void]$hwp.HAction.GetDefault('Goto', $goto.HSet)
    Write-Output 'MEMBERS'
    $goto | Get-Member | Select-Object Name, MemberType, Definition | Format-Table -AutoSize
    Write-Output 'PROPERTIES'
    $goto | Format-List *
    Write-Output ('PAGECOUNT=' + $hwp.PageCount)
    Write-Output ('POS=' + (($hwp.GetPos()) -join ','))
    foreach ($selectionIndex in 0..10) {
        $hwp.MovePos(2, 0, 0) | Out-Null
        [void]$hwp.HAction.GetDefault('Goto', $goto.HSet)
        $goto.SetSelectionIndex = $selectionIndex
        $goto.HSet.SetItem('DialogResult', 2)
        $result = $hwp.HAction.Execute('Goto', $goto.HSet)
        Write-Output ("GOTO index=$selectionIndex result=$result pos=" + (($hwp.GetPos()) -join ','))
    }
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
