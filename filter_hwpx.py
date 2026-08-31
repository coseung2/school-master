import sys,zipfile,xml.etree.ElementTree as E
def lname(t): return t.split('}')[-1]
def txt(e): return ''.join(x.text or '' for x in e.iter() if lname(x.tag)=='t')
keys=['자율·자치','동아리','진로','행사','봉사','학교폭력','교통안전','민주시민','생명존중','장애인식','다문화','통일','독도','경제･금융','경제·금융','환경','보건교육','성교육','성폭력','양성평등','인권','재난','안전','약물','인터넷','정보통신','폭력예방','가정폭력','아동학대','흡연','음주','응급처치','식생활','영양','재난','직업','꿈']
for path in sys.argv[1:]:
 print('\n### FILE',path)
 with zipfile.ZipFile(path) as z:
  for sn in [n for n in z.namelist() if n.startswith('Contents/section') and n.endswith('.xml')]:
   root=E.fromstring(z.read(sn))
   for i,tbl in enumerate([e for e in root.iter() if lname(e.tag)=='tbl']):
    for tr in [e for e in tbl.iter() if lname(e.tag)=='tr']:
     cells=[txt(tc).replace('\n',' / ') for tc in tr if lname(tc.tag)=='tc']; s=' | '.join(cells)
     if any(k in s for k in keys): print(f'T{i}: {s}')
