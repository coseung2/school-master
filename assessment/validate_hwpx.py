from __future__ import annotations

import collections
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


path = Path(sys.argv[1])
with zipfile.ZipFile(path) as archive:
    if archive.testzip() is not None:
        raise SystemExit("ZIP_CORRUPT")
    if archive.namelist()[0] != "mimetype":
        raise SystemExit("MIMETYPE_NOT_FIRST")
    if archive.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
        raise SystemExit("MIMETYPE_COMPRESSED")
    archive_section = archive.read("Contents/section0.xml")
    root = ET.fromstring(archive_section)
    ET.fromstring(archive.read("Contents/header.xml"))
    ET.fromstring(archive.read("Contents/content.hpf"))

paragraphs = [node for node in root if local(node.tag) == "p"]
text = "\n".join(
    "".join((part.text or "") for part in paragraph.iter() if local(part.tag) == "t")
    for paragraph in paragraphs
)

subjects = ("사회", "수학", "실과", "음악", "미술", "영어")
expected_criteria = {"사회": 2, "수학": 3, "실과": 2, "음악": 2, "미술": 2, "영어": 2}

checks = {
    "cover": all(value in text for value in ("2026학년도", "과정 중심 평가 계획", "5학년 2학기", "장 량 초 등 학 교")),
    "operations": all(text.count(f"{subject}과 교수학습 및 평가 운영계획") == 1 for subject in subjects),
    "criteria": all(text.count(f"{subject} 수행평가 기준안") == count for subject, count in expected_criteria.items()),
    "bad_semester_removed": "1학기" not in text and "2025학년도" not in text,
    "typos_removed": not any(
        value in text
        for value in (
            "음악으로 세기고",
            "불교과 국가의 종교",
            "밤에서 불을 켜서",
            "간심",
            "더울 발전시킬",
            "도형(수학)",
            "생활 속 대상에서 도형",
            "도형을 3개 찾았을 경우",
            "도형을 2개만 찾았을 경우",
            "도형을 1개만 찾았을 경우",
            "찾은 도형",
            "찾은 수학적 원리",
            "생활 속 대상에 들어 있는 다양한 수학적 원리",
            "이를 이를 통해 추론할 수 있는",
            "가치를 인증 받고",
            "목반에 글자를",
        )
    ),
    "art7": all(
        value in text
        for value in (
            "7. 먹과 색이 어우러진 우리 그림",
            "수묵 담채화의 표현 방법",
            "삼묵법",
            "몰골법",
            "구륵법",
            "선의 굵기와 흐름에 변화를 주기",
        )
    ),
    "layout_cache_removed": b"<hp:linesegarray>" not in archive_section,
}

for value in (
    "음악으로 세기고",
    "불교과 국가의 종교",
    "밤에서 불을 켜서",
    "간심",
    "더울 발전시킬",
    "도형(수학)",
    "생활 속 대상에서 도형",
):
    if value in text:
        print(f"remaining_bad_text={value}")

for name, passed in checks.items():
    print(f"{name}={'OK' if passed else 'FAIL'}")
if not all(checks.values()):
    raise SystemExit(1)
print(f"paragraphs={len(paragraphs)}")
print("VALIDATE_HWPX_OK")
