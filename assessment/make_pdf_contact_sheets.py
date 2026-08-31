from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


source = Path(sys.argv[1])
output = Path(sys.argv[2])
columns = int(sys.argv[3]) if len(sys.argv) > 3 else 3
rows = int(sys.argv[4]) if len(sys.argv) > 4 else 3

paths = sorted(source.glob("page-*.png"))
if not paths:
    raise SystemExit(f"No rendered pages found in {source}")

with Image.open(paths[0]) as sample:
    page_ratio = sample.height / sample.width

thumb_width = 420
thumb_height = round(thumb_width * page_ratio)
label_height = 34
gap = 18
margin = 24
sheet_width = margin * 2 + columns * thumb_width + (columns - 1) * gap
sheet_height = margin * 2 + rows * (thumb_height + label_height) + (rows - 1) * gap
per_sheet = columns * rows
font = ImageFont.load_default(size=20)

output.mkdir(parents=True, exist_ok=True)
for sheet_index in range(math.ceil(len(paths) / per_sheet)):
    sheet = Image.new("RGB", (sheet_width, sheet_height), "#d8d8d8")
    draw = ImageDraw.Draw(sheet)
    batch = paths[sheet_index * per_sheet : (sheet_index + 1) * per_sheet]
    for item_index, path in enumerate(batch):
        row, column = divmod(item_index, columns)
        x = margin + column * (thumb_width + gap)
        y = margin + row * (thumb_height + label_height + gap)
        with Image.open(path) as page:
            page.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            px = x + (thumb_width - page.width) // 2
            py = y + label_height + (thumb_height - page.height) // 2
            sheet.paste(page.convert("RGB"), (px, py))
        label = path.stem.replace("page-", "Page ")
        draw.text((x, y), label, fill="black", font=font)
    target = output / f"contact-{sheet_index + 1:02d}.jpg"
    sheet.save(target, quality=92)

print(f"sheets={math.ceil(len(paths) / per_sheet)} pages={len(paths)}")
