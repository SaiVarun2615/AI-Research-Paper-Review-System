# scripts/pipeline_runner.py

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"

def run_full_pipeline():
    steps = [
        "paper_fetcher.py",
        "extract_text.py", 
        "key_findings.py",
        "statistics_engine.py",
        "draft_generator_llm.py",
        "milestone3_generate.py",
    ]

    for step in steps:
        script_path = SCRIPTS / step
        print(f"▶ Running {script_path.name}")

        subprocess.run(
            [sys.executable, str(script_path)],  # 🔥 THIS IS THE FIX
            check=True
        )

    return "Full pipeline completed successfully"
