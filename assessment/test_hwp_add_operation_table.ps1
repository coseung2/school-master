$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $args[0]).Path
$output = [System.IO.Path]::GetFullPath($args[1])

$hwp = New-Object -ComObject HWPFrame.HwpObject
try {
    $hwp.XHwpWindows.Item(0).Visible = $false
    $hwp.SetMessageBoxMode(0x20000)
    if (-not $hwp.Open($source, '', '')) { throw 'open failed' }
    $hwp.MovePos(2, 0, 0) | Out-Null
    $hwp.HAction.Run('BreakPage') | Out-Null
    $hwp.HAction.Run('InsertText') | Out-Null
    $text = $hwp.HParameterSet.HInsertText
    $hwp.HAction.GetDefault('InsertText', $text.HSet)
    $text.Text = "사회과 교수학습 및 평가 운영계획`r`n2026학년도 2학기 | 5학년`r`n시기 | 성취기준 | 단원명 | 평가 영역 | 평가 요소 | 수업·평가 방법, 연계의 주안점 | 평가 기준"
    $hwp.HAction.Execute('InsertText', $text.HSet) | Out-Null
    if (-not $hwp.SaveAs($output, 'HWPX', '')) { throw 'save failed' }
    Write-Output ('pages=' + $hwp.PageCount)
} finally {
    try { $hwp.Clear(1) | Out-Null } catch {}
    try { $hwp.Quit() | Out-Null } catch {}
}
