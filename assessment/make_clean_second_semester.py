from __future__ import annotations

import argparse
import copy
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


SUBJECTS = ("사회", "수학", "실과", "음악", "미술", "영어")
TABLE_START_RE = re.compile(r"^(사회|수학|실과|음악|미술|영어) 수행평가 기준안")

ET.register_namespace("hp", "http://www.hancom.co.kr/hwpml/2011/paragraph")
ET.register_namespace("hs", "http://www.hancom.co.kr/hwpml/2011/section")
ET.register_namespace("hc", "http://www.hancom.co.kr/hwpml/2011/core")

ROOT_NAMESPACE_DECLARATIONS = (
    'xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" '
    'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
    'xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" '
    'xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
    'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" '
    'xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" '
    'xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" '
    'xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" '
    'xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/" '
    'xmlns:opf="http://www.idpf.org/2007/opf/" '
    'xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" '
    'xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar" '
    'xmlns:epub="http://www.idpf.org/2007/ops" '
    'xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"'
)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(node: ET.Element) -> str:
    return "".join((part.text or "") for part in node.iter() if local(part.tag) == "t")


def direct_text(paragraph: ET.Element) -> str:
    pieces: list[str] = []
    for child in paragraph:
        if local(child.tag) != "run":
            continue
        pieces.extend((part.text or "") for part in child.iter() if local(part.tag) == "t")
    return "".join(pieces).strip()


def text_nodes(node: ET.Element):
    for child in node.iter():
        if local(child.tag) == "t":
            yield child


def replace_text(node: ET.Element, replacements: list[tuple[str, str]]) -> int:
    count = 0
    for text_node in text_nodes(node):
        value = text_node.text or ""
        for old, new in replacements:
            if old in value:
                occurrences = value.count(old)
                value = value.replace(old, new)
                count += occurrences
        text_node.text = value
    return count


def set_direct_text(paragraph: ET.Element, value: str) -> None:
    direct = [
        node
        for child in paragraph
        if local(child.tag) == "run"
        for node in child.iter()
        if local(node.tag) == "t"
    ]
    if not direct:
        raise ValueError("Paragraph has no direct text node")
    direct[0].text = value
    for node in direct[1:]:
        node.text = ""


def copy_cover(source_root: ET.Element) -> list[ET.Element]:
    cover: list[ET.Element] = []
    for child in list(source_root):
        if local(child.tag) != "p":
            continue
        if any(local(node.tag) == "tbl" for node in child.iter()):
            break
        clone = copy.deepcopy(child)
        for node in clone.iter():
            if local(node.tag) == "secPr":
                node.tag = "{http://www.hancom.co.kr/hwpml/2011/paragraph}secPr"
        for text_node in text_nodes(clone):
            value = text_node.text or ""
            if "5학년" in value and "1학기" in value:
                text_node.text = value.replace("1학기", "2학기")
        cover.append(clone)
    if not cover:
        raise ValueError("Could not find cover paragraphs")
    return cover


def split_subject_blocks(root: ET.Element) -> dict[str, list[ET.Element]]:
    body = [child for child in list(root) if local(child.tag) == "p"]
    starts: list[tuple[int, str]] = []
    for index, paragraph in enumerate(body):
        match = TABLE_START_RE.match(text_of(paragraph).strip())
        if match:
            starts.append((index, match.group(1)))

    blocks: dict[str, list[ET.Element]] = {subject: [] for subject in SUBJECTS}
    for position, (start, subject) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(body)
        blocks[subject].extend(copy.deepcopy(item) for item in body[start:end])
    return blocks


def find_operation_table(source_root: ET.Element, subject: str) -> ET.Element:
    heading = f"{subject}과 교수학습 및 평가 운영계획"
    for paragraph in source_root:
        if local(paragraph.tag) == "p" and text_of(paragraph).strip().startswith(heading):
            clone = copy.deepcopy(paragraph)
            for node in clone.iter():
                if local(node.tag) == "secPr":
                    node.tag = "{http://www.hancom.co.kr/hwpml/2011/paragraph}secPr"
            return clone
    raise ValueError(f"Missing operation table template for {subject}")


def find_first_table(paragraph: ET.Element) -> ET.Element:
    for node in paragraph.iter():
        if local(node.tag) == "tbl":
            return node
    raise ValueError("Paragraph does not contain a table")


def rows(table: ET.Element) -> list[ET.Element]:
    return [child for child in table if local(child.tag) == "tr"]


