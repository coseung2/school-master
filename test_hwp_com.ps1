$ErrorActionPreference='Continue'
$h=New-Object -ComObject HWPFrame.HwpObject
Write-Output ('obj='+$h)
$h.XHwpWindows.Item(0).Visible=$false | Out-Null
$r=$h.RegisterModule('FilePathCheckDLL','FilePathCheckerModuleExample'); Write-Output ('register='+$r)
$ok=$h.Open('C:\Schoolmaster 2026\hwp2\수행평가_100.hwp','HWPML',''); Write-Output ('open='+$ok)
$s=$h.SaveAs('C:\Users\user\Desktop\school master\test_out.hwpx','HWPX',''); Write-Output ('save='+$s)
$h.Quit() | Out-Null
