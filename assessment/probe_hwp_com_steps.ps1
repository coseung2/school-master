$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $args[0]).Path
$log = [System.IO.Path]::GetFullPath($args[1])

function Log([string]$message) {
    Add-Content -LiteralPath $log -Value ((Get-Date -Format 'HH:mm:ss.fff') + ' ' + $message)
}

Log 'before-com'
$hwp = New-Object -ComObject HWPFrame.HwpObject
Log 'after-com'
try {
    $hwp.XHwpWindows.Item(0).Visible = $true
    Log 'visible'
    try {
        $registered = $hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModuleExample')
        Log ('registered=' + $registered)
    } catch {
        Log ('register-error=' + $_.Exception.Message)
    }
    Log 'before-open'
    $opened = $hwp.Open($source, 'HWPX', 'forceopen:true')
    Log ('after-open=' + $opened)
} catch {
    Log ('fatal=' + $_.Exception.ToString())
    throw
}
