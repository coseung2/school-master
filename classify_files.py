import pyodbc,sys,re
from pathlib import Path
from collections import defaultdict,Counter
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
p='C:\\Schoolmaster 2026\\suh5.mdb'; c=pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+p); cur=c.cursor()
mp=defaultdict(list)
for t in [x.table_name for x in cur.tables(tableType='TABLE')]:
 try:
  cols=[x.column_name for x in cur.columns(table=t)]
  if 'sp1' not in cols: continue
  for row in cur.execute(f'SELECT sno,ahak,prim,sp1 FROM [{t}]').fetchall():
   if row.sp1: mp[str(row.sp1)].append((t,row.sno,row.ahak,row.prim))
 except:continue
root=Path(r'C:\Schoolmaster 2026\suhdb2\5')
files=[p.name for p in root.iterdir() if p.is_file() and p.name.endswith('a')]
print('db IDs',len(mp),'files',len(files))
un=Counter(); tb=Counter(); ex=defaultdict(list)
for n in files:
 id=n[:-1]; refs=mp.get(id)
 if refs:
  for t,s,a,pr in refs: tb[(t,a)]+=1; ex[(t,a)].append((id,s,pr))
 else: un[id[:4]]+=1
print('table/sem counts')
for k,v in sorted(tb.items()): print(k,v)
print('unmapped prefixes',un)
for k,e in sorted(ex.items()):
 print('\n##',k,'n=',len(e)); print(';'.join(f'{id}:{s}:{pr}' for id,s,pr in e[:10]))
