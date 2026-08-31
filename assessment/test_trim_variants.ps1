$ErrorActionPreference = 'Stop'

$source = (Resolve-Path -LiteralPath $args[0]).Path
$outputDirectory = [System.IO.Path]::GetFullPath($args[1])
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null

function Save-Variant([string]$name, [scriptblock]$edit) {
    $hwp = New-Object -ComObject HWPFrame.HwpObject
    try {
        $hwp.XHwpWindows.Item(0).Visible = $false
        $hwp.SetMessageBoxMode(0x20000)
        if (-not $hwp.Open($source, '', '')) { throw 'Open failed' }
        Write-Output ($name + ':before=' + $hwp.PageCount)
        & $edit $hwp
        Write-Output ($name + ':after=' + $hwp.PageCount)
        $target = Join-Path $outputDirectory ($name + '.hwpx')
        if (-not $hwp.SaveAs($target, 'HWPX', '')) { throw 'Save failed' }
        Write-Output ($name + ':saved=' + $target)
    } finally {
        try { $hwp.Clear(1) | Out-Null } catch {}
        try { $hwp.Quit() | Out-Null } catch {}
    }
}

Save-Variant 'move-select-end' {
    param($hwp)
    Write-Output ('doc-begin=' + $hwp.HAction.Run('MoveDocBegin'))
    Write-Output ('page-down=' + $hwp.HAction.Run('MovePageDown'))
    Write-Output ('page-begin=' + $hwp.HAction.Run('MovePageBegin'))
    Write-Output ('select-end=' + $hwp.HAction.Run('MoveSelDocEnd'))
    Write-Output ('delete=' + $hwp.HAction.Run('Delete'))
}

Save-Variant 'goto-select-end' {
    param($hwp)
    [void]$hwp.HAction.Run('MoveDocBegin')
    $goto = $hwp.HParameterSet.HGotoE
    $hwp.HAction.GetDefault('Goto', $goto.HSet)
    $goto.SetSelectionIndex = 1
    $goto.HSet.SetItem('DialogResult', 2)
    Write-Output ('goto=' + $hwp.HAction.Execute('Goto', $goto.HSet))
    Write-Output ('page-begin=' + $hwp.HAction.Run('MovePageBegin'))
    Write-Output ('select-end=' + $hwp.HAction.Run('MoveSelDocEnd'))
    Write-Output ('delete=' + $hwp.HAction.Run('Delete'))
}

Save-Variant 'six-arg-select' {
    param($hwp)
    [void]$hwp.HAction.Run('MoveDocBegin')
    [void]$hwp.HAction.Run('MovePageDown')
    [void]$hwp.HAction.Run('MovePageBegin')
    $startList = 0
    $startPara = 0
    $startPos = 0
    [void]$hwp.GetPos([ref]$startList, [ref]$startPara, [ref]$startPos)
    [void]$hwp.HAction.Run('MoveDocEnd')
    $endList = 0
    $endPara = 0
    $endPos = 0
    [void]$hwp.GetPos([ref]$endList, [ref]$endPara, [ref]$endPos)
    Write-Output ('start=' + $startList + ',' + $startPara + ',' + $startPos)
    Write-Output ('end=' + $endList + ',' + $endPara + ',' + $endPos)
    Write-Output ('select=' + $hwp.SelectText($startList, $startPara, $startPos, $endList, $endPara, $endPos))
    Write-Output ('delete=' + $hwp.HAction.Run('Delete'))
}
