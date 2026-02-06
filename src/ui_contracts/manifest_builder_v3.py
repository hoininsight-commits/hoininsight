import json
import yaml
from datetime import datetime
from pathlib import Path
from src.ui_contracts.stage_caps_resolver import resolve_stage_caps, load_policy

def build_manifest_v3(project_root: Path):
    """
    Registry-driven Manifest Builder v3 with Stage Caps.
    """
    registry_path = project_root / "registry" / "ui_cards" / "ui_card_registry_v1.yml"
    if not registry_path.exists():
        raise FileNotFoundError(f"Registry not found at {registry_path}")
        
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)
        
    policy = load_policy(project_root)
    cards = registry.get("cards", [])
    
    # 1. Resolve Caps & Overflow
    active_assets, overflow_assets = resolve_stage_caps(cards, policy)
    
    # 2. Add existence check for manifest
    def prepare_asset(card):
        asset_full_path = project_root / card["asset_path"]
        exists = asset_full_path.exists()
        return {
            "key": card["key"],
            "title": card["title"],
            "path": card["asset_path"],
            "required": card.get("required", False),
            "stage": card.get("stage", "SUPPORT"),
            "order": card.get("order", 999),
            "exists": exists
        }

    manifest = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "registry_version": registry.get("version", 1),
        "policy_version": policy.get("version", 1),
        "authority": "src/ui_contracts",
        "assets": [prepare_asset(a) for a in active_assets],
        "overflow": [prepare_asset(a) for a in overflow_assets]
    }
    
    out_path = project_root / "data" / "ui" / "manifest.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"[Manifest v3] Build complete. Assets: {len(manifest['assets'])}, Overflow: {len(manifest['overflow'])}")
    return manifest

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    build_manifest_v3(project_root)
