import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.memory_engine import MemoryEngine

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal Market Memory Engine Verification (IS-23)")
    
    # Ensure fresh storage for test
    memory_file = base_dir / "data" / "issuesignal" / "market_memory.json"
    if memory_file.exists():
        memory_file.unlink()
    
    engine = MemoryEngine(base_dir)
    
    # 1. First Issuance
    print("\n[STEP 1] Recording first trigger...")
    t1 = {
        "issue_id": "IS-2026-01-29-001",
        "root_cause": "SUBSIDY_CUT",
        "actor": "GOVERNMENT",
        "destination": "CHIP_CAPEX",
        "irreversible": True
    }
    engine.record_issuance(t1)
    
    # 2. Immediate Duplicate Check (High Overlap)
    print("\n[STEP 2] Checking immediate duplicate (100% overlap)...")
    t2 = t1.copy()
    is_dupe, reason = engine.check_duplication(t2)
    print(f" - Duplicate detected? {is_dupe}")
    print(f" - Reason: {reason}")
    
    # 3. Variation Check (50% overlap, safe)
    print("\n[STEP 3] Checking variation (50% overlap, different destination/actor)...")
    t3 = t1.copy()
    t3["actor"] = "BIGTECH"
    t3["destination"] = "AI_SERVER"
    is_dupe3, reason3 = engine.check_duplication(t3)
    print(f" - Duplicate detected? {is_dupe3}")
    
    # 4. Mocking "Soft Lock" (21 days later)
    print("\n[STEP 4] Mocking 22-day old memory (Soft Lock)...")
    with open(memory_file, "r") as f:
        mems = json.load(f)
    mems[0]["timestamp"] = (datetime.now() - timedelta(days=22)).isoformat()
    with open(memory_file, "w") as f:
        json.dump(mems, f)
        
    engine = MemoryEngine(base_dir) # Reload
    # High overlap (100%) but same destination -> soft lock should hit if no change
    is_dupe4, reason4 = engine.check_duplication(t1)
    print(f" - Soft lock hit for same structure? {is_dupe4}")
    print(f" - Reason: {reason4}")
    
    # High overlap but different destination -> should pass soft lock
    t5 = t1.copy()
    t5["destination"] = "HBM_LINE"
    is_dupe5, _ = engine.check_duplication(t5)
    print(f" - Pass soft lock with different destination? {not is_dupe5}")

    # 5. Mocking "Expiry" (46 days later)
    print("\n[STEP 5] Mocking 46-day old memory (Expiry)...")
    mems[0]["timestamp"] = (datetime.now() - timedelta(days=46)).isoformat()
    with open(memory_file, "w") as f:
        json.dump(mems, f)
        
    engine = MemoryEngine(base_dir) # Reload
    is_dupe6, _ = engine.check_duplication(t1)
    print(f" - Duplicate detected after 45 days? {is_dupe6} (Expected: False)")

    if is_dupe and not is_dupe3 and is_dupe4 and not is_dupe5 and not is_dupe6:
        print("\n[VERIFY][SUCCESS] IssueSignal Market Memory Engine (IS-23) is fully functional.")
    else:
        print("\n[VERIFY][FAIL] Verification failed.")

if __name__ == "__main__":
    main()
