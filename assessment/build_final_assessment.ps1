$ErrorActionPreference = 'Stop'

$source = (Resolve-Path -LiteralPath $args[0]).Path
$metadataPath = (Resolve-Path -LiteralPath $args[1]).Path
$output = [System.IO.Path]::GetFullPath($args[2])
$pdfOutput = [System.IO.Path]::GetFullPath($args[3])
$metadata = Get-Content -LiteralPath $metadataPath -Raw -Encoding UTF8 | ConvertFrom-Json
$subjects = @('사회', '수학', '실과', '음악', '미술', '영어')

New-Item -ItemType Directory -Path ([System.IO.Path]::GetDirectoryName($output)) -Force | Out-Null
New-Item -ItemType Directory -Path ([System.IO.Path]::GetDirectoryName($pdfOutput)) -Force | Out-Null

function Insert-Text($hwp, [string]$value) {
    $parameter = $hwp.HParameterSet.HInsertText
    $hwp.HAction.GetDefault('InsertText', $parameter.HSet)
    $parameter.Text = $value
    [void]$hwp.HAction.Execute('InsertText', $parameter.HSet)
}

function Set-Character($hwp, [double]$points, [bool]$bold) {
    $shape = $hwp.HParameterSet.HCharShape
    $hwp.HAction.GetDefault('CharShape', $shape.HSet)
    $shape.FaceNameHangul = '함초롬바탕'
    $shape.FaceNameLatin = 'Arial'
    $shape.FaceNameHanja = '함초롬바탕'
    $shape.Height = [int]($points * 100)
    $shape.Bold = if ($bold) { 1 } else { 0 }
    [void]$hwp.HAction.Execute('CharShape', $shape.HSet)
}

function Set-Align($hwp, [string]$alignment) {
    switch ($alignment) {
        'center' { [void]$hwp.HAction.Run('ParagraphShapeAlignCenter') }
        'right' { [void]$hwp.HAction.Run('ParagraphShapeAlignRight') }
        default { [void]$hwp.HAction.Run('ParagraphShapeAlignLeft') }
    }
}

function New-Paragraph($hwp, [int]$count = 1) {
    foreach ($index in 1..$count) { [void]$hwp.HAction.Run('BreakPara') }
}

