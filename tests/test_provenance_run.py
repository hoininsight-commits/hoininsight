import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ops.run_daily_pipeline import run_decision_normalization
from src.content.script_engine import TodayScriptEngine

if __name__ == "__main__":
    print(">>> Starting STEP-D Provenance & Causality Run...")
    success = run_decision_normalization()
    if success:
        print("✅ Provenance & Causality Run Completed.")
        
        print(">>> Starting Script Synthesis...")
        engine = TodayScriptEngine(project_root)
        script = engine.run_synthesis()
        if script:
            print("✅ Script Synthesis Completed.")
        else:
            print("❌ Script Synthesis Failed.")
    else:
        print("❌ Provenance Run Failed.")
