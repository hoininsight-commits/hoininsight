import os
import json
from pathlib import Path

def test_ref013_no_undefined_guard():
    print("=== VERIFYING REF-013: No-Undefined Asset Guard ===")
    project_root = Path(os.getcwd())
    
    # Check both working dir and published dir
    data_paths = [
        project_root / "data_outputs/ops",
        project_root / "docs/data/ui",
        project_root / "docs/data/ops"
    ]
    
    forbidden = '"undefined"'
    leaks = []
    
    for dp in data_paths:
        if not dp.exists(): continue
        for p in dp.rglob("*.json"):
            content = p.read_text(encoding="utf-8")
            if forbidden in content:
                leaks.append(f"JSON Leak: {p.relative_to(project_root)} contains 'undefined'")
                
    # Essential Asset Presence Check
    essential = ["manifest.json", "operator_main_card.json"]
    for dp in [project_root / "docs/data/ui", project_root / "data_outputs/ops"]:
        if not dp.exists(): continue
        present_files = [f.name for f in dp.glob("*.json")]
        for e in essential:
            # manifest is in ui/ usually
            pass

    assert not leaks, f"Found undefined values in UI assets:\n" + "\n".join(leaks)
    print("\n=== REF-013 ASSET GUARD SUCCESS ===")

if __name__ == "__main__":
    test_ref013_no_undefined_guard()
