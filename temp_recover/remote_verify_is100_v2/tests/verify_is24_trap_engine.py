import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.trap_engine import TrapEngine

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal Trap Detection Engine Verification (IS-24)")
    
    engine = TrapEngine(base_dir)
    
    # CASE 1: PASS - Strong capex + clear actor/must/time + no asymmetry
    print("\n[CASE 1] Testing PASS (Valid Structural Move)...")
    signal_1 = {
        "actor": "GOV",
        "must_item": "HBM_CAPACITY",
        "time_window": "2w",
        "entry_latency": 1,
        "exit_shock": 2
    }
    evidence_1 = {
        "evidence": [
            {"type": "STRONG", "desc": "Official capex expansion announcement with contract numbers."}
        ]
    }
    passed_1, reason_1, debug_1 = engine.evaluate(signal_1, evidence_1)
    print(f" - Result: {'PASS' if passed_1 else 'REJECT'} (Reason: {reason_1})")
    print(f" - Debug: {debug_1}")

    # CASE 2: REJECT - Headline only (NO_CAPITAL_EVIDENCE)
    print("\n[CASE 2] Testing REJECT (NO_CAPITAL_EVIDENCE - Headline only)...")
    signal_2 = signal_1.copy()
    evidence_2 = {
        "evidence": [
            {"type": "WEAK", "desc": "Single news article mentioning potential discussions."}
        ]
    }
    passed_2, reason_2, _ = engine.evaluate(signal_2, evidence_2)
    print(f" - Result: {'PASS' if passed_2 else 'REJECT'} (Reason: {reason_2})")

    # CASE 3: REJECT - Missing Actor (NO_FORCED_BUYER)
    print("\n[CASE 3] Testing REJECT (NO_FORCED_BUYER)...")
    signal_3 = signal_1.copy()
    signal_3["actor"] = "UNKNOWN"
    passed_3, reason_3, _ = engine.evaluate(signal_3, evidence_1)
    print(f" - Result: {'PASS' if passed_3 else 'REJECT'} (Reason: {reason_3})")

    # CASE 4: REJECT - Missing Must Item (NO_MUST_ITEM)
    print("\n[CASE 4] Testing REJECT (NO_MUST_ITEM)...")
    signal_4 = signal_1.copy()
    signal_4["must_item"] = ""
    passed_4, reason_4, _ = engine.evaluate(signal_4, evidence_1)
    print(f" - Result: {'PASS' if passed_4 else 'REJECT'} (Reason: {reason_4})")

    # CASE 5: REJECT - Vague Time Window (NO_TIME_WINDOW)
    print("\n[CASE 5] Testing REJECT (NO_TIME_WINDOW)...")
    signal_5 = signal_1.copy()
    signal_5["time_window"] = "Soon"
    passed_5, reason_5, _ = engine.evaluate(signal_5, evidence_1)
    print(f" - Result: {'PASS' if passed_5 else 'REJECT'} (Reason: {reason_5})")

    # CASE 6: REJECT - Time Asymmetry Trap (Slow entry, Fast exit)
    print("\n[CASE 6] Testing REJECT (TIME_ASYMMETRY_TRAP)...")
    signal_6 = {
        "actor": "GOV",
        "must_item": "HBM_CAPACITY",
        "time_window": "2w",
        "entry_latency": 3, # Slow entry
        "exit_shock": 0     # Instant exit (fragile policy)
    }
    evidence_weak = {
        "evidence": [{"type": "MEDIUM", "desc": "Policy draft published."}] # Not STRONG
    }
    passed_6, reason_6, _ = engine.evaluate(signal_6, evidence_weak)
    print(f" - Result: {'PASS' if passed_6 else 'REJECT'} (Reason: {reason_6})")

    # CASE 7: PASS Exception - EntryLatency long but capital already committed
    print("\n[CASE 7] Testing PASS EXCEPTION (Long latency but strong commitment)...")
    passed_7, reason_7, _ = engine.evaluate(signal_6, evidence_1) # evidence_1 has STRONG type
    print(f" - Result: {'PASS' if passed_7 else 'REJECT'} (Reason: {reason_7})")

    if all([passed_1, not passed_2, not passed_3, not passed_4, not passed_5, not passed_6, passed_7]):
        print("\n[VERIFY][SUCCESS] IssueSignal Trap Detection Engine (IS-24) is fully functional.")
    else:
        print("\n[VERIFY][FAIL] Verification failed.")

if __name__ == "__main__":
    main()
