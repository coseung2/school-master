import sys,zipfile,xml.etree.ElementTree as E,collections
def ln(t):return t.split('}')[-1]
def tx(e):return ''.join(x.text or '' for x in e.iter() if ln(x.tag)=='t')
for path in sys.argv[1:]:
 with zipfile.ZipFile(path) as z:
  root=E.fromstring(z.read('Contents/section0.xml')); counts=collections.Counter(); details=collections.defaultdict(list)
  for ti,tbl in enumerate([e for e in root.iter() if ln(e.tag)=='tbl']):
   cells=[]
   for tc in [e for e in tbl.iter() if ln(e.tag)=='tc']:
    a=next((e for e in tc if ln(e.tag)=='cellAddr'),None);s=next((e for e in tc if ln(e.tag)=='cellSpan'),None)
    if a is None:continue
    cells.append((int(a.attrib.get('rowAddr',0)),int(a.attrib.get('colAddr',0)),int(s.attrib.get('rowSpan',1)),int(s.attrib.get('colSpan',1)),tx(tc)))
   if not cells:continue
   mr=max(r+rs for r,c,rs,cs,t in cells);mc=max(c+cs for r,c,rs,cs,t in cells);g=[['']*mc for _ in range(mr)]
   for r,c,rs,cs,t in cells:
    for rr in range(r,min(mr,r+rs)):
     for cc in range(c,min(mc,c+cs)):
      if not g[rr][cc]:g[rr][cc]=t
   if not any('과목명' in x for row in g for x in row):continue
   for row in g:
    cat=row[3] if len(row)>3 else ''
    if cat in ('자율·자치활동','동아리활동','진로활동'):
      counts[cat]+=1; details[cat].append((row[0],row[1],row[2],row[6],row[4]))
  print(path,dict(counts))
  for k,v in details.items(): print(k); print('\n'.join(map(str,v)))
