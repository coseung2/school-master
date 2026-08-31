import pyodbc,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
p=r'C:\Schoolmaster 2026\suh5.mdb'
c=pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+p); cur=c.cursor()
for t in ['국어','사회A','도덕']:
 print(t,[x.column_name for x in cur.columns(table=t)])
 try: print(cur.execute(f'SELECT ahak,COUNT(*) FROM [{t}] GROUP BY ahak').fetchall())
 except Exception as e: print('ERR',e)
