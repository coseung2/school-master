from __future__ import annotations

import sys
from pathlib import Path

import fitz


def main() -> None:
    operations = Path(sys.argv[1])
    body = Path(sys.argv[2])
    output = Path(sys.argv[3])

    document = fitz.open()
    with fitz.open(operations) as source:
        document.insert_pdf(source)
    with fitz.open(body) as source:
        document.insert_pdf(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output, garbage=4, deflate=True)
    print(f"pages={len(document)} output={output}")


if __name__ == "__main__":
    main()
