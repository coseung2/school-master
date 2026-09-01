$ErrorActionPreference = 'Stop'

$operationsDir = (Resolve-Path -LiteralPath $args[0]).Path
$source = (Resolve-Path -LiteralPath $args[1]).Path
$output = [System.IO.Path]::GetFullPath($args[2])
$pdfOutput = [System.IO.Path]::GetFullPath($args[3])

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

$images = Get-ChildItem -LiteralPath $operationsDir -Filter 'page-*.png' -File | Sort-Object Name
if ($images.Count -ne 6) { throw "Expected six operation-plan images, found $($images.Count)" }

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    try { [void]$hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModuleExample') } catch {}
    $hwp.SetMessageBoxMode(0)
    Add-Cover $hwp

    foreach ($image in $images) {
        [void]$hwp.MovePos(3, 0, 0)
        [void]$hwp.HAction.Run('BreakPage')
        Set-Align $hwp 'center'
        $inserted = $hwp.InsertPicture($image.FullName, $true, 1, $false, $false, 0, 166.0, 234.5)
        if ($null -eq $inserted) { throw "InsertPicture failed: $($image.FullName)" }
    }

    [void]$hwp.MovePos(3, 0, 0)
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
        @('찾은 수학적 원리가 미술과 어떻게 융합되었는가를 이해하고 있는가?', '수묵 담채화의 재료와 용구를 바르게 사용하고 작품의 의도와 표현 특징을 설명할 수 있는가?')
    )
    foreach ($pair in $replacements) { Replace-All $hwp ([string]$pair[0]) ([string]$pair[1]) }

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
