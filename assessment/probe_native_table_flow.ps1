$ErrorActionPreference = 'Stop'

$output = [System.IO.Path]::GetFullPath($args[0])
$pdfOutput = [System.IO.Path]::GetFullPath($args[1])

function Insert-Text($hwp, [string]$value) {
    $parameter = $hwp.HParameterSet.HInsertText
    $hwp.HAction.GetDefault('InsertText', $parameter.HSet)
    $parameter.Text = $value
    if (-not $hwp.HAction.Execute('InsertText', $parameter.HSet)) {
        throw "InsertText failed: $value"
    }
}

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)

    $table = $hwp.HParameterSet.HTableCreation
    $hwp.HAction.GetDefault('TableCreate', $table.HSet)
    $table.Rows = 2
    $table.Cols = 2
    $table.WidthType = 2
    $table.HeightType = 1
    $table.WidthValue = $hwp.MiliToHwpUnit(120.0)
    $table.HeightValue = $hwp.MiliToHwpUnit(30.0)
    $table.CreateItemArray('ColWidth', 2)
    $table.CreateItemArray('RowHeight', 2)
    foreach ($index in 0..1) {
        $table.ColWidth.Item($index) = $hwp.MiliToHwpUnit(60.0)
        $table.RowHeight.Item($index) = $hwp.MiliToHwpUnit(15.0)
    }
    if (-not $hwp.HAction.Execute('TableCreate', $table.HSet)) {
        throw 'TableCreate failed'
    }

    $values = @('A1', 'A2', 'B1', 'B2')
    for ($index = 0; $index -lt $values.Count; $index++) {
        Insert-Text $hwp $values[$index]
        if ($index -lt $values.Count - 1) {
            if (-not $hwp.HAction.Run('TableRightCell')) {
                throw "TableRightCell failed at $index"
            }
        }
    }

    $beforeList = 0
    $beforePara = 0
    $beforePos = 0
    [void]$hwp.GetPos([ref]$beforeList, [ref]$beforePara, [ref]$beforePos)
    $moved = $hwp.MovePos(3, 0, 0)
    $afterList = 0
    $afterPara = 0
    $afterPos = 0
    [void]$hwp.GetPos([ref]$afterList, [ref]$afterPara, [ref]$afterPos)
    Write-Output ("before=$beforeList,$beforePara,$beforePos")
    Write-Output ('moveDocEnd=' + $moved)
    Write-Output ("after=$afterList,$afterPara,$afterPos")
    [void]$hwp.HAction.Run('BreakPage')
    Insert-Text $hwp 'OUTSIDE TABLE'

    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'HWPX SaveAs failed' }
    if (-not $hwp.SaveAs($pdfOutput, 'PDF', '')) { throw 'PDF SaveAs failed' }
    Write-Output ('pages=' + $hwp.PageCount)
    Write-Output ('hwpx=' + $output)
    Write-Output ('pdf=' + $pdfOutput)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
