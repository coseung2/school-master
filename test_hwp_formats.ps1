$path='C:\Schoolmaster 2026\hwp2\수행평가_100.hwp'
$formats=@('','HWP','HWPML','HWPML2X','HWPML2','XML','HWPX')
foreach($fmt in $formats){
 $h=New-Object -ComObject HWPFrame.HwpObject
 try{$h.XHwpWindows.Item(0).Visible=$false|Out-Null}catch{}
 $ok=$h.Open($path,$fmt,'forceopen:true'); Write-Output ('fmt=['+$fmt+'] open='+$ok)
 $out='C:\Users\user\Desktop\school master\fmt_'+($formats.IndexOf($fmt))+'.hwpx';
 try{$s=$h.SaveAs($out,'HWPX',''); Write-Output (' save='+$s)}catch{Write-Output (' saveerr='+$_.Exception.Message)}
 $h.Quit()|Out-Null
}
