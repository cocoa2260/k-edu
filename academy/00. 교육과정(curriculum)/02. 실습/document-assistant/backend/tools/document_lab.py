"""Actual PDF/OCR + existing index boundary demonstration; no LLM calls.

python -m tools.document_lab --specimens DIR --tessdata-dir DIR --output DIR
"""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

from app.document_ingest import command, fixture_column_order, ingest, normalize, ocr_metrics, resolve, sha_file
from retrieval.index import LocalIndex


class BoundaryEncoder:
    """Constant unit vector; deliberately NONSEMANTIC. Ranking uses BM25 only."""
    profile = dict(model_id="l8-boundary-fixture", revision="v1", dimension=2, normalized=True)

    def encode(self, texts, kind):
        return [[1.0, 0.0] for _ in texts]


def metadata(name):
    return dict(id="l8-" + name, version="1", access="staff", current=True, deleted=False, title="합성 환불 문서 " + name)


def run(specimens, tessdata_dir, output):
    specimens, output = Path(specimens), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    gold = json.loads((specimens / "gold.json").read_text())
    extracts, metrics = {}, {}
    for name in ("digital", "scan", "degraded", "mixed"):
        path = specimens / (name + ".pdf")
        if sha_file(path) != gold["files"][path.name]: raise ValueError("Specimen checksum mismatch")
        extraction = ingest(path, metadata(name), tessdata_dir=tessdata_dir)
        extracts[name] = extraction
        (output / (name + "-extraction.json")).write_text(json.dumps(extraction, ensure_ascii=False, indent=2) + "\n")
        if name in ("scan", "degraded"):
            blocks = [b for b in extraction["pages"][0]["blocks"] if b["bbox"][1] < 700]
            metrics[name] = ocr_metrics(gold["gold_scan_lines"], " ".join(b["text"] for b in blocks), gold["critical_fields"])
    processed = ingest(specimens / "degraded.pdf", metadata("degraded"), tessdata_dir=tessdata_dir, preprocess=True)
    metrics["degraded_threshold175"] = ocr_metrics(gold["gold_scan_lines"], " ".join(b["text"] for b in processed["pages"][0]["blocks"] if b["bbox"][1] < 700), gold["critical_fields"])
    (output / "degraded-preprocessed-extraction.json").write_text(json.dumps(processed, ensure_ascii=False, indent=2) + "\n")
    from pypdf import PdfReader
    raw = PdfReader(specimens / "digital.pdf").pages[0].extract_text()
    columns = fixture_column_order(specimens / "digital.pdf", gold["fixture_layout"]["columns_bbox"], gold["fixture_layout"]["split_x"])
    layout = dict(raw_content_stream_text=raw, manual_region_columns=columns,
        raw_right_before_left=raw.find("B1.") < raw.find("A1."),
        table_expected=gold["gold_table"], table_observed=extracts["digital"]["pages"][0]["tables"][0]["rows"],
        table_exact=extracts["digital"]["pages"][0]["tables"][0]["rows"] == gold["gold_table"],
        general_layout_detection=False)
    document, locators = normalize(extracts["digital"])
    index = LocalIndex.create(output / "l8-index.sqlite", BoundaryEncoder(), [document])
    try:
        selection = index.search("영수증을", method="bm25", k=1)
        context = index.context(selection)
        physical = [resolve(row, extracts["digital"], specimens / "digital.pdf", metadata("digital")) for row in context]
        if not physical: raise ValueError("Expected source roundtrip")
        index_manifest = index.manifest()
    finally: index.close()
    # Existing index's historical origin_path default is explicitly not a PDF path.
    result = dict(schema_version="0.1", synthetic=True, llm_calls=0, vision_calls=0,
        environment=dict(python=platform.python_version(), packages={n:importlib.metadata.version(n) for n in ("pdfplumber", "pypdf", "Pillow", "reportlab")}, tesseract=command(["tesseract", "--version"]).splitlines()[0]),
        assets={p.name: sha_file(p) for p in sorted(Path(tessdata_dir).glob("*.traineddata"))},
        routes={name:[p["route"] for p in extraction["pages"]] for name,extraction in extracts.items()},
        image_only_text_layer_empty={name: not (PdfReader(specimens / (name + ".pdf")).pages[0].extract_text() or "").strip() for name in ("scan", "degraded")},
        ocr_metrics=metrics, layout=layout,
        index_boundary=dict(encoder="constant fixture; NONSEMANTIC", ranking="BM25", selection=selection, context=context, physical_locators=physical,
            index_manifest=index_manifest, locator_count=len(locators), source_path="digital.pdf",
            warning="Legacy index origin_path is a logical default; use verified physical locator sidecar for this PDF."),
        quality_accepted=False, review_required=True, limitations=["four synthetic PDFs, not a representative OCR benchmark", "fixed manual column regions", "OCR confidence is not calibrated correctness", "no CLIP/VLM/OCR-free model run", "no real authentication, hostile PDF sandbox or web upload"])
    (output / "observed.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(dict(routes=result["routes"], metrics=metrics, table_exact=layout["table_exact"], physical_locators=physical), ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    for name in ("specimens", "tessdata-dir", "output"): parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    run(args.specimens, args.tessdata_dir, args.output)
