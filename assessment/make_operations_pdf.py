from __future__ import annotations

import json
import sys
from pathlib import Path

import fitz


SUBJECTS = ("사회", "수학", "실과", "음악", "미술", "영어")
PAGE = fitz.paper_rect("a4")
MARGIN_X = 28
TOP = 27
BOTTOM = 30
TABLE_WIDTH = PAGE.width - MARGIN_X * 2
COL_WIDTHS = [31, 70, 65, 38, 58, 160, 22, TABLE_WIDTH - 444]
HEADER_FILL = (0.91, 0.94, 0.98)
TITLE_FILL = (0.82, 0.88, 0.95)
LABEL_FILL = (0.94, 0.95, 0.96)
GRID = (0.25, 0.25, 0.25)


def find_font() -> tuple[str, str]:
    candidates = (
        Path(r"C:\Windows\Fonts\malgun.ttf"),
        Path(r"C:\Windows\Fonts\NanumGothic.ttf"),
        Path(r"C:\Windows\Fonts\batang.ttc"),
    )
    for candidate in candidates:
        if candidate.exists():
            return "korean", str(candidate)
    raise FileNotFoundError("No Korean font found")


FONT_NAME, FONT_FILE = find_font()


def rect(x: float, y: float, width: float, height: float) -> fitz.Rect:
    return fitz.Rect(x, y, x + width, y + height)


def draw_text(
    page: fitz.Page,
    box: fitz.Rect,
    value: str,
    *,
    size: float,
    align: int = 0,
    bold: bool = False,
    valign: float = 0.5,
    lineheight: float = 1.14,
) -> None:
    inset = 2.2
    target = fitz.Rect(box.x0 + inset, box.y0 + inset, box.x1 - inset, box.y1 - inset)
    fitted_size = size
    best_size: float | None = None
    while fitted_size >= 4.6:
        shape = page.new_shape()
        spare = shape.insert_textbox(
            target,
            value,
            fontname=FONT_NAME,
            fontfile=FONT_FILE,
            fontsize=fitted_size,
            align=align,
            lineheight=lineheight,
        )
        if spare >= -0.1:
            shape.commit(overlay=True)
            best_size = fitted_size
            break
        fitted_size -= 0.2
    if best_size is None:
        raise ValueError(f"Text overflow ({spare:.1f}): {value[:80]}")
    if bold:
        page.insert_textbox(
            fitz.Rect(target.x0 + 0.18, target.y0, target.x1 + 0.18, target.y1),
            value,
            fontname=FONT_NAME,
            fontfile=FONT_FILE,
            fontsize=best_size,
            align=align,
            lineheight=lineheight,
        )


def draw_cell(
    page: fitz.Page,
    box: fitz.Rect,
    value: str,
    *,
    size: float,
    align: int = 0,
    bold: bool = False,
    fill: tuple[float, float, float] | None = None,
    lineheight: float = 1.14,
) -> None:
    page.draw_rect(box, color=GRID, fill=fill, width=0.45, overlay=False)
    draw_text(page, box, value, size=size, align=align, bold=bold, lineheight=lineheight)