def cells(row: ET.Element) -> list[ET.Element]:
    return [child for child in row if local(child.tag) == "tc"]


def set_cell_text(cell: ET.Element, value: str) -> None:
    nodes = list(text_nodes(cell))
    if not nodes:
        raise ValueError("Cell has no text node")
    nodes[0].text = value
    for node in nodes[1:]:
        node.text = ""


def read_meta(criteria_paragraph: ET.Element) -> dict[str, str]:
    all_tables = [node for node in criteria_paragraph.iter() if local(node.tag) == "tbl"]
    table = all_tables[0]
    row_list = rows(table)
    if len(row_list) < 7:
        raise ValueError("Unexpected criteria table shape")

    metadata: dict[str, str] = {}
    for row in row_list:
        cell_list = cells(row)
        values = [re.sub(r"\s+", " ", text_of(cell)).strip() for cell in cell_list]
        for index, value in enumerate(values):
            key = value.replace(" ", "")
            if key in {"단원명", "평가시기", "평가요소", "성취기준", "영역", "평가유형", "수업․평가주안점"}:
                if index + 1 < len(values):
                    metadata[key] = values[index + 1]

    grade_label_map = {"상": "A", "중": "B", "하": "C", "A": "A", "B": "B", "C": "C"}
    for candidate in all_tables:
        for row in rows(candidate):
            cell_list = cells(row)
            values = [re.sub(r"\s+", " ", text_of(cell)).strip() for cell in cell_list]
            if len(values) >= 2 and values[0] in grade_label_map:
                metadata[grade_label_map[values[0]]] = values[-1]

    required = {"단원명", "평가시기", "평가요소", "성취기준", "영역", "수업․평가주안점", "A", "B", "C"}
    missing = required.difference(metadata)
    if missing:
        raise ValueError(f"Missing criteria metadata: {sorted(missing)}")
    return metadata


def build_operation_table(template: ET.Element, subject: str, metas: list[dict[str, str]]) -> ET.Element:
    table = find_first_table(template)
    row_list = rows(table)
    if len(row_list) < 5:
        raise ValueError(f"Unexpected operation-table template for {subject}")

    # Keep the exact 1st-semester style and one three-row evaluation record as a row template.
    title_row = row_list[0]
    semester_row = row_list[1]
    header_row = row_list[2]
    data_start = next(
        (
            index
            for index in range(3, len(row_list) - 2)
            if len(cells(row_list[index])) >= 8
            and len(cells(row_list[index + 1])) >= 2
            and len(cells(row_list[index + 2])) >= 2
        ),
        None,
    )
    if data_start is None or data_start + 2 >= len(row_list):
        raise ValueError(f"Operation table for {subject} has no reusable A/B/C row triplet")
    data_template = row_list[data_start : data_start + 3]

    title_cells = cells(title_row)
    set_cell_text(title_cells[0], f"{subject}과 교수학습 및 평가 운영계획")
    semester_cells = cells(semester_row)
    set_cell_text(semester_cells[0], "2026학년도 2학기")
    if len(semester_cells) > 1:
        set_cell_text(semester_cells[1], "5학년")

    for row in list(table):
        if local(row.tag) == "tr" and row not in {title_row, semester_row, header_row}:
            table.remove(row)

    for meta in metas:
        for grade_index, label in enumerate(("A", "B", "C")):
            row = copy.deepcopy(data_template[grade_index])
            cell_list = cells(row)
            if grade_index == 0 and len(cell_list) < 8:
                raise ValueError(f"Unexpected row cell count for {subject}: {len(cell_list)}")
            if len(cell_list) >= 8:
                values = [
                    meta["평가시기"],
                    meta["성취기준"],
                    meta["단원명"],
                    meta["영역"],
                    meta["평가요소"],
                    meta["수업․평가주안점"],
                    label,
                    meta[label],
                ]
            else:
                values = [label, meta[label]]
            for cell, value in zip(cell_list, values):
                set_cell_text(cell, value)
            table.append(row)

    return template


def find_criteria(block: list[ET.Element]) -> list[ET.Element]:
    result: list[ET.Element] = []
    for paragraph in block:
        text = text_of(paragraph).strip()
        if TABLE_START_RE.match(text):
            result.append(paragraph)
    return result


