from __future__ import annotations

import sys
from pathlib import Path

import fitz


source = Path(sys.argv[1])
output = Path(sys.argv[2])
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 100
output.mkdir(parents=True, exist_ok=True)

document = fitz.open(source)
matrix = fitz.Matrix(dpi / 72, dpi / 72)
for index, page in enumerate(document):
    pixmap = page.get_pixmap(matrix=matrix, alpha=False)
    pixmap.save(output / f"page-{index + 1:03d}.png")
print(f"rendered={len(document)}")
