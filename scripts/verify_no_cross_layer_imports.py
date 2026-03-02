#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

# Prohibition Rules (Forbidden: Key -> Forbidden Importer)
RULES = [
    {
        "pattern": r"from src\.engine",
        "forbidden_in": ["src/ui", "src/ui_logic", "src/reporters"],
        "reason": "UI/Reporters must not depend on Engine logic directly (only on published assets)"
    },
    {
        "pattern": r"import src\.engine",
        "forbidden_in": ["src/ui", "src/ui_logic", "src/reporters"],
        "reason": "UI/Reporters must not depend on Engine logic directly (only on published assets)"
    },
    {
        "pattern": r"from src\.ops\.narrative",
        "forbidden_in": ["src/ui", "src/ui_logic"],
        "reason": "UI must not contain Narrative scoring/calculation logic (No Scoring Leak)"
    },
    {
        "pattern": r"from src\.collectors",
        "forbidden_in": ["src/ui", "src/ui_logic", "src/ops"],
        "reason": "Intelligence/UI layers must not depend on raw collection logic"
    }
]

def verify():
    root = Path(".").resolve()
    violations = []

    print("--- Verifying Cross-Layer Isolation ---")
    
    for rule in RULES:
        pattern = re.compile(rule["pattern"])
        for folder in rule["forbidden_in"]:
            folder_path = root / folder
            if not folder_path.exists():
                continue
                
            for py_file in folder_path.rglob("*.py"):
                # Skip the SSOT publisher itself as it needs to orchestrate
                if "run_publish_ui_decision_assets.py" in str(py_file):
                    continue
                if "publish_ui_assets.py" in str(py_file):
                    continue
                # Skip legacy orchestrators being phased out in Phase 21
                if "run_daily_pipeline.py" in str(py_file):
                    continue
                if "run_content_pack_pipeline.py" in str(py_file):
                    continue
                    
                content = py_file.read_text(encoding="utf-8")
                if pattern.search(content):
                    rel_path = py_file.relative_to(root)
                    violations.append(f"❌ {rel_path}: {rule['reason']}")

    if violations:
        for v in violations:
            print(v)
        print(f"\nTotal violations: {len(violations)}")
        sys.exit(1)
    else:
        print("✅ No cross-layer violations found.")
        sys.exit(0)

if __name__ == "__main__":
    verify()
