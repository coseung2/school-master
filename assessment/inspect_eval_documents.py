from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(node: ET.Element) -> str:
    return "".join((part.text or "") for part in node.iter() if local(part.tag) == "t")


def inspect(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("Contents/section0.xml"))

    body = list(root)
    paragraphs = [node for node in body if local(node.tag) == "p"]
    controls: list[dict[str, object]] = []
    for index, paragraph in enumerate(paragraphs):
        kinds = [local(node.tag) for node in paragraph.iter() if local(node.tag) in {"tbl", "pic", "rect", "ellipse", "container"}]
        controls.append(
            {
                "index": index,
                "id": paragraph.attrib.get("id"),
                "paraPrIDRef": paragraph.attrib.get("paraPrIDRef"),
                "styleIDRef": paragraph.attrib.get("styleIDRef"),
                "text": re.sub(r"\s+", " ", text_of(paragraph)).strip()[:180],
                "controls": kinds,
            }
        )

    return {
        "file": str(path),
        "paragraph_count": len(paragraphs),
        "body_child_count": len(body),
        "paragraphs": controls,
    }


if __name__ == "__main__":
    for name in sys.argv[1:]:
        data = inspect(Path(name))
        output = Path(name).with_suffix(".structure.json")
        output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(output)
