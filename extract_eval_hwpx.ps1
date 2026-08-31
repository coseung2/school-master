$ErrorActionPreference = 'Stop'

$db = 'C:\Schoolmaster 2026\suh5.mdb'
$srcRoot = 'C:\Schoolmaster 2026\suhdb2\5'
$desktop = [Environment]::GetFolderPath('Desktop')
$outRoot = Join-Path $desktop '스쿨마스터_5학년_2학기_수행평가_예시자료'
$subjects = [ordered]@{
    '국어' = '국어'
    '사회' = '사회A'
    '도덕' = '도덕'
    '수학' = '수학A'
    '과학' = '과학A'
    '실과' = '실과A'
    '체육' = '체육A'
    '음악' = '음악A'
    '미술' = '미술A'
    '영어' = '영어A'
}

New-Item -ItemType Directory -Path $outRoot -Force | Out-Null
$cn = New-Object System.Data.OleDb.OleDbConnection
$cn.ConnectionString = "Provider=Microsoft.ACE.OLEDB.12.0;Data Source=$db;Persist Security Info=False;"
$cn.Open()

$hwp = New-Object -ComObject HWPFrame.HwpObject
$hwp.XHwpWindows.Item(0).Visible = $false
try { [void]$hwp.RegisterModule('FilePathCheckDLL','FilePathCheckerModuleExample') } catch {}
try { $hwp.SetMessageBoxMode(0) } catch {}

$manifest = New-Object System.Collections.Generic.List[object]
foreach ($subject in $subjects.Keys) {
    $table = $subjects[$subject]
    $subjectDir = Join-Path $outRoot $subject
    New-Item -ItemType Directory -Path $subjectDir -Force | Out-Null
    $cmd = $cn.CreateCommand()
    $cmd.CommandText = "SELECT sno,sdan,sp1 FROM [$table]"
    $rd = $cmd.ExecuteReader()
    $n = 0
    while ($rd.Read()) {
        if (([string]$rd.GetValue(0)).Trim() -eq '') { continue }
        # ahak is encoded in the sno prefix for these legacy tables: 20xxxxxx = 2nd semester.
        $sno = [string]$rd.GetValue(0)
        if (-not $sno.StartsWith('2')) { continue }
        $id = ([string]$rd.GetValue(2)).Trim()
        if ($id -eq '') { continue }
        # HWPML 변환본을 우선 사용하면 구형 HWP 보안 확인창과 복구 대화상자를 피할 수 있다.
        $src = Join-Path $srcRoot ($id + 'a')
        if (-not (Test-Path -LiteralPath $src)) {
            $src = Join-Path $srcRoot $id
        }
        if (-not (Test-Path -LiteralPath $src)) {
            $manifest.Add([pscustomobject]@{Subject=$subject;Sno=$sno;SourceId=$id;Status='원본 없음';Output=''})
            continue
        }
        $n++
        $out = Join-Path $subjectDir ('{0:D2}_{1}.hwpx' -f $n,$id)
        try {
            if ($src.EndsWith('a')) {
                [void]$hwp.Open($src,'HWPML2X','forceopen:true')
            } else {
                [void]$hwp.Open($src,'HWP','forceopen:true')
            }
            [void]$hwp.SaveAs($out,'HWPX','')
            $manifest.Add([pscustomobject]@{Subject=$subject;Sno=$sno;SourceId=$id;Status='변환 완료';Output=$out})
        } catch {
            $manifest.Add([pscustomobject]@{Subject=$subject;Sno=$sno;SourceId=$id;Status=('오류: ' + $_.Exception.Message);Output=$out})
        } finally {
            try { [void]$hwp.Clear(1) } catch {}
        }
    }
    $rd.Close()
}
$cn.Close()
try { $hwp.Quit() } catch {}

$manifest | Export-Csv -LiteralPath (Join-Path $outRoot 'manifest.csv') -NoTypeInformation -Encoding UTF8
$manifest | Group-Object Subject | Select-Object Name,Count | Format-Table -AutoSize
