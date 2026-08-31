$ErrorActionPreference = 'Stop'

$metadataPath = (Resolve-Path -LiteralPath $args[0]).Path
$output = [System.IO.Path]::GetFullPath($args[1])
$pdfOutput = [System.IO.Path]::GetFullPath($args[2])
$metadata = Get-Content -LiteralPath $metadataPath -Raw -Encoding UTF8 | ConvertFrom-Json

function Insert-Text($hwp, [string]$value) {
    $parameter = $hwp.HParameterSet.HInsertText
    $hwp.HAction.GetDefault('InsertText', $parameter.HSet)
    $parameter.Text = $value
    [void]$hwp.HAction.Execute('InsertText', $parameter.HSet)
}

function Create-Table($hwp, $items) {
    $rowCount = 1 + (3 * $items.Count)
    $totalCells = $rowCount * 8
    $writtenCells = 0
    $table = $hwp.HParameterSet.HTableCreation
    $hwp.HAction.GetDefault('TableCreate', $table.HSet)
    $table.Rows = $rowCount
    $table.Cols = 8
    $table.WidthType = 2
    $table.HeightType = 1
    $table.WidthValue = $hwp.MiliToHwpUnit(170.0)
    $table.HeightValue = $hwp.MiliToHwpUnit(7.0 * $rowCount)
    $table.CreateItemArray('ColWidth', 8)
    $table.CreateItemArray('RowHeight', $rowCount)
    foreach ($index in 0..7) { $table.ColWidth.Item($index) = $hwp.MiliToHwpUnit(21.25) }
    foreach ($index in 0..($rowCount - 1)) { $table.RowHeight.Item($index) = $hwp.MiliToHwpUnit(7.0) }
    if (-not $hwp.HAction.Execute('TableCreate', $table.HSet)) { throw 'TableCreate failed' }

    $headers = @('시기','성취기준','단원명','평가 영역','평가 요소','수업·평가 방법','기준','내용')
    foreach ($value in $headers) {
        Insert-Text $hwp $value
        $writtenCells++
        if ($writtenCells -lt $totalCells) { [void]$hwp.HAction.Run('TableRightCell') }
    }
    foreach ($item in $items) {
        foreach ($row in @(
            @($item.when,$item.standard,$item.unit,$item.area,$item.element,$item.method,'A',$item.A),
            @('','','','','','','B',$item.B),
            @('','','','','','','C',$item.C)
        )) {
            foreach ($value in $row) {
                Insert-Text $hwp ([string]$value)
                $writtenCells++
                if ($writtenCells -lt $totalCells) { [void]$hwp.HAction.Run('TableRightCell') }
            }
        }
    }
    [void]$hwp.HAction.Run('Cancel')
    [void]$hwp.MovePos(3,0,0)
}

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    foreach ($subject in @('사회','수학')) {
        Insert-Text $hwp ($subject + '과 교수학습 및 평가 운영계획')
        [void]$hwp.HAction.Run('BreakPara')
        Create-Table $hwp $metadata.$subject
        [void]$hwp.HAction.Run('BreakPage')
    }
    Insert-Text $hwp 'END OF DOCUMENT'
    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'HWPX SaveAs failed' }
    if (-not $hwp.SaveAs($pdfOutput, 'PDF', '')) { throw 'PDF SaveAs failed' }
    Write-Output ('pages=' + $hwp.PageCount)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
