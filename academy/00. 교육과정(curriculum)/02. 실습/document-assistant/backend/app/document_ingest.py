"""L8 bounded local PDF laboratory, NOT a production untrusted-PDF sandbox.

Coordinates: PDF points in the rendered page frame, origin top-left, x right,
y down. Rotation/crop variants are refused instead of guessing a transform.
Document strings are data; no prompt, tool dispatch, eval or shell interpolation.
"""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
import unicodedata

import pdfplumber
from PIL import Image
from pypdf import PdfReader

PARSER_VERSION = "l8-local-v1"


class DocumentRejected(ValueError):
    pass


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def allowed(metadata):
    return metadata.get("access") == "staff" and metadata.get("current") is True and metadata.get("deleted", False) is False


def authorize(metadata):
    if not allowed(metadata): raise DocumentRejected("Source not eligible before file access")
    if not all(isinstance(metadata.get(k), str) and metadata[k].strip() for k in ("id", "version", "title")):
        raise DocumentRejected("Missing trusted source metadata")


def command(args, timeout=30):
    try:
        return subprocess.run(args, check=True, capture_output=True, text=True, timeout=timeout).stdout
    except (subprocess.SubprocessError, OSError) as error:
        raise DocumentRejected("Local renderer/OCR failed or timed out") from error


def check_languages(language, tessdata_dir):
    if not re.fullmatch(r"[a-z]{3}(\+[a-z]{3})*", language): raise DocumentRejected("Invalid OCR language")
    opts = ["--tessdata-dir", str(tessdata_dir)] if tessdata_dir else []
    available = command(["tesseract", "--list-langs", *opts]).splitlines()[1:]
    if not set(language.split("+")).issubset(set(available)): raise DocumentRejected("OCR language unavailable")
    return opts


def ocr_page(path, page_number, width, height, *, language, tessdata_dir, preprocess=False):
    opts = check_languages(language, tessdata_dir)
    with tempfile.TemporaryDirectory(prefix="l8-ocr-") as folder:
        stem = Path(folder) / "page"
        command(["pdftoppm", "-f", str(page_number), "-l", str(page_number), "-singlefile", "-r", "216", "-png", str(path), str(stem)])
        image_path = stem.with_suffix(".png")
        with Image.open(image_path) as original:
            pixel_width, pixel_height = original.size
            if pixel_width * pixel_height > 12_000_000: raise DocumentRejected("Rendered page too large")
            if preprocess:
                # Size is preserved; this threshold is not a universal deskew/table solution.
                original.convert("L").point(lambda x: 255 if x > 175 else 0).convert("RGB").save(image_path)
        # Explicit variable avoids relying on a system `configs/tsv` file when
        # --tessdata-dir points at only the separately pinned language assets.
        raw = command(["tesseract", str(image_path), "stdout", *opts, "-l", language, "--oem", "1", "--psm", "6", "-c", "tessedit_create_tsv=1"])
    if not raw.startswith("level\tpage_num\t"): raise DocumentRejected("OCR did not return TSV")
    words = []
    for row in csv.DictReader(io.StringIO(raw), delimiter="\t", quoting=csv.QUOTE_NONE):
        if row["level"] != "5" or not row.get("text", "").strip(): continue
        x, y, w, h = (float(row[k]) for k in ("left", "top", "width", "height"))
        box = [x * width / pixel_width, y * height / pixel_height, (x + w) * width / pixel_width, (y + h) * height / pixel_height]
        words.append(dict(text=row["text"].strip(), bbox=box, confidence=float(row["conf"]),
            group=[int(row[k]) for k in ("block_num", "par_num", "line_num")]))
    lines = []
    for group in dict.fromkeys(tuple(w["group"]) for w in words):
        items = [w for w in words if tuple(w["group"]) == group]
        lines.append(dict(kind="ocr_line", text=" ".join(w["text"] for w in items),
            bbox=[min(w["bbox"][0] for w in items), min(w["bbox"][1] for w in items), max(w["bbox"][2] for w in items), max(w["bbox"][3] for w in items)],
            confidence=sum(w["confidence"] for w in items) / len(items), words=items))
    if not lines: raise DocumentRejected("Blank/undecodable OCR page requires review")
    return lines


