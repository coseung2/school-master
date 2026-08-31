$keys = @(
    'Registry::HKEY_CURRENT_USER\Software\HNC\HwpAutomation\Modules',
    'Registry::HKEY_CURRENT_USER\Software\HNC\Office\HwpAutomation\Modules',
    'Registry::HKEY_LOCAL_MACHINE\Software\HNC\HwpAutomation\Modules',
    'Registry::HKEY_LOCAL_MACHINE\Software\WOW6432Node\HNC\HwpAutomation\Modules'
)

foreach ($key in $keys) {
    Write-Output "KEY $key"
    if (Test-Path -LiteralPath $key) {
        Get-ItemProperty -LiteralPath $key | Format-List
    } else {
        Write-Output 'missing'
    }
}

Get-ChildItem -LiteralPath 'C:\Program Files (x86)\HNC' -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match 'FilePath|Checker|CheckDLL|Automation' } |
    Select-Object FullName, Length
