import json
import os
from pathlib import Path
from src.ops.consistency_repair_engine import ConsistencyRepairEngine

def test_repair():
    root = Path("/Users/jihopa/Downloads/HoinInsight_Remote")
    
    # 1. Prepare Mock Data
    core_state = {
        "core_theme": "AI Power Constraint",
        "commit": "test-commit-123"
    }
    
    mock_brief = {
        "metadata": {"generated_at": "2026-03-24 10:00:00"},
        "display_title": "Generic Market Report",
        "narrative_brief": {
            "title": "Generic Market Report",
            "featured_theme": "AI Evolution", # Mismatched
            "summary": "Old summary"
        },
        "impact_map": {
            "theme": "AI Evolution", # Mismatched
            "mentionable_stocks": [
                {
                    "ticker": "NVIDIA",
                    "name": "NVIDIA",
                    "rationale": "High relevance to Market Equilibrium" # Placeholder
                },
                {
                    "ticker": "Caterpillar",
                    "name": "Caterpillar",
                    "rationale": "" # Empty
                }
            ]
        },
        "content_studio": {
            "selected_topic": "Policy Radar", # Mismatched
            "script": {
                "hook": "Today we talk about Policy..."
            }
        }
    }
    
    # Save mocks
    (root / "data" / "operator").mkdir(parents=True, exist_ok=True)
    with open(root / "data" / "operator" / "core_theme_state.json", "w") as f:
        json.dump(core_state, f)
        
    with open(root / "data" / "ops" / "today_operator_brief.json", "w") as f:
        json.dump(mock_brief, f)

    # 2. Run Repair
    engine = ConsistencyRepairEngine(root)
    repaired = engine.run_repair()
    
    # 3. Assertions
    print(f"Repaired Theme: {repaired['core_theme']}")
    print(f"Repaired Title: {repaired['display_title']}")
    print(f"Repaired Narrative Theme: {repaired['narrative']['title']}")
    print(f"Repaired Topic: {repaired['topic']['name']}")
    
    for s in repaired['impact']['stocks']:
        print(f"Stock: {s['ticker']}, Rationale: {s['rationale']}")
        if "High relevance" in s['rationale']:
            print("❌ FAILURE: Placeholder still exists!")
            return False

    if repaired['core_theme'] != "AI Power Constraint":
        print("❌ FAILURE: Wrong theme!")
        return False
        
    if repaired['narrative']['title'] == "Generic Market Report":
         print("❌ FAILURE: Title not corrected!")
         return False

    print("✅ SUCCESS: Consistency Repair verified.")
    return True

if __name__ == "__main__":
    test_repair()
