from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


SUBJECTS = ("사회", "수학", "실과", "음악", "미술", "영어")


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(node: ET.Element) -> str:
    return "".join((part.text or "") for part in node.iter() if local(part.tag) == "t")


def rows(table: ET.Element) -> list[ET.Element]:
    return [node for node in table if local(node.tag) == "tr"]


def cells(row: ET.Element) -> list[ET.Element]:
    return [node for node in row if local(node.tag) == "tc"]


def tables(paragraph: ET.Element) -> list[ET.Element]:
    return [node for node in paragraph.iter() if local(node.tag) == "tbl"]


def read_meta(paragraph: ET.Element) -> dict[str, str]:
    table_list = tables(paragraph)
    result: dict[str, str] = {}
    for row in rows(table_list[0]):
        values = [re.sub(r"\s+", " ", text_of(cell)).strip() for cell in cells(row)]
        for index, value in enumerate(values):
            key = value.replace(" ", "")
            if key in {"단원명", "평가시기", "평가요소", "성취기준", "영역", "수업․평가주안점"} and index + 1 < len(values):
                result[key] = values[index + 1]
    levels = {"상": "A", "중": "B", "하": "C", "A": "A", "B": "B", "C": "C"}
    for table in table_list:
        for row in rows(table):
            values = [re.sub(r"\s+", " ", text_of(cell)).strip() for cell in cells(row)]
            if len(values) >= 2 and values[0] in levels:
                result[levels[values[0]]] = values[-1]
    return result


def extract(path: Path) -> dict[str, list[dict[str, str]]]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("Contents/section0.xml"))
    output: dict[str, list[dict[str, str]]] = {subject: [] for subject in SUBJECTS}
    for paragraph in root:
        if local(paragraph.tag) != "p":
            continue
        text = text_of(paragraph).strip()
        for subject in SUBJECTS:
            if text.startswith(f"{subject} 수행평가 기준안"):
                raw = read_meta(paragraph)
                output[subject].append(
                    {
                        "when": raw["평가시기"],
                        "standard": raw["성취기준"],
                        "unit": raw["단원명"],
                        "area": raw["영역"],
                        "element": raw["평가요소"],
                        "method": raw["수업․평가주안점"],
                        "A": raw["A"],
                        "B": raw["B"],
                        "C": raw["C"],
                    }
                )
                break
    return output


if __name__ == "__main__":
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    target.write_text(json.dumps(extract(source), ensure_ascii=False, indent=2), encoding="utf-8")
    print(target)
