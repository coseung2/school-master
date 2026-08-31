from pathlib import Path
import sys,re
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
root=Path(r'C:\Schoolmaster 2026\suhdb2\5')
terms=['국어','사회','도덕','수학','과학','실과','체육','음악','미술','영어']
for term in terms:
 print('\n##',term)
 n=0
 for p in root.glob('*a'):
  try:s=p.read_text(encoding='utf-8',errors='ignore')
  except:continue
  if term in s:
   n+=1
   if n<=20:
    i=s.find(term); print(p.name,s[max(0,i-100):i+250].replace('><','> <'))
 print('count',n)
