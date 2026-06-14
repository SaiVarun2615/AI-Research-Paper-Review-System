import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.pdf_export import build_pdf


def test_pdf_generation():
    pdf_path = build_pdf()
    assert Path(pdf_path).exists()
    assert str(pdf_path).endswith(".pdf")
