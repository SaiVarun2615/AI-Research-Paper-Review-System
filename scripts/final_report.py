from pathlib import Path

DRAFTS_DIR = Path(__file__).parent.parent / "research" / "drafts"
OUTPUT = DRAFTS_DIR / "final_report.txt"

def run():
    sections = ["abstract.txt", "methods.txt", "results.txt", "references.txt"]
    with open(OUTPUT, "w", encoding="utf-8") as out:
        for sec in sections:
            out.write(f"\n\n=== {sec.replace('.txt','').upper()} ===\n\n")
            out.write((DRAFTS_DIR / sec).read_text(encoding="utf-8"))

    print("✅ Final report generated")

if __name__ == "__main__":
    run()
