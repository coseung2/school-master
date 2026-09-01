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
        ("이를 이를 통해 추론할 수 있는", "이를 통해 추론할 수 있는"),
        ("가치를 인증 받고", "가치를 인정받고"),
        ("목반에 글자를", "목판에 글자를"),
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
    # The scoring grid may contain the legacy wording split across nested
    # text runs, so identify it by its stable 12-row shape and the first
    # assessment-item label rather than one exact contaminated phrase.
    scoring = next(
        table
        for table in reversed(tables)
        if len(rows(table)) == 12
        and cells(rows(table)[0])
        and text_of(cells(rows(table)[0])[0]).strip().startswith("평가 항목 (1)")
        and any(
            marker in text_of(table)
            for marker in ("도형을 3개 찾았을 경우", "생활 속 대상", "도형(수학)")
        )
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


RAW_REPLACEMENTS = (
    ("음악으로 세기고", "음각으로 새기고"),
    ("불교과 국가의 종교", "불교가 국가의 종교"),
    ("밤에서 불을 켜서", "밤에 불을 켜서"),
    ("간심", "관심"),
    ("더울 발전시킬", "더욱 발전시킬"),
    ("이를 이를 통해 추론할 수 있는", "이를 통해 추론할 수 있는"),
    ("가치를 인증 받고", "가치를 인정받고"),
    ("목반에 글자를", "목판에 글자를"),
    ("PC또는 스마트 기기", "PC 또는 스마트 기기"),
    ("접 시", "접시"),
    ("대칭 도형", "대칭도형"),
    ("<벼타작.>", "<벼타작>"),
    ("생활 속 대상에서 도형(수학)을 찾을 수 있는가?", "수묵 담채화의 표현 방법을 활용하여 먹과 색의 농담을 나타낼 수 있는가?"),
    ("도형을 3개 찾았을 경우", "삼묵법·몰골법·구륵법을 적절히 활용하고 먹과 색의 농담을 풍부하게 표현한 경우"),
    ("도형을 2개만 찾았을 경우", "두 가지 이상의 표현 방법을 활용하고 먹과 색의 농담을 나타낸 경우"),
    ("도형을 1개만 찾았을 경우", "안내에 따라 한 가지 표현 방법과 먹의 농담을 부분적으로 나타낸 경우"),
    ("1번 질문에서 도형을 3개 찾았을 경우", "삼묵법·몰골법·구륵법을 적절히 활용하고 먹과 색의 농담을 풍부하게 표현한 경우"),
    ("1번 질문에서 도형을 2개만 찾았을 경우", "두 가지 이상의 표현 방법을 활용하고 먹과 색의 농담을 나타낸 경우"),
    ("1번 질문에서 도형을 1개만 찾았을 경우", "안내에 따라 한 가지 표현 방법과 먹의 농담을 부분적으로 나타낸 경우"),
    ("찾은 도형(수학)을 자세히 관찰하여 연결되어 있는 모양을 파악하였는가?", "붓을 누르는 힘과 먹물의 양을 조절하여 선의 굵기와 흐름에 변화를 주었는가?"),
    ("찾은 수묵 담채화 표현 방법을 자세히 관찰하여 연결되어 있는 모양을 파악하였는가?", "붓을 누르는 힘과 먹물의 양을 조절하여 선의 굵기와 흐름에 변화를 주었는가?"),
    ("※ 평소에 무심코 봐 왔던 생활 속 대상을 집중하여 관심 있게 보면서 미적 대상으로 인식하는 데초점을 두어 평가하므로, 주제를 벗어나지 않는 범위에서 각자의 관점을 존중하여 정답으로 처리함.", "※ 붓의 힘과 먹물의 양을 조절하여 선의 굵기와 흐름을 자연스럽게 표현했는지 평가함."),
    ("※ 평소에 무심코 봐 왔던 생활 속 대상을 집중하여 관심 있게 보면서 미적 대상으로 인식하는 데", "※ 붓의 힘과 먹물의 양을 조절하여 선의 굵기와 흐름을 자연스럽게 표현했는지 평가함."),
    ("초점을 두어 평가하므로, 주제를 벗어나지 않는 범위에서 각자의 관점을 존중하여 정답으로 처리함.", ""),
    ("붓을 누르는 힘과 먹물의 양을 다르게 하여 선의 굵기에 변화 주기", "붓을 누르는 힘과 먹물의 양을 다르게 하여 선의 굵기와 흐름에 변화를 주기"),
    ("찾은 수학적 원리가 미술과 어떻게 융합되었는가를 이해하고 있는가?", "수묵 담채화의 재료와 용구를 바르게 사용하고 작품의 의도와 표현 특징을 설명할 수 있는가?"),
    ("※ 생활 속 대상에 들어 있는 다양한 수학적 원리가, 우리가 접하는 대상을 더 아름답고 조화롭게 만들고,우리의 삶을 여러 측면에서 더 풍요롭게 만든다는 내용이 들어가면 정답으로 처리함.", "※ 재료와 용구를 바르게 사용하고 작품에 활용한 삼묵법·몰골법·구륵법, 먹과 색의 농담, 선의 변화를 설명했는지 평가함."),
    ("※ 생활 속 대상에 들어 있는 다양한 수학적 원리가, 우리가 접하는 대상을 더 아름답고 조화롭게 만들고,", "※ 재료와 용구를 바르게 사용하고 작품에 활용한 삼묵법·몰골법·구륵법, 먹과 색의 농담, 선의 변화를 설명했는지 평가함."),
    ("우리의 삶을 여러 측면에서 더 풍요롭게 만든다는 내용이 들어가면 정답으로 처리함.", ""),
)


def apply_raw_replacements(section_data: bytes) -> tuple[bytes, dict[str, int]]:
    """Patch only text bytes so HWPML layout and namespace serialization stay intact."""
    text = section_data.decode("utf-8")
    counts: dict[str, int] = {}
    for old, new in RAW_REPLACEMENTS:
        count = text.count(old)
        if count:
            text = text.replace(old, new)
        counts[old] = count
    # Hancom stores paragraph layout in linesegarray. After external text
    # edits that cache becomes stale and Hancom may report the document as
    # damaged or tampered. Remove only caches belonging to changed paragraphs;
    # untouched layout data remains byte-for-byte intact.
    changed_markers = [value for old, new in RAW_REPLACEMENTS for value in (old, new)]
    text, removed = strip_changed_paragraph_linesegarrays(text, changed_markers)
    counts["<hp:linesegarray>"] = removed
    return text.encode("utf-8"), counts


def strip_changed_paragraph_linesegarrays(text: str, markers: list[str]) -> tuple[str, int]:
    token_re = re.compile(r"<[^>]+>|[^<]+", re.DOTALL)
    paragraphs: list[tuple[int, int, str]] = []
    line_segments: list[tuple[int, int]] = []
    para_stack: list[dict[str, object]] = []
    line_stack: list[int] = []
    for match in token_re.finditer(text):
        token = match.group(0)
        if token.startswith("<hp:p") and not token.startswith("</"):
            para_stack.append({"start": match.start(), "parts": []})
        elif token.startswith("</hp:p"):
            if para_stack:
                frame = para_stack.pop()
                paragraphs.append((int(frame["start"]), match.end(), "".join(frame["parts"])))
        elif token.startswith("<hp:linesegarray") and not token.endswith("/>"):
            line_stack.append(match.start())
        elif token.startswith("</hp:linesegarray") and line_stack:
            line_segments.append((line_stack.pop(), match.end()))
        elif not token.startswith("<") and para_stack:
            # Keep only direct paragraph text. A table-hosting paragraph may
            # contain many nested hp:p nodes; their changes must not cause the
            # host paragraph's unrelated layout cache to be removed.
            para_stack[-1]["parts"].append(token)
    marked = [(start, end) for start, end, value in paragraphs if any(marker in value for marker in markers)]
    removals = [segment for segment in line_segments if any(start <= segment[0] and segment[1] <= end for start, end in marked)]
    for start, end in reversed(removals):
        text = text[:start] + text[end:]
    return text, len(removals)


def main() -> None:
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    with zipfile.ZipFile(source) as archive:
        original_section = archive.read("Contents/section0.xml")
    section_data, counts = apply_raw_replacements(original_section)
    write_package(source, target, section_data)

    root = ET.fromstring(section_data)
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
        "도형을 3개 찾았을 경우",
        "도형을 2개만 찾았을 경우",
        "도형을 1개만 찾았을 경우",
        "목반에 글자를",
        "이를 이를 통해 추론할 수 있는",
        "가치를 인증 받고",
    )
    remaining = [value for value in forbidden if value in full_text]
    if remaining:
        raise ValueError(f"Corrections remain: {remaining}")
    for old, count in counts.items():
        print(f"{old}={count}")
    print(target)


if __name__ == "__main__":
    main()
