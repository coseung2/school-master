$path='C:\Schoolmaster 2026\suhdb2\5\50020406190805155505'
$h=New-Object -ComObject HWPFrame.HwpObject
$h.XHwpWindows.Item(0).Visible=$false|Out-Null
$ok=$h.Open($path,'HWP','forceopen:true'); Write-Output ('open='+$ok)
$s=$h.SaveAs('C:\Users\user\Desktop\test_base.hwpx','HWPX',''); Write-Output ('save='+$s)
$h.Quit()|Out-Null
