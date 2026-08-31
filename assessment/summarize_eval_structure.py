from __future__ import annotations

import json
import sys
from pathlib import Path


for name in sys.argv[1:]:
    data = json.loads(Path(name).read_text(encoding="utf-8"))
    print(f"### {name}")
    for item in data["paragraphs"]:
        if not item["text"] and not item["controls"]:
            continue
        controls = ",".join(item["controls"])
        print(f"{item['index']:04d}\t{controls:20s}\t{item['text']}")
