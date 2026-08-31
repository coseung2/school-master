import sys
from html.parser import HTMLParser
class P(HTMLParser):
 def __init__(self):super().__init__();self.in_table=0;self.table=[];self.rows=[];self.cur=[];self.in_td=False;self.buf='';self.attr={}
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='table':self.in_table+=1;self.rows=[]
  elif t=='tr' and self.in_table:self.cur=[]
  elif t=='td' and self.in_table:self.in_td=True;self.buf='';self.attr=d
 def handle_data(self,d):
  if self.in_td:self.buf+=d
 def handle_endtag(self,t):
  if t=='td' and self.in_td:self.cur.append((self.buf,' '.join(self.buf.split()),int(self.attr.get('rowspan','1')),int(self.attr.get('colspan','1'))));self.in_td=False
  elif t=='tr' and self.in_table:self.rows.append(self.cur)
  elif t=='table' and self.in_table:
   self.table.append(self.rows);self.in_table-=1
for fn in sys.argv[1:]:
 p=P();p.feed(open(fn,encoding='utf-8').read());print('### FILE',fn)
 for ti,rows in enumerate(p.table):
  grid=[]
  for ri,cells in enumerate(rows):
   while len(grid)<=ri:grid.append([])
   ci=0
   for raw,s,rs,cs in cells:
    while ci<len(grid[ri]) and grid[ri][ci]:ci+=1
    while len(grid[ri])<ci+cs:grid[ri].append('')
    for rr in range(ri,ri+rs):
     while len(grid)<=rr:grid.append([])
     while len(grid[rr])<ci+cs:grid[rr].append('')
     for cc in range(ci,ci+cs):
      if not grid[rr][cc]:grid[rr][cc]=s
    ci+=cs
  print(f'## TABLE {ti} {len(grid)}x{max(map(len,grid),default=0)}')
  for row in grid:print(' | '.join(row))
