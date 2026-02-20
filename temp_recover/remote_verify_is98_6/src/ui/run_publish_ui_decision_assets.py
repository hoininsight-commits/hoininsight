from src.ui.ui_decision_contract import build_ui_decision_contract
from src.ui.natural_language_mapper import NaturalLanguageMapper
import shutil
import json
import os
from pathlib import Path

def run_publish():
    # 1. Build contract in temp dir
    build_ui_decision_contract(input_dir="data/decision", output_dir="data/ui_decision")

    # 2. Generate Natural Language Briefing
    mapper = NaturalLanguageMapper(input_dir="data/decision")
    briefing = mapper.build_briefing()
    briefing_path = Path("data/ui_decision/natural_language_briefing.json")
    with open(briefing_path, "w", encoding="utf-8") as f:
        json.dump(briefing, f, indent=2, ensure_ascii=False)
    print(f"[UI-MAPPER] Generated {briefing_path}")

    # 3. Publish to docs/data/decision
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
