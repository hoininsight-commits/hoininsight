import os
import json
import subprocess
from pathlib import Path
from src.decision.run_is96_4 import main as run_pipeline

def verify_is96_4():
    print("\n" + "="*60)
    print("📋 IS-96-4 DECISION OUTPUT VERIFICATION")
    print("="*60)

    base_dir = Path(".")
    decision_dir = base_dir / "data/decision"
    
    # 1. Pipeline Execution
    print("\n[1/3] Executing Decision Assembly Pipeline...")
    try:
        run_pipeline()
        print("  ✅ Pipeline Execution: SUCCESS")
    except Exception as e:
        print(f"  ❌ Pipeline Execution: FAILED ({e})")
        return

    # 2. File Persistence & Content Check
    print("\n[2/3] Checking Output Files & Content...")
    files_to_check = [
        "interpretation_units.json",
        "speakability_decision.json",
        "narrative_skeleton.json"
    ]
    
    for filename in files_to_check:
        p = decision_dir / filename
        if p.exists():
            print(f"  ✅ {filename}: EXISTS")
            try:
                data = json.loads(p.read_text(encoding='utf-8'))
                if data:
                    print(f"     - Content check: OK ({type(data).__name__})")
                    if filename == "speakability_decision.json":
                        for unit_id, decision in data.items():
                            if "speakability_flag" in decision:
                                print(f"     - Flag found for {unit_id[:8]}: {decision['speakability_flag']}")
                else:
                    print(f"     - ⚠️ {filename}: EMPTY")
            except Exception as e:
                print(f"     - ❌ {filename}: JSON PARSE ERROR ({e})")
        else:
            print(f"  ❌ {filename}: MISSING")

    # 3. Constitutional Integrity Check (Add-only)
    print("\n[3/3] Constitutional Integrity Check (Add-only)...")
    forbidden = [
        "docs/DATA_COLLECTION_MASTER.md",
        "docs/BASELINE_SIGNALS.md",
        "docs/ANOMALY_DETECTION_LOGIC.md"
    ]
    # Standard Restoration Baseline
    BASELINE = "d17bb99dc"
    for doc in forbidden:
        try:
            diff = subprocess.check_output(["git", "diff", "HEAD", "--", doc]).decode("utf-8")
            if diff:
                print(f"  ❌ {doc}: INTEGRITY BREACH! Unsaved modifications detected.")
            else:
                print(f"  ✅ {doc}: Integrity OK (No modifications)")
        except:
             print(f"  ⚠️ {doc}: Git check failed.")

    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    verify_is96_4()
