import pyodbc,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
for fn in ['suh1.mdb','suh2.mdb','suh3.mdb','suh4.mdb','suh5.mdb','suh6.mdb']:
 p='C:\\Schoolmaster 2026\\'+fn
 try:c=pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+p);cur=c.cursor()
 except Exception as e: print(fn,e);continue
 tabs=[x.table_name for x in cur.tables(tableType='TABLE')]; print('\n##',fn,[t for t in tabs if any(t.startswith(s) for s in ['실과','체육'])])
 for t in tabs:
  if any(t.startswith(s) for s in ['실과','체육']):
   try: print(t,cur.execute(f'SELECT ahak,COUNT(*) FROM [{t}] GROUP BY ahak').fetchall())
   except Exception as e:print(t,e)
