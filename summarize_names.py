from pathlib import Path
from collections import Counter
import sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path(r'C:\Schoolmaster 2026\suhdb2\5')
names=[p.name for p in root.iterdir() if p.is_file() and not p.name.endswith('a')]
print('base',len(names))
for n,c in Counter(x[:4] for x in names).most_common(): print(n,c)
print('5th char',Counter(x[3] for x in names).most_common())
print('first 3',Counter(x[:3] for x in names).most_common())
