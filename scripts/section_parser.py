# scripts/section_parser.py

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
IN_DIR = ROOT / "research" / "extracted_text"
OUT_DIR = ROOT / "research" / "extracted_text"

def split_sections(text):
    sections = {
        "abstract": "",
        "introduction": "",
        "methodology": "",
        "results": "",
        "conclusion": ""
    }

    patterns = {
        "abstract": r"abstract",
        "introduction": r"introduction",
        "methodology": r"methodology|methods",
        "results": r"results",
        "conclusion": r"conclusion"
    }

    lower = text.lower()

    for sec, pat in patterns.items():
        match = re.search(pat, lower)
        if match:
            start = match.start()
            sections[sec] = text[start:start+3000]

    return sections

for file in IN_DIR.glob("*.json"):
    data = json.loads(file.read_text(encoding="utf-8"))
    sections = split_sections(data["full_text"])

    data["sections"] = sections

    file.write_text(json.dumps(data, indent=2), encoding="utf-8")

print("✅ Section-wise extraction completed")
