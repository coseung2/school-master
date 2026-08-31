from pathlib import Path
import pyodbc,sys,re
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
root=Path(r'C:\Schoolmaster 2026')
for p in sorted(root.glob('*.mdb')):
  try: c=pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+str(p), timeout=5)
  except Exception as e: print('ERR',p.name,e); continue
  cur=c.cursor(); tabs=[x.table_name for x in cur.tables(tableType='TABLE')]
  print(f'## {p.name} ({len(tabs)} tables) {tabs[:30]}')
  for t in tabs:
    try:
      cols=[x.column_name for x in cur.columns(table=t)]
      # inspect text-like columns only
      textcols=[x for x in cols if x]
      if not textcols: continue
      rows=cur.execute(f'SELECT TOP 200 * FROM [{t}]').fetchall()
    except Exception as e: continue
    hits=[]
    for row in rows:
      s=' | '.join(str(v) for v in row if v is not None)
      if any(k in s for k in ['2학기','5학년','검정','수행평가','국어','사회','도덕','과학','수학','영어','체육','음악','미술','실과']): hits.append(s[:500])
    if hits:
      print('TABLE',t,'cols',cols,'hits',len(hits))
      for h in hits[:5]: print(' ',h)
