from src.ui.ui_decision_contract import build_ui_decision_contract
import shutil
import os
from pathlib import Path

def run_publish():
    # 1. Build contract in temp dir
    build_ui_decision_contract(input_dir="data/decision", output_dir="data/ui_decision")

    # 2. Publish to docs/data/decision
    dest_dir = Path("docs/data/decision")
    dest_dir.mkdir(parents=True, exist_ok=True)

    src_dir = Path("data/ui_decision")
    if src_dir.exists():
        for f in src_dir.glob("*.json"):
            shutil.copy2(f, dest_dir / f.name)
            print(f"[PUBLISH] Copied {f.name} -> {dest_dir}")
    
    # Also ensure build_meta.json is copied if it exists in data/
    # (Though workflow usually generates it directly in docs/data/)
    
    print("[PUBLISH] UI Decision Assets published to docs/data/decision")

if __name__ == "__main__":
    run_publish()