def draw_header(page: fitz.Page, subject: str, page_number: int, continued: bool = False) -> float:
    page.insert_font(fontname=FONT_NAME, fontfile=FONT_FILE)
    y = TOP
    suffix = " (계속)" if continued else ""
    title = rect(MARGIN_X, y, TABLE_WIDTH, 25)
    draw_cell(
        page,
        title,
        f"{subject}과 교수학습 및 평가 운영계획{suffix}",
        size=13.2,
        align=1,
        bold=True,
        fill=TITLE_FILL,
    )
    y += 25
    semester_left = rect(MARGIN_X, y, TABLE_WIDTH * 0.67, 17)
    semester_right = rect(semester_left.x1, y, TABLE_WIDTH - semester_left.width, 17)
    draw_cell(page, semester_left, "2026학년도 2학기", size=8.4, align=1, bold=True)
    draw_cell(page, semester_right, "5학년", size=8.4, align=1, bold=True)
    y += 17
    headers = ("시기", "성취기준", "단원명", "평가 영역", "평가 요소", "수업·평가 방법, 연계의 주안점", "평가 기준", "내용")
    x = MARGIN_X
    for width, value in zip(COL_WIDTHS, headers):
        draw_cell(page, rect(x, y, width, 25), value, size=6.4, align=1, bold=True, fill=HEADER_FILL)
        x += width
    y += 25
    page.insert_text(
        (PAGE.width / 2 - 12, PAGE.height - 15),
        f"- {page_number} -",
        fontname=FONT_NAME,
        fontfile=FONT_FILE,
        fontsize=7,
        color=(0.35, 0.35, 0.35),
    )
    return y


def estimate_group_height(item: dict[str, str]) -> float:
    text_load = max(
        len(item["standard"]) / 16,
        len(item["unit"]) / 13,
        len(item["area"]) / 8,
        len(item["element"]) / 12,
        len(item["method"]) / 42,
    )
    criteria_load = sum(max(1.0, len(item[key]) / 26) for key in ("A", "B", "C"))
    return max(168.0, 36 + max(text_load * 7.4, criteria_load * 7.5))


def draw_item(page: fitz.Page, y: float, item: dict[str, str], height: float) -> float:
    criteria_heights = []
    criteria_total = max(72.0, height)
    loads = [max(1.0, len(item[key]) / 27) for key in ("A", "B", "C")]
    load_sum = sum(loads)
    for load in loads:
        criteria_heights.append(criteria_total * load / load_sum)

    x = MARGIN_X
    common_values = (item["when"], item["standard"], item["unit"], item["area"], item["element"], item["method"])
    common_sizes = (6.2, 6.15, 6.3, 6.3, 6.15, 6.05)
    common_aligns = (1, 0, 0, 1, 0, 0)
    for width, value, size, align in zip(COL_WIDTHS[:6], common_values, common_sizes, common_aligns):
        draw_cell(page, rect(x, y, width, height), value, size=size, align=align, lineheight=1.12)
        x += width

    criterion_x = x
    detail_x = criterion_x + COL_WIDTHS[6]
    cy = y
    for label, key, row_height in zip(("A", "B", "C"), ("A", "B", "C"), criteria_heights):
        draw_cell(page, rect(criterion_x, cy, COL_WIDTHS[6], row_height), label, size=7, align=1, bold=True, fill=LABEL_FILL)
        draw_cell(page, rect(detail_x, cy, COL_WIDTHS[7], row_height), item[key], size=6.0, align=0, lineheight=1.11)
        cy += row_height
    return y + height


def add_subject(document: fitz.Document, subject: str, items: list[dict[str, str]], page_number: int) -> int:
    page = document.new_page(width=PAGE.width, height=PAGE.height)
    y = draw_header(page, subject, page_number)
    available = PAGE.height - BOTTOM - y
    for index, item in enumerate(items):
        height = estimate_group_height(item)
        if height > available:
            page_number += 1
            page = document.new_page(width=PAGE.width, height=PAGE.height)
            y = draw_header(page, subject, page_number, continued=True)
            available = PAGE.height - BOTTOM - y
        y = draw_item(page, y, item, height)
        available = PAGE.height - BOTTOM - y
    return page_number + 1


def main() -> None:
    metadata_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    metadata: dict[str, list[dict[str, str]]] = json.loads(metadata_path.read_text(encoding="utf-8"))
    document = fitz.open()
    page_number = 2
    for subject in SUBJECTS:
        page_number = add_subject(document, subject, metadata[subject], page_number)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path, garbage=4, deflate=True)
    print(f"pages={len(document)} output={output_path}")


if __name__ == "__main__":
    main()
