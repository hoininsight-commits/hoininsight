import sys
import os
from pathlib import Path
from datetime import datetime
import json

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.ops.run_daily_pipeline import (
    run_operator_brief_builder,
    run_consistency_engine,
    run_investment_decision,
    run_execution_tracking,
    run_performance_evaluation,
    run_risk_engine,
    run_learning_update,
    run_capital_allocation
)

def debug_allocation():
    print("--- DEBUG ALLOCATION START ---")
    run_operator_brief_builder()
    run_consistency_engine()
    run_investment_decision()
    run_execution_tracking()
    run_performance_evaluation()
    run_risk_engine()
    run_learning_update()
    run_capital_allocation()
    print("--- DEBUG ALLOCATION COMPLETED ---")
    
    brief_path = project_root / "data" / "operator" / "today_operator_brief.json"
    if brief_path.exists():
        with open(brief_path, "r") as f:
            brief = json.load(f)
            print(f"Portfolio in brief: {'portfolio_allocation' in brief}")
            if 'portfolio_allocation' in brief:
                exposure = brief['portfolio_allocation']['theme_exposure']
                print(f"Theme Exposure: {exposure}")
                for a in brief['portfolio_allocation']['allocations']:
                    print(f"  - {a['ticker']}: {a['weight']}")

if __name__ == "__main__":
    debug_allocation()
