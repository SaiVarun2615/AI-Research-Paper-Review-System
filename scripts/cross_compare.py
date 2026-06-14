# scripts/cross_compare.py

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "research" / "analysis" / "key_findings.json"

data = json.loads(DATA.read_text(encoding="utf-8"))

common_themes = []

for paper in data:
    for point in paper["key_findings"]:
        if point.strip():
            common_themes.append(point.strip())

print("🔍 Cross-paper common findings:")
for theme in common_themes[:10]:
    print("-", theme)
