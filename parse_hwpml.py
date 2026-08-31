from pathlib import Path
from lxml import etree
import re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
root=Path(r'C:\Schoolmaster 2026\hwp2')
for p in sorted(root.glob('*')):
    if p.is_file():
        try: txt=p.read_text(encoding='utf-8')
        except Exception as e: print(p,e); continue
        try: rt=etree.fromstring(txt.encode())
        except Exception as e: print(p,'XMLERR',e); continue
        chars=rt.xpath('.//CHAR/text()')
        # collapse duplicate structural text only preserving order
        out=' '.join(x.strip() for x in chars if x.strip())
        print(f'## {p.name}\n{out[:1500]}\n')
