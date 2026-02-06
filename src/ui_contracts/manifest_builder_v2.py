import json
import yaml
from datetime import datetime
from pathlib import Path

def build_manifest_v2(project_root: Path):
    """
    Registry-driven Manifest Builder v2.
    Reads registry/ui_cards/ui_card_registry_v1.yml and generates data/ui/manifest.json.
    """
    registry_path = project_root / "registry" / "ui_cards" / "ui_card_registry_v1.yml"
    if not registry_path.exists():
        raise FileNotFoundError(f"Registry not found at {registry_path}")
        
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)
        
    version = registry.get("version", 1)
    cards = registry.get("cards", [])
    
    # Sort by order
    sorted_cards = sorted(cards, key=lambda x: x.get("order", 999))
    
    assets = []
    for card in sorted_cards:
        asset_full_path = project_root / card["asset_path"]
        exists = asset_full_path.exists()
        
        assets.append({
            "key": card["key"],
            "title": card["title"],
            "path": card["asset_path"],
            "required": card.get("required", False),
            "stage": card.get("stage", "SUPPORT"),
            "order": card.get("order", 999),
            "exists": exists
        })

    manifest = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "registry_version": version,
        "assets": assets
    }
    
    out_path = project_root / "data" / "ui" / "manifest.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"[Manifest v2] Created manifest with {len(assets)} assets at {out_path}")
    return manifest

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    build_manifest_v2(project_root)
