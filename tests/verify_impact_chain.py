import json
from pathlib import Path

def test_impact_chain_integrity():
    project_root = Path(__file__).parent.parent
    brief_path = project_root / "data" / "operator" / "today_operator_brief.json"
    
    if not brief_path.exists():
        print(f"❌ Brief not found at {brief_path}")
        return False
        
    with open(brief_path, "r", encoding="utf-8") as f:
        brief = json.load(f)
        
    impact_chain = brief.get("impact_map", {}).get("structural_impact_chain", [])
    if not impact_chain:
        print("❌ structural_impact_chain missing in brief")
        return False

    mandatory_keys = [
        "ticker", "theme_link", "mechanism_link", "structural_context",
        "industry_link", "company_link", "directness", "impact_reason", "evidence_basis"
    ]
    
    errors = []
    for stock in impact_chain:
        for key in mandatory_keys:
            if key not in stock or not stock[key]:
                errors.append(f"Stock {stock.get('ticker')} missing mandatory key: {key}")
        
        if stock.get("directness") not in ["direct", "indirect", "proxy"]:
            errors.append(f"Stock {stock.get('ticker')} has invalid directness: {stock.get('directness')}")

    # Verify Allocation Shift (Optional Logic Check)
    alloc_path = project_root / "data" / "allocation" / "capital_allocation.json"
    if alloc_path.exists():
        with open(alloc_path, "r", encoding="utf-8") as f:
            alloc_data = json.load(f)
            if not alloc_data.get("allocations"):
                errors.append("Allocation engine returned empty allocations")

    if errors:
        print("❌ [STEP-E] Impact Chain Verification Failed:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("✅ [STEP-E] Decision -> Impact Chain Verification Passed!")
        print(f"   Stocks Tracked: {len(impact_chain)}")
        print("   Structural Integrity: 100%")
        return True

if __name__ == "__main__":
    test_impact_chain_integrity()
