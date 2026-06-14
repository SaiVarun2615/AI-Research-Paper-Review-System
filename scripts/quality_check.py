from pathlib import Path

DRAFTS_DIR = Path(__file__).parent.parent / "research" / "drafts"

def check_file(path, min_words=30):
    if not path.exists():
        return "❌ File missing"
    text = path.read_text(encoding="utf-8").strip()
    if len(text.split()) < min_words:
        return "⚠️ Content too short"
    return "✅ Looks good"

def run_quality_checks():
    report = {}
    report["Abstract"] = check_file(DRAFTS_DIR / "abstract.txt", 80)
    report["Methods"] = check_file(DRAFTS_DIR / "methods.txt", 50)
    report["Results"] = check_file(DRAFTS_DIR / "results.txt", 50)
    report["References"] = check_file(DRAFTS_DIR / "references.txt", 10)
    return report
