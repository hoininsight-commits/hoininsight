import json
import os
from datetime import datetime
from pathlib import Path

def build_manifest(project_root: Path):
    """
    Scans data/ui/ and data/decision/ to create a UI manifest.
    Deterministic, template-based only.
    """
    data_ui = project_root / "data" / "ui"
    data_decision = project_root / "data" / "decision"
    
    manifest_path = data_ui / "manifest.json"
    
    assets = [
        {"key": "operator_narrative_order", "path": "data/ui/operator_narrative_order.json", "required": True},
        {"key": "operator_main_card", "path": "data/ui/operator_main_card.json", "required": True},
        {"key": "hero_summary", "path": "data/ui/hero_summary.json", "required": False},
        {"key": "narrative_entry_hook", "path": "data/ui/narrative_entry_hook.json", "required": False},
        {"key": "schedule_risk_calendar", "path": "data/ui/upcoming_risk_topN.json", "required": False},
        {"key": "interpretation_units", "path": "data/decision/interpretation_units.json", "required": True},
        {"key": "briefing", "path": "data/decision/natural_language_briefing.json", "required": False}
    ]
    
    # Check existence
    for asset in assets:
        full_path = project_root / asset["path"]
        if not full_path.exists():
            print(f"[Manifest] Warning: Asset {asset['key']} missing at {asset['path']}")
            # We keep the path in manifest, UI will handle with placeholder

    manifest = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "ui_base_path": "data/ui",
        "decision_base_path": "data/decision",
        "assets": assets
    }
    
    data_ui.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"[Manifest] Created manifest at {manifest_path}")
    return manifest

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    build_manifest(project_root)
