from __future__ import annotations

import copy
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(node: ET.Element) -> str:
    return "".join((part.text or "") for part in node.iter() if local(part.tag) == "t")


def text_nodes(node: ET.Element) -> list[ET.Element]:
    return [part for part in node.iter() if local(part.tag) == "t"]


def set_text(node: ET.Element, value: str) -> None:
    nodes = text_nodes(node)
    if not nodes:
        raise ValueError("Target cell has no text node")
    nodes[0].text = value
    for extra in nodes[1:]:
        extra.text = ""


def rows(table: ET.Element) -> list[ET.Element]:
    return [node for node in table if local(node.tag) == "tr"]


def cells(row: ET.Element) -> list[ET.Element]:
    return [node for node in row if local(node.tag) == "tc"]


def apply_replacements(root: ET.Element) -> dict[str, int]:
    replacements = (
        ("음악으로 세기고", "음각으로 새기고"),
        ("불교과 국가의 종교", "불교가 국가의 종교"),
        ("밤에서 불을 켜서", "밤에 불을 켜서"),
        ("간심", "관심"),
        ("더울 발전시킬", "더욱 발전시킬"),
        ("있었음을 할 수 있다", "있었음을 알 수 있다"),
        ("접 시", "접시"),
        ("대칭 도형", "대칭도형"),
        ("<벼타작.>", "<벼타작>"),
    )
    counts = {old: 0 for old, _ in replacements}
    for node in text_nodes(root):
        value = node.text or ""
        for old, new in replacements:
            if old in value:
                counts[old] += value.count(old)
                value = value.replace(old, new)
        node.text = value
    return counts


def replace_art_scoring_table(root: ET.Element) -> None:
    art = next(
        paragraph
        for paragraph in root
        if local(paragraph.tag) == "p"
        and "미술 수행평가 기준안" in text_of(paragraph)
        and "7. 먹과 색이 어우러진 우리 그림" in text_of(paragraph)
    )
    tables = [node for node in art.iter() if local(node.tag) == "tbl"]
    scoring = next(
        table
        for table in reversed(tables)
        if len(rows(table)) == 12
        and cells(rows(table)[0])
        and text_of(cells(rows(table)[0])[0]).strip() == "평가 항목 (1)"
        and ("생활 속 대상에서 도형" in text_of(table) or "도형(수학)" in text_of(table))
    )
    row_list = rows(scoring)
    if len(row_list) != 12:
        raise ValueError(f"Unexpected art scoring table row count: {len(row_list)}")

    content = (
        (1, "수묵 담채화의 표현 방법을 활용하여 먹과 색의 농담을 나타낼 수 있는가?"),
        (2, "삼묵법·몰골법·구륵법을 적절히 활용하고 먹과 색의 농담을 풍부하게 표현한 경우"),
        (1, "두 가지 이상의 표현 방법을 활용하고 먹과 색의 농담을 나타낸 경우"),
        (1, "안내에 따라 한 가지 표현 방법과 먹의 농담을 부분적으로 나타낸 경우"),
        (1, "붓을 누르는 힘과 먹물의 양을 조절하여 선의 굵기와 흐름에 변화를 주었는가?"),
        (2, "선의 굵기와 흐름의 변화를 자연스럽고 효과적으로 나타낸 경우"),
        (1, "선의 굵기나 흐름에 부분적인 변화를 나타낸 경우"),
        (1, "안내에 따라 선의 변화를 부분적으로 나타낸 경우"),
        (1, "수묵 담채화의 재료와 용구를 바르게 사용하고 작품의 의도와 표현 특징을 설명할 수 있는가?"),
        (2, "재료와 용구를 바르게 사용하고 작품의 의도와 표현 특징을 구체적으로 설명한 경우"),
        (1, "재료와 용구를 바르게 사용하고 작품의 표현 특징을 설명한 경우"),
        (1, "안내에 따라 재료와 용구를 사용하고 작품에 대해 간단히 말한 경우"),
    )
    for row, (cell_index, value) in zip(row_list, content):
        row_cells = cells(row)
        if cell_index >= len(row_cells):
            raise ValueError("Unexpected art scoring table cell shape")
        set_text(row_cells[cell_index], value)


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
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    with zipfile.ZipFile(source) as archive:
        original_section = archive.read("Contents/section0.xml")
    root = ET.fromstring(original_section)

    counts = apply_replacements(root)
    replace_art_scoring_table(root)

    original_text = original_section.decode("utf-8")
    root_start = original_text.index("<hs:sec")
    root_end = original_text.index(">", root_start)
    root_open = original_text[root_start : root_end + 1]
    ET.register_namespace("hp", "http://www.hancom.co.kr/hwpml/2011/paragraph")
    ET.register_namespace("hs", "http://www.hancom.co.kr/hwpml/2011/section")
    ET.register_namespace("hc", "http://www.hancom.co.kr/hwpml/2011/core")
    serialized = ET.tostring(root, encoding="unicode", xml_declaration=False)
    serialized = root_open + serialized[serialized.index(">") + 1 :]
    section_data = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' + serialized
    ).encode("utf-8")
    write_package(source, target, section_data)

    full_text = re.sub(r"\s+", " ", text_of(root))
    forbidden = (
        "음악으로 세기고",
        "불교과 국가의 종교",
        "밤에서 불을 켜서",
        "간심",
        "더울 발전시킬",
        "도형(수학)",
        "생활 속 대상에서 도형",
        "찾은 수학적 원리",
    )
    remaining = [value for value in forbidden if value in full_text]
    if remaining:
        raise ValueError(f"Corrections remain: {remaining}")
    for old, count in counts.items():
        print(f"{old}={count}")
    print(target)


if __name__ == "__main__":
    main()
