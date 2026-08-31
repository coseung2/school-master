$ErrorActionPreference = 'Stop'

$image = (Resolve-Path -LiteralPath $args[0]).Path
$output = [System.IO.Path]::GetFullPath($args[1])
$pdfOutput = [System.IO.Path]::GetFullPath($args[2])
$log = [System.IO.Path]::GetFullPath('tmp\picture-probe.log')

function Log([string]$message) {
    Add-Content -LiteralPath $log -Value ((Get-Date -Format 'HH:mm:ss.fff') + ' ' + $message)
}

Set-Content -LiteralPath $log -Value ''

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    Log 'com-created'
    $hwp.XHwpWindows.Item(0).Visible = $false
    try {
        $registered = $hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModuleExample')
        Log ('registered=' + $registered)
    } catch {
        Log ('register-error=' + $_.Exception.Message)
    }
    $hwp.SetMessageBoxMode(0)
    Log 'before-picture'
    $result = $hwp.InsertPicture($image, $true, 0, $false, $false, 0, 0, 0)
    Log ('after-picture=' + ($null -ne $result))
    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'HWPX SaveAs failed' }
    Log 'saved-hwpx'
    if (-not $hwp.SaveAs($pdfOutput, 'PDF', '')) { throw 'PDF SaveAs failed' }
    Log 'saved-pdf'
    Write-Output ('pages=' + $hwp.PageCount)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
