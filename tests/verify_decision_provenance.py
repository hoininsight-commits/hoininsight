import json
from pathlib import Path

def test_provenance_structure():
    project_root = Path(__file__).parent.parent
    brief_path = project_root / "data" / "ops" / "today_operator_brief.json"
    
    if not brief_path.exists():
        print(f"❌ Brief not found at {brief_path}")
        return False
        
    with open(brief_path, "r", encoding="utf-8") as f:
        brief = json.load(f)
        
    # Mandatory Fields for STEP-C
    decision = brief.get("investment_decision", {})
    integrity = brief.get("decision_integrity")
    
    mandatory_fields = ["action", "timing", "confidence", "risk", "allocation"]
    errors = []
    
    # 1. Check Decision Provenance
    for field in mandatory_fields:
        data = decision.get(field)
        if not data:
            errors.append(f"Missing field: {field}")
            continue
            
        if not isinstance(data, dict):
            errors.append(f"Field {field} is not a dictionary (must be provenance object)")
            continue
            
        for key in ["value", "source", "reason", "evidence"]:
            if key not in data:
                errors.append(f"Field {field} missing provenance key: {key}")
                
    # 2. Check Integrity
    if not integrity:
        errors.append("Missing decision_integrity metadata")
    else:
        for key in ["fallback_ratio", "status", "engine_fields"]:
            if key not in integrity:
                errors.append(f"Integrity missing key: {key}")
                
    # 3. Check Evidence Chain
    chain_path = project_root / "data" / "ops" / "decision_evidence_chain.json"
    if not chain_path.exists():
        errors.append("Missing decision_evidence_chain.json")
    
    if errors:
        print("❌ [STEP-C] Verification Failed:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("✅ [STEP-C] Decision Provenance Verification Passed!")
        print(f"   Integrity Status: {integrity.get('status')} (Ratio: {integrity.get('fallback_ratio')})")
        return True

if __name__ == "__main__":
    test_provenance_structure()
