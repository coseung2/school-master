import sys
from html.parser import HTMLParser
class P(HTMLParser):
 def __init__(self): super().__init__(); self.in_table=0; self.in_tr=False; self.in_td=False; self.cell=''; self.row=[]; self.rows=[]; self.tidx=-1
 def handle_starttag(self,t,a):
  if t=='table': self.in_table+=1; self.tidx+=1
  elif t=='tr' and self.in_table: self.in_tr=True; self.row=[]
  elif t=='td' and self.in_tr: self.in_td=True; self.cell=''
 def handle_endtag(self,t):
  if t=='td' and self.in_td: self.row.append(' '.join(self.cell.split())); self.in_td=False
  elif t=='tr' and self.in_tr: self.rows.append((self.tidx,self.row)); self.in_tr=False
  elif t=='table' and self.in_table: self.in_table-=1
 def handle_data(self,d):
  if self.in_td:self.cell+=d
for fn in sys.argv[1:]:
 print('### FILE',fn)
 p=P(); p.feed(open(fn,encoding='utf-8').read())
 for ti,row in p.rows:
  print(f'T{ti}: '+' | '.join(row))
