$ErrorActionPreference = 'Stop'
$output = [System.IO.Path]::GetFullPath($args[0])

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)

    $parameter = $hwp.HParameterSet.HTableCreation
    $hwp.HAction.GetDefault('TableCreate', $parameter.HSet)
    $parameter.Rows = 4
    $parameter.Cols = 8
    $parameter.WidthType = 2
    $parameter.HeightType = 1
    $parameter.WidthValue = $hwp.MiliToHwpUnit(160.0)
    $parameter.HeightValue = $hwp.MiliToHwpUnit(20.0)
    $parameter.CreateItemArray('ColWidth', 8)
    $parameter.CreateItemArray('RowHeight', 4)
    foreach ($index in 0..7) {
        $parameter.ColWidth.Item($index) = $hwp.MiliToHwpUnit(20.0)
    }
    foreach ($index in 0..3) {
        $parameter.RowHeight.Item($index) = $hwp.MiliToHwpUnit(5.0)
    }
    $created = $hwp.HAction.Execute('TableCreate', $parameter.HSet)
    Write-Output ('created=' + $created)

    $values = @(
        'When', 'Standard', 'Unit', 'Area', 'Element', 'Method', 'Grade', 'Detail',
        'October', 'S', 'U', 'R', 'E', 'M', 'A', 'High',
        '', '', '', '', '', '', 'B', 'Middle',
        '', '', '', '', '', '', 'C', 'Low'
    )
    foreach ($value in $values) {
        $insert = $hwp.HParameterSet.HInsertText
        $hwp.HAction.GetDefault('InsertText', $insert.HSet)
        $insert.Text = $value
        [void]$hwp.HAction.Execute('InsertText', $insert.HSet)
        [void]$hwp.HAction.Run('TableRightCell')
    }

    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'Save failed' }
    Write-Output ('pages=' + $hwp.PageCount)
    Write-Output ('output=' + $output)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
