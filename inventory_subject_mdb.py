from pathlib import Path
import pyodbc,sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
root=Path(r'C:\Schoolmaster 2026')
for p in sorted(root.glob('*.mdb')):
 try: c=pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+str(p), timeout=3)
 except: continue
 cur=c.cursor(); tabs=[x.table_name for x in cur.tables(tableType='TABLE')]
 subs=[t for t in tabs if any(k in t for k in ['국어','사회','도덕','수학','과학','실과','체육','음악','미술','영어'])]
 if not subs: continue
 print('\n##',p.name)
 for t in subs:
  try:
   n=cur.execute(f'SELECT COUNT(*) FROM [{t}]').fetchone()[0]
   cols=[x.column_name for x in cur.columns(table=t)]
   # get representative first row values
   row=cur.execute(f'SELECT TOP 1 * FROM [{t}]').fetchone()
   vals=' | '.join(str(v).replace('\n',' ')[:100] for v in (row or []) if v is not None)
   print(t,n,'cols',len(cols),'row',vals[:300])
  except Exception as e: print(t,'ERR',e)
