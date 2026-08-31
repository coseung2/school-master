$ErrorActionPreference = 'Stop'

$source = (Resolve-Path -LiteralPath $args[0]).Path
$target = [System.IO.Path]::GetFullPath($args[1])

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    try { [void]$hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModuleExample') } catch {}
    try { $hwp.SetMessageBoxMode(0x00020000) } catch {}
    if (-not $hwp.Open($source, 'HWPX', 'forceopen:true')) {
        throw "Failed to open $source"
    }
    $hwp.MovePos(2, 0, 0)
    Write-Output ('text=' + $hwp.GetTextFile('TEXT', ''))
    Write-Output ('pages=' + $hwp.PageCount)
    $hwp.SaveAs($target, 'HWPX', '') | Out-Null
    Write-Output ('saved=' + $target)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
