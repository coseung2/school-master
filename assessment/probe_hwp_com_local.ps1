$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $args[0]).Path
$target = [System.IO.Path]::GetFullPath($args[1])
$log = [System.IO.Path]::GetFullPath($args[2])

function Log([string]$message) {
    Add-Content -LiteralPath $log -Value ((Get-Date -Format 'HH:mm:ss.fff') + ' ' + $message)
}

Log 'before-com'
$hwp = New-Object -ComObject HWPFrame.HwpObject
Log 'after-com'
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    Log 'visible-false'
    Log 'before-open'
    $opened = $hwp.Open($source, 'HWPX', 'forceopen:true;versionwarning:false;suspendpassword:true')
    Log ('after-open=' + $opened)
    Log ('pages=' + $hwp.PageCount)
    $saved = $hwp.SaveAs($target, 'HWPX', '')
    Log ('saved=' + $saved)
} catch {
    Log ('fatal=' + $_.Exception.ToString())
    throw
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
