from __future__ import annotations

import copy
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_nodes(root: ET.Element):
    for node in root.iter():
        if local(node.tag) == "t":
            yield node


source = Path(sys.argv[1])
target = Path(sys.argv[2])

with zipfile.ZipFile(source) as archive:
    section = archive.read("Contents/section0.xml")
    root = ET.fromstring(section)

replacements = (
    ("5학년 1학기", "5학년 2학기"),
    ("5학년  1학기", "5학년  2학기"),
    ("5학년    1학기", "5학년    2학기"),
    ("음악으로 세기고", "음각으로 새기고"),
    ("불교과 국가의 종교", "불교가 국가의 종교"),
    ("밤에서 불을 켜서", "밤에 불을 켜서"),
    ("간심", "관심"),
    ("더울 발전시킬", "더욱 발전시킬"),
    ("생활 속 대상에서 도형(수학)을 찾을 수 있는가?", "수묵 담채화의 표현 방법을 활용하여 먹과 색의 농담 및 선의 변화를 나타낼 수 있는가?"),
    ("도형(수학)", "수묵 담채화 표현 방법"),
)

counts = {old: 0 for old, _ in replacements}
for node in text_nodes(root):
    value = node.text or ""
    for old, new in replacements:
        if old in value:
            counts[old] += value.count(old)
            value = value.replace(old, new)
    node.text = value

section_text = section.decode("utf-8")
start = section_text.index("<hs:sec")
open_end = section_text.index(">", start)
root_open = section_text[start : open_end + 1]

ET.register_namespace("hp", "http://www.hancom.co.kr/hwpml/2011/paragraph")
ET.register_namespace("hs", "http://www.hancom.co.kr/hwpml/2011/section")
ET.register_namespace("hc", "http://www.hancom.co.kr/hwpml/2011/core")
serialized = ET.tostring(root, encoding="unicode", xml_declaration=False)
serialized_open_end = serialized.index(">")
serialized = root_open + serialized[serialized_open_end + 1 :]
updated_section = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' + serialized

target.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(source) as source_archive, zipfile.ZipFile(target, "w") as output:
    for source_info in source_archive.infolist():
        data = updated_section.encode("utf-8") if source_info.filename == "Contents/section0.xml" else source_archive.read(source_info.filename)
        info = copy.copy(source_info)
        info.CRC = info.compress_size = info.file_size = 0
        output.writestr(info, data)

for old, count in counts.items():
    print(f"{old}={count}")
print(target)
