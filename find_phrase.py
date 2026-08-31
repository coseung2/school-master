import pyodbc,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
p=r'C:\Schoolmaster 2026\suh5.mdb'; c=pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+p); cur=c.cursor()
for t in [x.table_name for x in cur.tables(tableType='TABLE')]:
 try:
  cols=[x.column_name for x in cur.columns(table=t)]
  rows=cur.execute(f'SELECT * FROM [{t}]').fetchall()
 except: continue
 for i,row in enumerate(rows):
  s=' | '.join(str(v) for v in row if v is not None)
  if any(k in s for k in ['인권을','작품에 대한 의견을','환경 위기','학급 공동체']):
   print(t,i,s[:1000])
