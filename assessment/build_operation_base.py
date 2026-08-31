from __future__ import annotations

import copy
import io
import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


SUBJECTS = ("사회", "수학", "실과", "음악", "미술", "영어")


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(node: ET.Element) -> str:
    return "".join((part.text or "") for part in node.iter() if local(part.tag) == "t")


def register_namespaces(data: bytes) -> None:
    for _, namespace in ET.iterparse(io.BytesIO(data), events=("start-ns",)):
        prefix, uri = namespace
        ET.register_namespace(prefix, uri)


def text_nodes(node: ET.Element) -> list[ET.Element]:
    return [part for part in node.iter() if local(part.tag) == "t"]


def set_text(node: ET.Element, value: str) -> None:
    nodes = text_nodes(node)
    if not nodes:
        raise ValueError("No text node in target")
    nodes[0].text = value
    for extra in nodes[1:]:
        extra.text = ""


def table_of(paragraph: ET.Element) -> ET.Element:
    return next(node for node in paragraph.iter() if local(node.tag) == "tbl")


def rows(table: ET.Element) -> list[ET.Element]:
    return [node for node in table if local(node.tag) == "tr"]


def cells(row: ET.Element) -> list[ET.Element]:
    return [node for node in row if local(node.tag) == "tc"]


def find_operation_paragraph(root: ET.Element, subject: str) -> ET.Element:
    prefix = f"{subject}과 교수학습 및 평가 운영계획"
    for paragraph in root:
        if local(paragraph.tag) == "p" and text_of(paragraph).strip().startswith(prefix):
            return copy.deepcopy(paragraph)
    raise ValueError(f"Missing operation-plan template: {subject}")


def fill_operation_table(paragraph: ET.Element, subject: str, items: list[dict[str, str]]) -> None:
    table = table_of(paragraph)
    row_list = rows(table)
    required_rows = 3 + len(items) * 3
    if len(row_list) < required_rows:
        raise ValueError(f"Not enough reusable rows for {subject}: {len(row_list)} < {required_rows}")

    set_text(cells(row_list[0])[0], f"{subject}과 교수학습 및 평가 운영계획")
    set_text(cells(row_list[1])[0], "2026학년도 2학기")
    set_text(cells(row_list[1])[1], "5학년")

    for row in row_list[required_rows:]:
        table.remove(row)
    table.attrib["rowCnt"] = str(required_rows)
    row_list = rows(table)

    for item_index, item in enumerate(items):
        a_row = row_list[3 + item_index * 3]
        b_row = row_list[4 + item_index * 3]
        c_row = row_list[5 + item_index * 3]
        a_cells = cells(a_row)
        b_cells = cells(b_row)
        c_cells = cells(c_row)
        values = (
            item["when"],
            item["standard"],
            item["unit"],
            item["area"],
            item["element"],
            item["method"],
            "A",
            item["A"],
        )
        if len(a_cells) != len(values) or len(b_cells) != 2 or len(c_cells) != 2:
            raise ValueError(f"Unexpected operation-plan row shape for {subject}")
        for cell, value in zip(a_cells, values):
            set_text(cell, value)
        set_text(b_cells[0], "B")
        set_text(b_cells[1], item["B"])
        set_text(c_cells[0], "C")
        set_text(c_cells[1], item["C"])


def write_package(source: Path, target: Path, section_data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as source_archive, zipfile.ZipFile(target, "w") as output:
        for source_info in source_archive.infolist():
            info = copy.copy(source_info)
            info.CRC = 0
            info.compress_size = 0
            info.file_size = 0
            data = section_data if source_info.filename == "Contents/section0.xml" else source_archive.read(source_info)
            output.writestr(info, data)


def main() -> None:
    template = Path(sys.argv[1])
    metadata_path = Path(sys.argv[2])
    target = Path(sys.argv[3])
    metadata: dict[str, list[dict[str, str]]] = json.loads(metadata_path.read_text(encoding="utf-8"))

    with zipfile.ZipFile(template) as archive:
        original_section = archive.read("Contents/section0.xml")
    register_namespaces(original_section)
    source_root = ET.fromstring(original_section)

    cover: list[ET.Element] = []
    for paragraph in source_root:
        if local(paragraph.tag) != "p":
            continue
        if any(local(node.tag) == "tbl" for node in paragraph.iter()):
            break
        clone = copy.deepcopy(paragraph)
        for node in text_nodes(clone):
            if "5학년" in (node.text or "") and "1학기" in (node.text or ""):
                node.text = (node.text or "").replace("1학기", "2학기")
        cover.append(clone)
    if not cover:
        raise ValueError("Cover was not found")

    result_root = copy.deepcopy(source_root)
    for child in list(result_root):
        result_root.remove(child)
    for paragraph in cover:
        result_root.append(paragraph)

    for index, subject in enumerate(SUBJECTS):
        paragraph = find_operation_paragraph(source_root, subject)
        fill_operation_table(paragraph, subject, metadata[subject])
        # The original cover naturally fills page 1. Every later subject starts on a new page.
        if index > 0:
            paragraph.attrib["pageBreak"] = "1"
        result_root.append(paragraph)

    original_text = original_section.decode("utf-8")
    root_start = original_text.index("<hs:sec")
    root_end = original_text.index(">", root_start)
    original_root_open = original_text[root_start : root_end + 1]
    serialized = ET.tostring(result_root, encoding="unicode", xml_declaration=False)
    serialized_root_end = serialized.index(">")
    serialized = original_root_open + serialized[serialized_root_end + 1 :]
    section_data = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' + serialized
    ).encode("utf-8")
    write_package(template, target, section_data)
    print(target)


if __name__ == "__main__":
    main()
