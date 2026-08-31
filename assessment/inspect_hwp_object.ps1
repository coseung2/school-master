$ErrorActionPreference = 'Stop'

$source = (Resolve-Path -LiteralPath $args[0]).Path
$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    if (-not $hwp.Open($source, '', '')) { throw 'Open failed' }

    $hwp | Get-Member |
        Where-Object { $_.Name -match 'Pos|Select|Text|Document|Move|Copy|Paste|Page|Block' } |
        Select-Object Name, MemberType, Definition |
        Format-Table -AutoSize

    $list = 0
    $para = 0
    $pos = 0
    [void]$hwp.GetPos([ref]$list, [ref]$para, [ref]$pos)
    Write-Output ("START_POS=$list,$para,$pos")

    foreach ($action in @('MoveDocBegin', 'MovePageDown', 'MovePageBegin', 'MovePageEnd', 'MoveSelPageEnd', 'MoveSelDocEnd')) {
        $result = $hwp.HAction.Run($action)
        $list = 0
        $para = 0
        $pos = 0
        [void]$hwp.GetPos([ref]$list, [ref]$para, [ref]$pos)
        Write-Output ("ACTION=$action RESULT=$result POS=$list,$para,$pos")
    }
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
