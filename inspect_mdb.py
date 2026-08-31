import pyodbc, sys
sys.stdout.reconfigure(encoding='utf-8')
p=r'C:\Schoolmaster 2026\suh_s.mdb'
c=pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+p)
cur=c.cursor()
for t in ['국어','사회','도덕','수학','과학','실과','체육','음악','미술','영어']:
    print('\n##',t)
    cols=[(x.column_name,x.type_name,x.column_size) for x in cur.columns(table=t)]
    print(cols)
    rows=cur.execute(f'SELECT TOP 5 * FROM [{t}]').fetchall()
    for row in rows: print(tuple(row))
