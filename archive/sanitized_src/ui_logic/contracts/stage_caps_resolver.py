import yaml
from pathlib import Path

def resolve_stage_caps(cards: list, policy: dict):
    """
    Apply stage caps to a list of cards.
    Returns (assets, overflow).
    """
    caps = policy.get("caps", {})
    stages = ["DECISION", "CONTENT", "SUPPORT"]
    
    final_assets = []
    overflow_assets = []
    
    # Process each stage according to UX Constitution
    for stage in stages:
        stage_cards = [c for c in cards if c.get("stage") == stage]
        # Sort by order
        stage_cards = sorted(stage_cards, key=lambda x: x.get("order", 999))
        
        cap = caps.get(stage, 99)
        
        # Split into active and overflow
        active = stage_cards[:cap]
        overflow = stage_cards[cap:]
        
        final_assets.extend(active)
        overflow_assets.extend(overflow)
        
    return final_assets, overflow_assets

def load_policy(project_root: Path):
    policy_path = project_root / "registry" / "ui_cards" / "ui_card_policy_v1.yml"
    if not policy_path.exists():
        return {"caps": {"DECISION": 4, "CONTENT": 5, "SUPPORT": 6}}
    with open(policy_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
