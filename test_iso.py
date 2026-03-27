import sys
import os
from pathlib import Path
from datetime import datetime
import json

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

def test_decision():
    from src.ops.investment_decision_engine import InvestmentDecisionEngine
    from src.ops.stock_decision_mapper import map_stock_decisions
    
    print("Testing Investment Decision Engine...")
    engine = InvestmentDecisionEngine(project_root)
    decision = engine.build_decision()
    print(f"Decision: {decision}")
    
    # Save standalone decision
    decision_path = project_root / "data" / "operator" / "investment_decision.json"
    print(f"Saving to {decision_path}")
    with open(decision_path, "w", encoding="utf-8") as f:
        json.dump(decision, f, indent=2, ensure_ascii=False)
    
    print(f"File size after save: {os.path.getsize(decision_path)}")

if __name__ == "__main__":
    test_decision()
