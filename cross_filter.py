import sys,zipfile,xml.etree.ElementTree as E
def ln(t):return t.split('}')[-1]
def tx(e):return ''.join(x.text or '' for x in e.iter() if ln(x.tag)=='t').replace('\n',' / ')
for path in sys.argv[1:]:
 print('### FILE',path)
 with zipfile.ZipFile(path) as z:
  root=E.fromstring(z.read('Contents/section0.xml'))
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
    s=' | '.join(row)
    if '【' in s or '[' in s: print(f'T{ti}: {s}')