def normalize_block(block: list[ET.Element]) -> None:
    replacements = [
        ("무늬를 음악으로 세기고", "무늬를 음각으로 새기고"),
        ("불교과 국가의 종교", "불교가 국가의 종교"),
        ("있었음을 할 수 있다", "있었음을 알 수 있다"),
        ("통해 추론할 수 있는", "이를 통해 추론할 수 있는"),
        ("밤에서 불을 켜서", "밤에 불을 켜서"),
        ("간심", "관심"),
        ("더울 발전시킬", "더욱 발전시킬"),
        ("이를 이를 통해 추론할 수 있는", "이를 통해 추론할 수 있는"),
        ("가치를 인증 받고", "가치를 인정받고"),
        ("목반에 글자를", "목판에 글자를"),
        ("대칭 도형", "대칭도형"),
        ("삼묵법", "삼묵법"),
        ("잇는 사람들", "있는 사람들"),
        ("<벼타작.>", "<벼타작>"),
    ]
    for paragraph in block:
        replace_text(paragraph, replacements)

    if block and text_of(block[0]).strip().startswith("미술"):
        art_text = "\n".join(text_of(paragraph) for paragraph in block)
        if "7. 먹과 색이 어우러진 우리 그림" in art_text:
            for paragraph in block:
                for text_node in text_nodes(paragraph):
                    value = text_node.text or ""
                    if "도형(수학)" in value or "생활 속 대상에서 도형" in value:
                        text_node.text = value.replace(
                            "생활 속 대상에서 도형(수학)을 찾을 수 있는가?",
                            "수묵 담채화의 표현 방법을 활용하여 먹과 색의 농담 및 선의 변화를 나타낼 수 있는가?",
                        ).replace(
                            "생활 속 대상에서 도형",
                            "수묵 담채화에서 먹과 색의 농담과 선의 변화",
                        ).replace("도형(수학)", "수묵 담채화 표현 방법")


def renumber_ids(root: ET.Element) -> None:
    id_elements: list[ET.Element] = []
    next_by_tag: dict[str, int] = {}
    for node in root.iter():
        if "id" in node.attrib:
            try:
                value = int(node.attrib["id"])
                tag = local(node.tag)
                next_by_tag[tag] = max(next_by_tag.get(tag, 0), value + 1)
                id_elements.append(node)
            except ValueError:
                continue
    seen: set[tuple[str, str]] = set()
    for node in id_elements:
        value = node.attrib["id"]
        tag = local(node.tag)
        key = (tag, value)
        if key in seen:
            node.attrib["id"] = str(next_by_tag[tag])
            next_by_tag[tag] += 1
        else:
            seen.add(key)

    # Some IDs are empty in Hancom-authored files; keep empty identifiers untouched.


def update_preview(workdir: Path) -> None:
    preview = workdir / "Preview" / "PrvText.txt"
    if preview.exists():
        preview.write_text(
            "2026학년도\n과정 중심 평가 계획\n5학년 2학기\n장 량 초 등 학 교\n"
            "사회 수학 실과 음악 미술 영어 교수학습 및 평가 운영계획과 수행평가 기준안",
            encoding="utf-8",
        )


