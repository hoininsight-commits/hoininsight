import sys
from pathlib import Path
from datetime import datetime
import json

def test_real_inputs():
    print("[TEST] Verifying IS-55 Real Input Connectors...")
    base_dir = Path(".")
    ymd = datetime.now().strftime("%Y-%m-%d")
    ymd_compact = ymd.replace("-", "")
    
    # 1. Check Fact Anchors (Harvester Output)
    fact_path = base_dir / "data" / "facts" / f"fact_anchors_{ymd_compact}.json"
    if not fact_path.exists():
        print(f"[FAIL] Fact Anchors not found at {fact_path}. Harvester did not run or failed.")
        sys.exit(1)
        
    facts = json.loads(fact_path.read_text(encoding='utf-8'))
    print(f"[PASS] Fact Anchors found: {len(facts)} entries.")
    
    # 2. Check Decision Card for Content Package
    # Find latest decision card for today
    today_decision_dir = base_dir / "data" / "decision" / ymd.replace("-", "/")
    card_path = today_decision_dir / "final_decision_card.json"
    
    if not card_path.exists():
         print(f"[FAIL] Final Decision Card not found at {card_path}.")
         sys.exit(1)
         
    card = json.loads(card_path.read_text(encoding='utf-8'))
    
    # Check Content Package Block
    pkg = card.get("blocks", {}).get("content_package", {})
    if not pkg:
        print("[FAIL] Content Package block missing in decision card.")
        sys.exit(1)
        
    if not pkg.get("long_form") or not pkg.get("shorts_ready"):
        print("[FAIL] Content Package incomplete (missing long_form or shorts).")
        sys.exit(1)
        
    print("[PASS] IS-55 Real Input & Content Generation verified.")

if __name__ == "__main__":
    test_real_inputs()
