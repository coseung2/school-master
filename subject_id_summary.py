import pyodbc,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
p=r'C:\Schoolmaster 2026\suh5.mdb'; c=pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+p); cur=c.cursor()
targets=['국어','사회','도덕','수학','과학','실과','체육','음악','미술','영어']
tabs=[x.table_name for x in cur.tables(tableType='TABLE')]
for base in targets:
 ts=[base] if base in tabs else sorted([t for t in tabs if t.startswith(base)])
 print('\n'+base)
 for t in ts:
  rows=cur.execute(f"SELECT sno,prim,sp1 FROM [{t}] WHERE ahak='2'").fetchall()
  print(t,len(rows),';'.join(f'{r.sno}:{r.prim}:{r.sp1}' for r in rows))
