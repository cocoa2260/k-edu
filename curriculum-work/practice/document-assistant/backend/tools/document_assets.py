"""Download public L8 assets with recorded SHA256; abort on any drift.

python -m tools.document_assets --output NEW_DIR
The mutable upstream URLs are guarded by snapshot hashes, not claimed pinned
revisions. Assets remain outside Git. Requires network for this setup only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ASSETS = {
    "kor.traineddata": ("https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/kor.traineddata", "6b85e11d9bbf07863b97b3523b1b112844c43e713df8b66418a081fd1060b3b2"),
    "eng.traineddata": ("https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/eng.traineddata", "7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2"),
    "NotoSansKR.ttf": ("https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf", "194018e6b2b293a7964f037b25c0249ce1418bc9ab3c971060a03aa57861e252"),
}


def setup(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name, (url, expected) in ASSETS.items():
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read(16_000_001)
        if len(data) > 16_000_000 or hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("Asset checksum mismatch; do not substitute a new version silently: " + name)
        (output / name).write_bytes(data)
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    font = TTFont(output / "NotoSansKR.ttf", recalcTimestamp=False)
    instantiateVariableFont(font, {"wght":400}, inplace=True)
    font.save(output / "NotoSansKR-Regular.ttf")
    record = dict(retrieved_snapshot="2026-10-31", url_revision="main, checksum guarded",
        inputs={name:dict(url=url,sha256=sha) for name,(url,sha) in ASSETS.items()},
        static_font_sha256=hashlib.sha256((output / "NotoSansKR-Regular.ttf").read_bytes()).hexdigest())
    (output / "assets.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--output", required=True)
    setup(parser.parse_args().output)