function Replace-All($hwp, [string]$oldValue, [string]$newValue) {
    [void]$hwp.HAction.Run('MoveDocBegin')
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

function Add-Cover($hwp) {
    Set-Align $hwp 'center'
    Set-Character $hwp 18 $false
    New-Paragraph $hwp 2
    Insert-Text $hwp '2026학년도'
    Set-Character $hwp 10 $false
    New-Paragraph $hwp 4
    Set-Character $hwp 30 $true
    Insert-Text $hwp '과정 중심 평가 계획'
    Set-Character $hwp 10 $false
    New-Paragraph $hwp 7
    Set-Character $hwp 23 $true
    Insert-Text $hwp '5학년 2학기'
    Set-Character $hwp 10 $false
    New-Paragraph $hwp 11
    Set-Character $hwp 17 $true
    Insert-Text $hwp '장 량 초 등 학 교'
    [void]$hwp.HAction.Run('BreakPage')
}

function Create-OperationTable($hwp, $items) {
    $rowCount = 1 + (3 * $items.Count)
    $totalCells = $rowCount * 8
    $writtenCells = 0
    $widths = @(10.0, 22.0, 20.0, 12.0, 21.0, 43.0, 8.0, 34.0)
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
    foreach ($index in 0..7) {
        $table.ColWidth.Item($index) = $hwp.MiliToHwpUnit($widths[$index])
    }
    foreach ($index in 0..($rowCount - 1)) {
        $table.RowHeight.Item($index) = $hwp.MiliToHwpUnit($(if ($index -eq 0) { 8.0 } else { 7.0 }))
    }
    if (-not $hwp.HAction.Execute('TableCreate', $table.HSet)) { throw 'TableCreate failed' }

    $headers = @('시기', '성취기준', '단원명', '평가 영역', '평가 요소', '수업·평가 방법, 연계의 주안점', '평가 기준', '내용')
    Set-Character $hwp 6.2 $true
    foreach ($header in $headers) {
        Set-Align $hwp 'center'
        Insert-Text $hwp $header
        $writtenCells++
        if ($writtenCells -lt $totalCells) {
            [void]$hwp.HAction.Run('TableRightCell')
        }
    }

    foreach ($item in $items) {
        $rows = @(
            @([string]$item.when, [string]$item.standard, [string]$item.unit, [string]$item.area, [string]$item.element, [string]$item.method, 'A', [string]$item.A),
            @('', '', '', '', '', '', 'B', [string]$item.B),
            @('', '', '', '', '', '', 'C', [string]$item.C)
        )
        foreach ($row in $rows) {
            for ($column = 0; $column -lt 8; $column++) {
                Set-Character $hwp 5.7 $false
                if ($column -in @(0, 3, 6)) { Set-Align $hwp 'center' } else { Set-Align $hwp 'left' }
                Insert-Text $hwp ([string]$row[$column])
                $writtenCells++
                if ($writtenCells -lt $totalCells) {
                    [void]$hwp.HAction.Run('TableRightCell')
                }
            }
        }
    }

    # Leave the final table cell before the next page break or inserted file.
    # Advancing right from the final cell appends rows and keeps all later
    # content nested inside this table.
    [void]$hwp.HAction.Run('Cancel')
    [void]$hwp.MovePos(3, 0, 0)
}

function Add-OperationSection($hwp, [string]$subject, $items, [bool]$first) {
    if (-not $first) { [void]$hwp.HAction.Run('BreakPage') }
    Set-Align $hwp 'center'
    Set-Character $hwp 15 $true
    Insert-Text $hwp ($subject + '과 교수학습 및 평가 운영계획')
    New-Paragraph $hwp
    Set-Character $hwp 10 $false
    Insert-Text $hwp '2026학년도 2학기                              5학년'
    New-Paragraph $hwp
    Set-Align $hwp 'left'
    Create-OperationTable $hwp $items
}

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    [void]$hwp.HAction.Run('MoveDocBegin')
    Add-Cover $hwp

    for ($index = 0; $index -lt $subjects.Count; $index++) {
        $subject = $subjects[$index]
        Add-OperationSection $hwp $subject $metadata.$subject ($index -eq 0)
    }

    [void]$hwp.HAction.Run('BreakPage')
    $insert = $hwp.HParameterSet.HInsertFile
    $hwp.HAction.GetDefault('InsertFile', $insert.HSet)
    $insert.FileName = $source
    $insert.KeepSection = 0
    $insert.KeepCharshape = 1
    $insert.KeepParashape = 1
    $insert.KeepStyle = 1
    if (-not $hwp.HAction.Execute('InsertFile', $insert.HSet)) { throw 'InsertFile failed' }

    $replacements = @(
        @('2025학년도', '2026학년도'),
        @('음악으로 세기고', '음각으로 새기고'),
        @('불교과 국가의 종교', '불교가 국가의 종교'),
        @('밤에서 불을 켜서', '밤에 불을 켜서'),
        @('간심', '관심'),
        @('더울 발전시킬', '더욱 발전시킬'),
        @('이를 이를 통해 추론할 수 있는', '이를 통해 추론할 수 있는'),
        @('가치를 인증 받고', '가치를 인정받고'),
        @('목반에 글자를', '목판에 글자를'),
        @('있었음을 할 수 있다', '있었음을 알 수 있다'),
        @('접 시', '접시'),
        @('대칭 도형', '대칭도형'),
        @('<벼타작.>', '<벼타작>'),
        @('생활 속 대상에서 도형(수학)을 찾을 수 있는가?', '수묵 담채화의 표현 방법을 활용하여 먹과 색의 농담을 나타낼 수 있는가?'),
        @('1번 질문에서 도형을 3개 찾았을 경우', '삼묵법·몰골법·구륵법을 적절히 활용하고 먹과 색의 농담을 풍부하게 표현한 경우'),
        @('1번 질문에서 도형을 2개만 찾았을 경우', '두 가지 이상의 표현 방법을 활용하고 먹과 색의 농담을 나타낸 경우'),
        @('1번 질문에서 도형을 1개만 찾았을 경우', '안내에 따라 한 가지 표현 방법과 먹의 농담을 부분적으로 나타낸 경우'),
        @('찾은 도형(수학)을 자세히 관찰하여 연결되어 있는 모양을 파악하였는가?', '붓을 누르는 힘과 먹물의 양을 조절하여 선의 굵기와 흐름에 변화를 주었는가?'),
        @('※ 평소에 무심코 봐 왔던 생활 속 대상을 집중하여 관심 있게 보면서 미적 대상으로 인식하는 데초점을 두어 평가하므로, 주제를 벗어나지 않는 범위에서 각자의 관점을 존중하여 정답으로 처리함.', '※ 붓의 힘과 먹물의 양을 조절하여 선의 굵기와 흐름을 자연스럽게 표현했는지 평가함.'),
        @('찾은 수학적 원리가 미술과 어떻게 융합되었는가를 이해하고 있는가?', '수묵 담채화의 재료와 용구를 바르게 사용하고 작품의 의도와 표현 특징을 설명할 수 있는가?'),
        @('※ 생활 속 대상에 들어 있는 다양한 수학적 원리가, 우리가 접하는 대상을 더 아름답고 조화롭게 만들고,우리의 삶을 여러 측면에서 더 풍요롭게 만든다는 내용이 들어가면 정답으로 처리함.', '※ 재료와 용구를 바르게 사용하고 작품에 활용한 삼묵법·몰골법·구륵법, 먹과 색의 농담, 선의 변화를 설명했는지 평가함.')
    )
    foreach ($pair in $replacements) {
        Replace-All $hwp ([string]$pair[0]) ([string]$pair[1])
    }

    [void]$hwp.HAction.Run('MoveDocBegin')
    try {
        $pageNumber = $hwp.HParameterSet.HPageNumPos
        $hwp.HAction.GetDefault('PageNumPos', $pageNumber.HSet)
        $pageNumber.DrawPos = 8
        $pageNumber.SideChar = 45
        $pageNumber.SuffixChar = 45
        [void]$hwp.HAction.Execute('PageNumPos', $pageNumber.HSet)
    } catch {}

    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'HWPX SaveAs failed' }
    if (-not $hwp.SaveAs($pdfOutput, 'PDF', '')) { throw 'PDF SaveAs failed' }
    Write-Output ('pages=' + $hwp.PageCount)
    Write-Output ('hwpx=' + $output)
    Write-Output ('pdf=' + $pdfOutput)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
