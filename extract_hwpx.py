import sys, zipfile, xml.etree.ElementTree as E

def lname(tag):
    return tag.split('}')[-1]

def text(el):
    # Preserve line breaks from individual paragraphs within cells
    vals=[]
    for x in el.iter():
        if lname(x.tag)=='t' and x.text:
            vals.append(x.text)
    return ''.join(vals)

for path in sys.argv[1:]:
    print('\n### FILE',path)
    with zipfile.ZipFile(path) as z:
        secs=[n for n in z.namelist() if n.startswith('Contents/section') and n.endswith('.xml')]
        for sn in secs:
            root=E.fromstring(z.read(sn)); print('##',sn)
            for i,tbl in enumerate([e for e in root.iter() if lname(e.tag)=='tbl']):
                print(f'### TABLE {i}')
                for tr in [e for e in tbl.iter() if lname(e.tag)=='tr']:
                    cells=[text(tc).replace('\n',' / ') for tc in tr if lname(tc.tag)=='tc']
                    print(' | '.join(cells))
