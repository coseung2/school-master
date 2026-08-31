$ErrorActionPreference = 'Stop'

$template = (Resolve-Path -LiteralPath $args[0]).Path
$source = (Resolve-Path -LiteralPath $args[1]).Path
$output = [System.IO.Path]::GetFullPath($args[2])

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    if (-not $hwp.Open($template, '', '')) { throw 'Failed to open template' }

    $hwp.MovePos(3, 0, 0) | Out-Null
    $find = $hwp.HParameterSet.HFindReplace
    $hwp.HAction.GetDefault('AllReplace', $find.HSet)
    $find.FindString = '5학년 1학기'
    $find.ReplaceString = '5학년 2학기'
    $find.IgnoreMessage = 1
    $find.FindRegExp = 0
    $find.FindStyle = ''
    $find.ReplaceStyle = ''
    $find.Direction = 0
    $find.FindType = 1
    $hwp.HAction.Execute('AllReplace', $find.HSet) | Out-Null

    $hwp.MovePos(3, 0, 0) | Out-Null
    $hwp.HAction.Run('BreakPage') | Out-Null
    $insert = $hwp.HParameterSet.HInsertFile
    $hwp.HAction.GetDefault('InsertFile', $insert.HSet)
    $insert.FileName = $source
    $insert.KeepSection = 1
    $insert.KeepCharshape = 1
    $insert.KeepParashape = 1
    $insert.KeepStyle = 1
    if (-not $hwp.HAction.Execute('InsertFile', $insert.HSet)) { throw 'InsertFile failed' }

    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'SaveAs failed' }
    Write-Output ('pages=' + $hwp.PageCount)
    Write-Output ('output=' + $output)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
