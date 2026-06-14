import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.quality_check import run_quality_checks


def test_quality_report_structure():
    report = run_quality_checks()
    assert isinstance(report, dict)
    for k in ["Abstract", "Methods", "Results", "References"]:
        assert k in report
