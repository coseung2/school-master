$ErrorActionPreference = 'Stop'

$template = (Resolve-Path -LiteralPath $args[0]).Path
$source = (Resolve-Path -LiteralPath $args[1]).Path
$metadataPath = (Resolve-Path -LiteralPath $args[2]).Path
$output = [System.IO.Path]::GetFullPath($args[3])
$pdfOutput = [System.IO.Path]::GetFullPath($args[4])
$metadata = Get-Content -LiteralPath $metadataPath -Raw -Encoding UTF8 | ConvertFrom-Json
$subjects = @('사회', '수학', '실과', '음악', '미술', '영어')

function Insert-Text($hwp, [string]$value) {
    $parameter = $hwp.HParameterSet.HInsertText
    $hwp.HAction.GetDefault('InsertText', $parameter.HSet)
    $parameter.Text = $value
    [void]$hwp.HAction.Execute('InsertText', $parameter.HSet)
}

function Insert-OperationSection($hwp, [string]$subject, $items) {
    [void]$hwp.HAction.Run('BreakPage')
    Insert-Text $hwp ($subject + '과 교수학습 및 평가 운영계획')
    [void]$hwp.HAction.Run('BreakPara')
    Insert-Text $hwp '2026학년도 2학기  |  5학년'
    [void]$hwp.HAction.Run('BreakPara')
    Insert-Text $hwp '시기 | 성취기준 | 단원명 | 평가 영역 | 평가 요소 | 수업·평가 방법, 연계의 주안점 | 평가 기준'
    [void]$hwp.HAction.Run('BreakPara')
    foreach ($item in $items) {
        Insert-Text $hwp (($item.when) + ' | ' + ($item.standard) + ' | ' + ($item.unit) + ' | ' + ($item.area) + ' | ' + ($item.element) + ' | ' + ($item.method))
        [void]$hwp.HAction.Run('BreakPara')
        Insert-Text $hwp ('A | ' + $item.A)
        [void]$hwp.HAction.Run('BreakPara')
        Insert-Text $hwp ('B | ' + $item.B)
        [void]$hwp.HAction.Run('BreakPara')
        Insert-Text $hwp ('C | ' + $item.C)
        [void]$hwp.HAction.Run('BreakPara')
    }
}

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    if (-not $hwp.Open($template, '', '')) { throw 'Failed to open 1st-semester template' }

    function Replace-All([string]$oldValue, [string]$newValue) {
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

    # The cover text is corrected in the XML-preserving post-processing pass.

    $hwp.MovePos(3, 0, 0) | Out-Null
    foreach ($subject in $subjects) {
        Insert-OperationSection $hwp $subject $metadata.$subject
    }

    [void]$hwp.HAction.Run('BreakPage')
    $insert = $hwp.HParameterSet.HInsertFile
    $hwp.HAction.GetDefault('InsertFile', $insert.HSet)
    $insert.FileName = $source
    $insert.KeepSection = 1
    $insert.KeepCharshape = 1
    $insert.KeepParashape = 1
    $insert.KeepStyle = 1
    if (-not $hwp.HAction.Execute('InsertFile', $insert.HSet)) { throw 'InsertFile failed' }

    # Content corrections are applied in a separate XML-preserving pass after Hancom saves the file.

    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'HWPX SaveAs failed' }
    if (-not $hwp.SaveAs($pdfOutput, 'PDF', '')) { throw 'PDF SaveAs failed' }
    Write-Output ('pages=' + $hwp.PageCount)
    Write-Output ('hwpx=' + $output)
    Write-Output ('pdf=' + $pdfOutput)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
