import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ops.run_daily_pipeline import run_decision_normalization

if __name__ == "__main__":
    print(">>> Starting STEP-C Provenance Run...")
    success = run_decision_normalization()
    if success:
        print("✅ Provenance Run Completed.")
    else:
        print("❌ Provenance Run Failed.")
