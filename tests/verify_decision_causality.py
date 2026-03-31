import json
from pathlib import Path

def test_causality_integrity():
    project_root = Path(__file__).parent.parent
    brief_path = project_root / "data" / "ops" / "today_operator_brief.json"
    
    if not brief_path.exists():
        print(f"❌ Brief not found at {brief_path}")
        return False
        
    with open(brief_path, "r", encoding="utf-8") as f:
        brief = json.load(f)
        
    # Mandatory Fields for STEP-D
    decision = brief.get("investment_decision", {})
    
    mandatory_decision_fields = ["action", "timing", "confidence"]
    causality_keys = ["theme", "mechanism", "structural_context", "trigger", "decision_link"]
    
    errors = []
    
    # 1. Check Decision Causality
    for field in mandatory_decision_fields:
        data = decision.get(field)
        if not data:
            errors.append(f"Missing decision field: {field}")
            continue
            
        causality = data.get("causality")
        if not causality:
            errors.append(f"Field {field} missing causality block")
            continue
            
        for key in causality_keys:
            if key not in causality or not causality[key]:
                errors.append(f"Causality in {field} missing key: {key}")

    # 2. Check Evidence Chain Expansion
    chain_path = project_root / "data" / "ops" / "decision_evidence_chain.json"
    if not chain_path.exists():
        errors.append("Missing decision_evidence_chain.json")
    else:
        with open(chain_path, "r", encoding="utf-8") as f:
            chain = json.load(f)
            if "causality_chain" not in chain:
                errors.append("Evidence chain missing causality_chain")

    # 3. Check Standalone Causality File
    causal_file = project_root / "data" / "ops" / "decision_causality_chain.json"
    if not causal_file.exists():
        errors.append("Missing decision_causality_chain.json")

    # 4. Check Script Engine Alignment (JSON)
    script_path = project_root / "data" / "content" / "today_video_script.json"
    if script_path.exists():
        with open(script_path, "r", encoding="utf-8") as f:
            script = json.load(f)
            if not script.get("causality_link"):
                errors.append("Video script JSON missing causality_link confirmation")

    if errors:
        print("❌ [STEP-D] Causality Verification Failed:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("✅ [STEP-D] Decision Causality Verification Passed!")
        print("   Structural Chain: ENABLED")
        print("   Script Alignment: ENABLED")
        return True

if __name__ == "__main__":
    test_causality_integrity()
