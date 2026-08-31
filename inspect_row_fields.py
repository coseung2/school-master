import pyodbc,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
p=r'C:\Schoolmaster 2026\suh5.mdb'; c=pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+p); cur=c.cursor()
for t,sno in [('국어',2011408),('도덕',2040605),('수학A',2041010),('과학A',2051010),('실과A',2051005),('체육A',2050508),('음악A',2060609),('미술A',2060505),('영어A',2070605),('사회A',2011010)]:
 cols=[x.column_name for x in cur.columns(table=t)]
 row=cur.execute(f"SELECT TOP 1 * FROM [{t}] WHERE sno=? AND ahak='2'",(sno,)).fetchone()
 print('\n##',t,sno)
 if row:
  for i,(col,v) in enumerate(zip(cols,row)): print(i,col,repr(str(v)[:500] if v is not None else v))
 else: print('not found')
