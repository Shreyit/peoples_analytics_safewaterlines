"""Inspect the PDF exported by PowerPoint and retain native slide previews."""
from __future__ import annotations

import json
import math
import sys
import unicodedata
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
# Optional deck prefix, e.g. "pitch" for the 20-minute pitch; default is the executive deck.
PREFIX = sys.argv[1] if len(sys.argv) > 1 else ""
DECK = {"": "Safewater_Lines_People_Experience", "pitch": "Safewater_Lines_Pitch_20min"}[PREFIX]
source = HERE / f"output/{DECK}_PowerPoint.pdf"
content = json.loads((HERE / (f"{PREFIX}_slide_content.json" if PREFIX else "slide_content.json")).read_text())
pdf = pymupdf.open(source)
assert len(pdf) == len(content)
dest = HERE / ("preview/native" if not PREFIX else f"preview/{PREFIX}/native")
dest.mkdir(parents=True, exist_ok=True)
for old in dest.glob("slide-*.png"):
    old.unlink()


def normalise(value):
    return "".join(unicodedata.normalize("NFKC", value).split())


missing, overflow, thumbs = [], [], []
for i, page in enumerate(pdf):
    extracted = normalise(page.get_text(sort=False))
    for obj in content[i]["objects"]:
        if obj["kind"] == "text" and normalise(" ".join(obj["lines"])) not in extracted:
            missing.append({"slide": i + 1, "text": obj["text"]})
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            x0, y0, x1, y1 = line["bbox"]
            if x0 < -1 or y0 < -1 or x1 > page.rect.width + 1 or y1 > page.rect.height + 1:
                overflow.append({"slide": i + 1, "bbox": line["bbox"]})
    path = dest / f"slide-{i+1:02d}.png"
    page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False).save(path)
    image = Image.open(path).convert("RGB")
    image.thumbnail((480, 270))
    thumbs.append(image)

sheet = Image.new("RGB", (1440, 300 * math.ceil(len(thumbs) / 3)), "#E8ECEF")
draw = ImageDraw.Draw(sheet)
for i, image in enumerate(thumbs):
    x, y = i % 3 * 480, i // 3 * 300
    sheet.paste(image, (x, y))
    draw.text((x + 12, y + 277), f"{i+1:02d}  {content[i]['section']}", fill="#365F7B")
sheet.save(dest / "contact-sheet.png")
result = {"renderer": "Microsoft PowerPoint for macOS PDF export", "pages": len(pdf),
          "all_expected_text_present": not missing, "text_outside_canvas": overflow,
          "missing_text": missing, "native_previews": "preview/native/"}
(HERE / ((f"{PREFIX}_" if PREFIX else "") + "native_qa_results.json")).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
assert not missing, f"PowerPoint PDF is missing {len(missing)} text elements; see native_qa_results.json"
assert not overflow, overflow
print(f"PASS: {len(pdf)} PowerPoint-rendered pages; all expected text present; no text outside the slide canvas.")
