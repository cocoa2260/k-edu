"""Check the v2 report's three physical/structural citations and both PDF renders."""
import argparse
import hashlib
import json
from pathlib import Path

import pdfplumber
from docx import Document

from tools.report_export import paragraphs


def compact(text):
    return "".join(text.split())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_render(path, expected):
    with pdfplumber.open(path) as pdf:
        text = compact("\n".join(p.extract_text() for p in pdf.pages))
        outside = sum(not (0 <= c["x0"] <= c["x1"] <= p.width and
                           0 <= c["top"] <= c["bottom"] <= p.height)
                      for p in pdf.pages for c in p.chars)
        missing = [i for i, line in enumerate(expected, 1) if compact(line) not in text]
        assert len(pdf.pages) == 1 and not missing and not outside
        return dict(pages=len(pdf.pages), expected_paragraphs=len(expected),
                    missing_paragraphs=missing, glyph_boxes_outside_page=outside, sha256=sha(path))


def run(report, docx_pdf, source):
    artifacts = report / "artifacts"
    spec_file = artifacts / "document-spec.json"
    assert spec_file.read_bytes() == (source / "multiformat-v1/output/document-spec.json").read_bytes()
    spec = json.loads(spec_file.read_text())
    expected = list(paragraphs(spec))
    assert [p.text for p in Document(artifacts / "evidence-report.docx").paragraphs] == expected
    sources = {
        "pdf": source / "document-v1/digital.pdf",
        "txt": source / "multiformat-v1/policy.txt",
        "docx": source / "multiformat-v1/policy.docx",
    }
    checked = []
    for claim in spec["claims"]:
        citation, = claim["citations"]
        loc = citation["locator"]
        path = sources[citation["doc"]]
        assert sha(path) == citation["source_sha256"]
        if loc["kind"] == "pdf_region":
            with pdfplumber.open(path) as pdf:
                observed = pdf.pages[loc["page"] - 1].crop(loc["bbox"]).extract_text()
        elif loc["kind"] == "text_line":
            observed = path.read_text().splitlines()[loc["line"] - 1]
        elif loc["kind"] == "docx_cell":
            observed = Document(path).tables[loc["table"] - 1].cell(loc["row"] - 1, loc["column"] - 1).text
        else:
            raise AssertionError(loc)
        assert compact(citation["quote"]) in compact(observed)
        checked.append(dict(claim=claim["id"], doc=citation["doc"], locator=loc, quote=citation["quote"],
                            source_sha256_matches=True, quote_at_locator=True))
    lab = json.loads((report / "observed.json").read_text())
    assert lab["source_restricted_after_output_blocks_new_export"]
    return dict(spec_matches_repository_v2=True, citations=checked,
                direct_pdf=check_render(artifacts / "evidence-report.pdf", expected),
                docx_render=check_render(docx_pdf, expected),
                restrict_blocks_new_export=True, existing_artifacts_present=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("report", "docx-pdf", "source", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    result = run(args.report, args.docx_pdf, args.source)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