def ingest(path, metadata, *, language="kor+eng", tessdata_dir=None, preprocess=False):
    authorize(metadata)  # Must precede reads, hashing, render, OCR, encoding.
    path = Path(path)
    if path.stat().st_size > 8_000_000: raise DocumentRejected("PDF byte limit")
    reader = PdfReader(str(path))
    if reader.is_encrypted: raise DocumentRejected("Encrypted PDF unsupported")
    if not 1 <= len(reader.pages) <= 6: raise DocumentRejected("PDF page limit")
    for page in reader.pages:
        if int(page.get("/Rotate", 0)) % 360: raise DocumentRejected("Rotated PDF frame unsupported; normalize explicitly")
        if tuple(page.cropbox) != tuple(page.mediabox) or float(page.mediabox.left) != 0 or float(page.mediabox.bottom) != 0 or float(page.get("/UserUnit", 1)) != 1:
            raise DocumentRejected("Crop/origin/UserUnit transform unsupported")
        if not (0 < float(page.mediabox.width) <= 900 and 0 < float(page.mediabox.height) <= 1200): raise DocumentRejected("Page dimensions unsupported")
    source_sha = sha_file(path)
    pages = []
    with pdfplumber.open(path) as pdf:
        for number, page in enumerate(pdf.pages, 1):
            digital = bool(page.chars)
            if digital:
                blocks = [dict(kind="text_line", text=line["text"], bbox=[line[k] for k in ("x0", "top", "x1", "bottom")]) for line in page.extract_text_lines() if line["text"].strip()]
                tables = [dict(kind="table", bbox=list(table.bbox), rows=table.extract(), cells=[list(c) if c else None for c in table.cells]) for table in page.find_tables()]
                # A text layer can be garbage/partial. Do not silently claim completeness.
                route = "digital_text_layer_needs_visual_review" if page.images else "digital"
            else:
                blocks = ocr_page(path, number, page.width, page.height, language=language, tessdata_dir=tessdata_dir, preprocess=preprocess)
                tables = []  # OCR boxes do NOT reconstruct table relationships.
                route = "ocr"
            if not blocks: raise DocumentRejected("Empty extraction requires review")
            pages.append(dict(page=number, width=page.width, height=page.height, route=route,
                method="pdfplumber" if digital else "tesseract_tsv", blocks=blocks, tables=tables))
    if sha_file(path) != source_sha: raise DocumentRejected("Source changed during extraction")
    return dict(metadata=dict(metadata), source_sha256=source_sha, parser_version=PARSER_VERSION,
        coordinate_system="rendered_page_points_top_left_xyxy", pages=pages,
        document_type="mixed" if len({p["route"] for p in pages}) > 1 else ("scanned" if pages[0]["route"] == "ocr" else "digital"),
        review_required=True)


def fixture_column_order(path, bbox, split_x):
    """Explicit hand-selected fixture regions; not a general layout detector."""
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        x0, top, x1, bottom = bbox
        return [page.crop((x0, top, split_x, bottom)).extract_text(), page.crop((split_x, top, x1, bottom)).extract_text()]


def normalize(extraction):
    """One line chunk per block; tables remain a separately reviewed sidecar."""
    metadata = extraction["metadata"]
    authorize(metadata)
    texts, locators = [], []
    for page in extraction["pages"]:
        for block in page["blocks"]:
            text = " ".join(block["text"].split())
            texts.append(text)
            locators.append(dict(doc_id=metadata["id"], version=metadata["version"], line=len(texts),
                source_sha256=extraction["source_sha256"], parser_version=extraction["parser_version"],
                page=page["page"], bbox=block["bbox"], method=page["method"], text_sha256=hashlib.sha256(text.encode()).hexdigest()))
    return dict(metadata, text="\n".join(texts)), locators


def resolve(row, extraction, path, current_metadata):
    """Use canonical extraction, never trust caller-supplied location or text."""
    authorize(current_metadata)
    metadata = extraction["metadata"]
    if any(current_metadata.get(k) != metadata.get(k) for k in ("id", "version", "access", "current")):
        raise DocumentRejected("Source metadata changed")
    if sha_file(path) != extraction["source_sha256"] or extraction["parser_version"] != PARSER_VERSION:
        raise DocumentRejected("Stale source/parser; extract and index again")
    document, locators = normalize(extraction)
    line = row.get("line")
    if type(line) is not int or not 1 <= line <= len(locators) or row.get("doc_id") != metadata["id"] or row.get("version") != metadata["version"]:
        raise DocumentRejected("Unknown source/line/version")
    text = document["text"].splitlines()[line - 1]
    if row.get("text") != text: raise DocumentRejected("Context text does not match extracted block")
    return locators[line - 1]


def edit_distance(a, b):
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        current = [i]
        for j, right in enumerate(b, 1): current.append(min(current[-1] + 1, previous[j] + 1, previous[j-1] + (left != right)))
        previous = current
    return previous[-1]


def ocr_metrics(gold_lines, predicted, fields):
    # Evaluation region excludes the known synthetic footer. Never used in extraction.
    reference = unicodedata.normalize("NFC", " ".join(gold_lines))
    hypothesis = unicodedata.normalize("NFC", " ".join(predicted.split()))
    compact = lambda text: "".join(text.split())
    return dict(cer_whitespace_excluded=edit_distance(compact(reference), compact(hypothesis)) / len(compact(reference)),
        wer_whitespace_tokens=edit_distance(reference.split(), hypothesis.split()) / len(reference.split()),
        critical_fields={field: compact(field) in compact(hypothesis) for field in fields},
        field_check="substring presence only; not correct row/semantic association", prediction=hypothesis)
