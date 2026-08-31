from pathlib import Path
from lxml import etree
from collections import Counter,defaultdict
import sys,re,json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
root=Path(r'C:\Schoolmaster 2026\suhdb2')
files=list(root.glob('*/*a'))
print('a files',len(files))
cnt=Counter(); examples=defaultdict(list); semcnt=Counter();
for i,p in enumerate(files):
  try: data=p.read_bytes(); rt=etree.fromstring(data)
  except Exception as e: continue
  text=' '.join(x.strip() for x in rt.xpath('.//CHAR/text()') if x.strip())
  # subject from first occurrence of 과목 <subject>
  m=re.search(r'과목\s+([^\s]+)',text)
  subj=m.group(1) if m else '?'
  cnt[subj]+=1
  if len(examples[subj])<3: examples[subj].append((str(p),text[:250]))
  sem='2학기' if '2학기' in text else ('1학기' if '1학기' in text else '?')
  semcnt[(subj,sem)]+=1
print('subjects',cnt)
print('sem',semcnt)
for s,es in examples.items():
 print('\n##',s)
 for p,t in es: print(p,'\n ',t)
