import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.paper_fetcher import fetch_from_queries


def test_fetch_function_exists():
    assert callable(fetch_from_queries)
