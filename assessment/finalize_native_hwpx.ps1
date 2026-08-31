$ErrorActionPreference = 'Stop'

$source = (Resolve-Path -LiteralPath $args[0]).Path
$output = [System.IO.Path]::GetFullPath($args[1])
$pdfOutput = [System.IO.Path]::GetFullPath($args[2])

function Replace-All($hwp, [string]$oldValue, [string]$newValue) {
    $hwp.MovePos(2, 0, 0) | Out-Null
    $find = $hwp.HParameterSet.HFindReplace
    $hwp.HAction.GetDefault('AllReplace', $find.HSet)
    $find.FindString = $oldValue
    $find.ReplaceString = $newValue
    $find.IgnoreMessage = 1
    $find.FindRegExp = 0
    $find.FindStyle = ''
    $find.ReplaceStyle = ''
    $find.Direction = 0
    $find.FindType = 1
    [void]$hwp.HAction.Execute('AllReplace', $find.HSet)
}

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    if (-not $hwp.Open($source, '', '')) { throw 'Failed to open native HWPX' }

    $replacements = Get-Content -LiteralPath ([System.IO.Path]::ChangeExtension($PSCommandPath, '.json')) -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($item in $replacements) {
        Replace-All $hwp ([string]$item.old) ([string]$item.new)
    }

    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'HWPX SaveAs failed' }
    if (-not $hwp.SaveAs($pdfOutput, 'PDF', '')) { throw 'PDF SaveAs failed' }
    Write-Output ('pages=' + $hwp.PageCount)
    Write-Output ('hwpx=' + $output)
    Write-Output ('pdf=' + $pdfOutput)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