def write_hwpx(workdir: Path, target: Path, source: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as source_archive, zipfile.ZipFile(target, "w") as output:
        for source_info in source_archive.infolist():
            name = source_info.filename
            path = workdir / Path(name)
            if not path.is_file():
                raise FileNotFoundError(name)
            info = copy.copy(source_info)
            info.CRC = 0
            info.compress_size = 0
            info.file_size = 0
            output.writestr(info, path.read_bytes())


def merge_header(template_header: bytes, source_header: bytes) -> ET.Element:
    """Keep template styles first, then add any source definitions it needs."""
    template_root = ET.fromstring(template_header)
    source_root = ET.fromstring(source_header)
    definition_tags = {
        "fontface",
        "borderFill",
        "charPr",
        "tabPr",
        "numbering",
        "bullet",
        "paraPr",
        "style",
    }

    template_groups = {
        local(node.tag): node
        for node in template_root.iter()
        if any(local(child.tag) in definition_tags for child in node)
    }
    source_groups = {
        local(node.tag): node
        for node in source_root.iter()
        if any(local(child.tag) in definition_tags for child in node)
    }
    id_offsets: dict[str, int] = {}

    for group_name, source_group in source_groups.items():
        template_group = template_groups.get(group_name)
        if template_group is None:
            continue
        children = [child for child in source_group if local(child.tag) in definition_tags]
        if not children:
            continue
        existing_ids = [
            int(child.attrib["id"])
            for child in template_group
            if child.attrib.get("id", "").isdigit()
        ]
        offset = max(existing_ids, default=-1) + 1
        id_offsets[local(children[0].tag)] = offset
        for child in children:
            clone = copy.deepcopy(child)
            if clone.attrib.get("id", "").isdigit():
                clone.attrib["id"] = str(int(clone.attrib["id"]) + offset)
            template_group.append(clone)
        if "itemCnt" in template_group.attrib:
            template_group.attrib["itemCnt"] = str(len(list(template_group)))

    template_root.attrib["sourceOffsets"] = ";".join(
        f"{name}:{value}" for name, value in sorted(id_offsets.items())
    )
    return template_root


def apply_source_header_offsets(root: ET.Element, merged_header: ET.Element) -> None:
    encoded = merged_header.attrib.pop("sourceOffsets", "")
    offsets = {
        name: int(value)
        for item in encoded.split(";")
        if item
        for name, value in [item.split(":", 1)]
    }
    reference_map = {
        "paraPrIDRef": "paraPr",
        "styleIDRef": "style",
        "charPrIDRef": "charPr",
        "borderFillIDRef": "borderFill",
    }
    for node in root.iter():
        for attribute, definition in reference_map.items():
            value = node.attrib.get(attribute)
            if value is not None and value.isdigit() and definition in offsets:
                node.attrib[attribute] = str(int(value) + offsets[definition])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="schoolmaster-assessment-") as temp:
        workdir = Path(temp)
        with zipfile.ZipFile(args.template) as archive:
            archive.extractall(workdir)
        with zipfile.ZipFile(args.source) as archive:
            source_header = archive.read("Contents/header.xml")
            source_section = archive.read("Contents/section0.xml")
            source_content = archive.read("Contents/content.hpf")
            source_bindata = {name: archive.read(name) for name in archive.namelist() if name.startswith("BinData/")}

        template_header = (workdir / "Contents" / "header.xml").read_bytes()
        template_root = ET.fromstring((workdir / "Contents" / "section0.xml").read_bytes())
        source_root = ET.fromstring(source_section)
        cover = copy_cover(template_root)
        blocks = split_subject_blocks(source_root)

        merged_header = merge_header(template_header, source_header)
        apply_source_header_offsets(source_root, merged_header)
        # Re-split after source references have been shifted into the merged header namespace.
        blocks = split_subject_blocks(source_root)

        new_root = copy.deepcopy(source_root)
        for child in list(new_root):
            new_root.remove(child)

        for paragraph in cover:
            new_root.append(paragraph)

        for subject in SUBJECTS:
            block = blocks[subject]
            if not block:
                raise ValueError(f"No source block for {subject}")
            normalize_block(block)
            criteria = find_criteria(block)
            metas = [read_meta(item) for item in criteria]
            operation_template = find_operation_table(template_root, subject)
            operation_table = build_operation_table(operation_template, subject, metas)
            new_root.append(operation_table)
            for paragraph in block:
                new_root.append(paragraph)

        (workdir / "Contents" / "header.xml").write_bytes(
            ET.tostring(merged_header, encoding="utf-8", xml_declaration=True)
        )
        section_xml = ET.tostring(new_root, encoding="unicode", xml_declaration=False)
        section_xml = re.sub(r'^<hs:sec(?:\s+xmlns:[^=]+="[^"]+")*', '<hs:sec', section_xml, count=1)
        if section_xml.startswith("<hs:sec>"):
            section_xml = section_xml.replace("<hs:sec>", f"<hs:sec {ROOT_NAMESPACE_DECLARATIONS}>", 1)
        elif section_xml.startswith("<hs:sec "):
            section_xml = section_xml.replace("<hs:sec ", f"<hs:sec {ROOT_NAMESPACE_DECLARATIONS} ", 1)
        (workdir / "Contents" / "section0.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' + section_xml,
            encoding="utf-8",
        )
        (workdir / "Contents" / "content.hpf").write_bytes(source_content)

        bindata_dir = workdir / "BinData"
        if bindata_dir.exists():
            shutil.rmtree(bindata_dir)
        bindata_dir.mkdir(parents=True)
        for name, data in source_bindata.items():
            target = workdir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

        update_preview(workdir)
        write_hwpx(workdir, args.output, args.source)
        print(args.output)


if __name__ == "__main__":
    main()
