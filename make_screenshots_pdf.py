from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

SCREENSHOTS = Path(r"C:\Users\user\Pictures\Screenshots")
OUT = Path(r"C:\Users\user\Desktop\5학년2학기_수행평가_과목별_목록_캡처_3페이지.pdf")

# Capture order corresponds to the subject tabs captured by the user.
PAGES = [
    ("실과", SCREENSHOTS / "스크린샷 2026-08-31 120606.png"),
    ("미술", SCREENSHOTS / "스크린샷 2026-08-31 120615.png"),
    ("수학", SCREENSHOTS / "스크린샷 2026-08-31 120553.png"),
    ("음악", SCREENSHOTS / "스크린샷 2026-08-31 120610.png"),
    ("국어", SCREENSHOTS / "스크린샷 2026-08-31 120539.png"),
    ("사회", SCREENSHOTS / "스크린샷 2026-08-31 120545.png"),
]

for subject, path in PAGES:
    if not path.exists():
        raise FileNotFoundError(path)

pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
W, H = landscape(A4)
c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
# Two captures per landscape page: readable while keeping the PDF to three pages.
for page_no in range(0, len(PAGES), 2):
    c.setFont("HYSMyeongJo-Medium", 14)
    c.drawString(32, H - 28, "5학년 2학기 수행평가 목록")
    c.setFont("HYSMyeongJo-Medium", 8)
    c.setFillGray(0.35)
    c.drawRightString(W - 32, H - 24, f"{page_no // 2 + 1} / {len(PAGES) // 2}")
    c.setFillGray(0)

    slot_top = H - 48
    slot_h = (H - 66) / 2
    for slot, (subject, path) in enumerate(PAGES[page_no:page_no + 2]):
        img = ImageReader(str(path))
        iw, ih = img.getSize()
        slot_bottom = slot_top - slot_h
        # Reserve a fixed band for the subject label so it never touches the capture.
        max_w = W - 64
        max_top = slot_top - 28
        max_bottom = slot_bottom + 12
        max_h = max_top - max_bottom
        scale = min(max_w / iw, max_h / ih)
        dw, dh = iw * scale, ih * scale
        x = (W - dw) / 2
        y = max_bottom + (max_h - dh) / 2
        c.setFont("HYSMyeongJo-Medium", 10)
        c.drawString(38, slot_top - 14, subject)
        c.setStrokeGray(0.78)
        c.rect(x - 3, y - 3, dw + 6, dh + 6, stroke=1, fill=0)
        c.drawImage(img, x, y, width=dw, height=dh, preserveAspectRatio=True, mask="auto")
        slot_top = slot_bottom
    c.showPage()
c.save()
print(OUT)
