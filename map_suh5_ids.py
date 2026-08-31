import pyodbc,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
p=r'C:\Schoolmaster 2026\suh5.mdb'; c=pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+p); cur=c.cursor()
subs=['국어','사회A','사회B','사회C','사회D','사회E','사회F','사회G','사회H','도덕','수학A','수학B','수학C','수학D','수학E','수학F','수학G','수학H','수학I','과학A','과학B','과학C','과학D','과학E','실과A','실과B','실과C','실과D','실과E','실과F','실과G','실과H','실과I','체육A','체육B','체육C','체육D','체육E','체육F','체육G','체육H','체육I','체육J','음악A','음악B','음악C','음악D','음악E','음악F','음악G','음악H','음악I','음악J','미술A','미술B','미술C','미술D','미술E','미술F','미술G','미술H','미술I','미술J','영어A','영어B','영어C','영어D','영어E','영어F','영어G','영어H','영어I']
for t in subs:
 try: rows=cur.execute(f"SELECT sno,sdan,acha,prim,sp1 FROM [{t}] WHERE ahak='2'").fetchall()
 except Exception: continue
 print('\n##',t)
 for r in rows: print(f'{r.sno}\t{r.sdan}\t{r.acha}\tprim={r.prim}\t{r.sp1}')
