$ErrorActionPreference = 'Continue'

$source = (Resolve-Path -LiteralPath $args[0]).Path
$variants = @(
    @{ Path = $source; Format = ''; Arg = '' },
    @{ Path = $source; Format = 'HWPX'; Arg = '' },
    @{ Path = $source; Format = ''; Arg = 'forceopen:true' },
    @{ Path = $source.Replace('\', '/'); Format = ''; Arg = '' },
    @{ Path = ('file:///' + $source.Replace('\', '/')); Format = ''; Arg = '' }
)

foreach ($variant in $variants) {
    $hwp = New-Object -ComObject HWPFrame.HwpObject
    try {
        $hwp.XHwpWindows.Item(0).Visible = $false
        $hwp.SetMessageBoxMode(0x20000)
        Write-Output ('TRY path=' + $variant.Path + ' format=' + $variant.Format + ' arg=' + $variant.Arg)
        $opened = $hwp.Open($variant.Path, $variant.Format, $variant.Arg)
        Write-Output ('RESULT=' + $opened)
        if ($opened) { Write-Output ('PAGES=' + $hwp.PageCount) }
    } catch {
        Write-Output ('ERROR=' + $_.Exception.Message)
    } finally {
        try { $hwp.Clear(1) | Out-Null } catch {}
        try { $hwp.Quit() | Out-Null } catch {}
    }
}
