"""Create and check an explicitly synthetic merged-cell PDF table."""
import argparse
import json
import re
import subprocess
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from app.document_ingest import ingest, normalize, resolve

PAGE = (595, 842)
X = (42, 146, 270, 380, 553)
Y = (130, 168, 213, 258, 303, 348)
ROWS = [
    ["구분", "신청 조건", "부담금", "제출 자료"],
    ["일반", "미사용", "0원", "영수증"],
    [None, "사용 이력 있음", "15000원", "영수증과 확인서"],
    ["특별", "기한 경과", "25000원", "소명서"],
    [None, "운영자 귀책", "5000원", "증빙 자료"],
]
FOOTNOTE = "예외: 운영자 귀책으로 미사용인 경우 부담금은 0원입니다."


def generate(output, font):
    digital = output / "complex-digital.pdf"
    pdfmetrics.registerFont(TTFont("KeduFixture", str(font)))
    doc = canvas.Canvas(str(digital), pagesize=PAGE, invariant=True)
    doc.setFont("KeduFixture", 21)
    doc.drawString(42, PAGE[1] - 77, "교육용 환불 조건표")
    doc.setFont("KeduFixture", 12)
    doc.drawString(42, PAGE[1] - 105, "병합된 분류와 행별 부담금 및 예외를 확인합니다.")
    for x in X:
        doc.line(x, PAGE[1] - Y[0], x, PAGE[1] - Y[-1])
    for i, y in enumerate(Y):
        doc.line(X[1] if i in (2, 4) else X[0], PAGE[1] - y, X[-1], PAGE[1] - y)
    doc.setFont("KeduFixture", 13)
    for row, cells in enumerate(ROWS):
        for col, cell in enumerate(cells):
            if cell is None:
                continue
            bottom = Y[row + (2 if col == 0 and row in (1, 3) else 1)]
            mid = (Y[row] + bottom) / 2
            doc.drawCentredString((X[col] + X[col + 1]) / 2, PAGE[1] - mid - 5, cell)
    doc.setFont("KeduFixture", 12)
    doc.drawString(42, PAGE[1] - 384, FOOTNOTE)
    doc.showPage()
    doc.save()
    subprocess.run(["pdftoppm", "-r", "216", "-png", "-singlefile", str(digital), str(output / "complex")], check=True)
    scan = canvas.Canvas(str(output / "complex-scan.pdf"), pagesize=PAGE, invariant=True)
    scan.drawImage(ImageReader(str(output / "complex.png")), 0, 0, *PAGE)
    scan.showPage()
    scan.save()


def inspect(path, assets):
    meta = dict(id=path.stem, version="1", access="staff", current=True, deleted=False, title="교육용 환불 조건표")
    result = ingest(path, meta, tessdata_dir=assets)
    page = result["pages"][0]
    document, _ = normalize(result)
    positions = {}
    for i, line in enumerate(document["text"].splitlines(), 1):
        for number in re.findall(r"(?<!\d)\d+\s*원", line):
            key = number.replace(" ", "")
            pointer = resolve(dict(doc_id=meta["id"], version="1", line=i, text=line), result, path, meta)
            positions.setdefault(key, []).append(dict(
                text=line, page=pointer["page"], bbox=pointer["bbox"], method=pointer["method"],
                line=i, source_sha256=pointer["source_sha256"]
            ))
    amounts_in_expected_row = {
        row[2]: any(Y[i] <= (b["bbox"][1] + b["bbox"][3]) / 2 <= Y[i + 1]
                    for b in positions.get(row[2], []))
        for i, row in enumerate(ROWS[1:], 1)
    }
    return dict(route=page["route"], blocks=page["blocks"], tables=page["tables"],
                exact_table=bool(page["tables"] and page["tables"][0]["rows"] == ROWS),
                amounts_in_expected_row=amounts_in_expected_row, amount_source_roundtrips=positions,
                footnote_exact=any("".join(FOOTNOTE.split()) in "".join(b["text"].split()) for b in page["blocks"]),
                source_sha256=result["source_sha256"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    generate(args.output, args.assets / "NotoSansKR-Regular.ttf")
    results = {key: inspect(args.output / f"complex-{key}.pdf", args.assets) for key in ("digital", "scan")}
    payload = dict(expected_table=ROWS, expected_footnote=FOOTNOTE, results=results)
    (args.output / "observed.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
