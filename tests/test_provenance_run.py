import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ops.run_daily_pipeline import run_decision_normalization, run_impact_chain_engine, run_capital_allocation, run_outcome_validation, run_confidence_recalibration
from src.content.script_engine import TodayScriptEngine

if __name__ == "__main__":
    print(">>> Starting STEP-G Full Validation-Weighted Trust Loop Run...")
    success = run_decision_normalization()
    if success:
        print("✅ Provenance & Causality Run Completed.")
        
        success_impact = run_impact_chain_engine()
        if success_impact:
            print("✅ Impact Chain Run Completed.")
            
            success_val = run_outcome_validation()
            if success_val:
                print("✅ Outcome Validation Run Completed.")
                
                success_recal = run_confidence_recalibration()
                if success_recal:
                    print("✅ Confidence Recalibration Run Completed.")
                    
                    success_alloc = run_capital_allocation()
                    if success_alloc:
                        print("✅ Capital Allocation Run Completed.")
                    else:
                        print("❌ Capital Allocation Run Failed.")
                else:
                    print("❌ Confidence Recalibration Run Failed.")
            else:
                print("❌ Outcome Validation Run Failed.")

        print(">>> Starting Script Synthesis...")
        engine = TodayScriptEngine(project_root)
        script = engine.run_synthesis()
        if script:
            print("✅ Script Synthesis Completed.")
        else:
            print("❌ Script Synthesis Failed.")
    else:
        print("❌ Provenance Run Failed.")
