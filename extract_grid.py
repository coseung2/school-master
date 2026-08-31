import sys,zipfile,xml.etree.ElementTree as E
def ln(t): return t.split('}')[-1]
def tx(e): return ''.join(x.text or '' for x in e.iter() if ln(x.tag)=='t').replace('\n',' / ')
for path in sys.argv[1:]:
 print('### FILE',path)
 with zipfile.ZipFile(path) as z:
  root=E.fromstring(z.read('Contents/section0.xml'))
  for ti,tbl in enumerate([e for e in root.iter() if ln(e.tag)=='tbl']):
   cells=[]
   for tc in [e for e in tbl.iter() if ln(e.tag)=='tc']:
    a=next((e for e in tc if ln(e.tag)=='cellAddr'),None); s=next((e for e in tc if ln(e.tag)=='cellSpan'),None)
    if a is None: continue
    cells.append((int(a.attrib.get('rowAddr',0)),int(a.attrib.get('colAddr',0)),int(s.attrib.get('rowSpan',1)),int(s.attrib.get('colSpan',1)),tx(tc)))
   if not cells: continue
   maxr=max(r+rs for r,c,rs,cs,t in cells); maxc=max(c+cs for r,c,rs,cs,t in cells)
   g=[['']*maxc for _ in range(maxr)]
   for r,c,rs,cs,t in cells:
    for rr in range(r,min(maxr,r+rs)):
     for cc in range(c,min(maxc,c+cs)):
      if not g[rr][cc]:g[rr][cc]=t
   # Print only tables with schedule headers or creative rows, and rows with text
   if maxc>=7 and any('과목명' in x for row in g for x in row):
    print(f'## TABLE {ti} grid {maxr}x{maxc}')
    for row in g:
     if any(row): print(' | '.join(row))
