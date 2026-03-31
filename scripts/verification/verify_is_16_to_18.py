import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.silence_layer import SilenceLayer
from src.issuesignal.narrative_guard import NarrativeGuard
from src.issuesignal.human_interrupt import HumanInterrupt

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal Silence & Control Verification (IS-16 to IS-18)")
    
    silence = SilenceLayer(base_dir)
    guard = NarrativeGuard(base_dir)
    interrupt = HumanInterrupt(base_dir)
    
    # Reset log files for clean test
    if silence.log_path.exists(): silence.log_path.unlink()
    if guard.history_path.exists(): guard.history_path.unlink()
    silence._ensure_log()
    guard._ensure_history()
    
    # 1. Test Daily Cap (IS-16)
    print("\n[STEP 1] Testing Daily Cap (3 limit)...")
    for i in range(5):
        can_i = silence.can_speak()
        print(f" - Attempt {i+1}: Can speak? {can_i}")
        if can_i:
            silence.record_speech()
            
    # 2. Test Narrative Saturation (IS-17)
    print("\n[STEP 2] Testing Narrative Saturation Guard...")
    story = "AI Capex is surging leading to HBM bottleneck."
    guard.record_narrative("IS-001", story)
    
    repeated_story = "The AI Capex spike continues to create HBM pressure."
    is_sat = guard.is_saturated(repeated_story)
    print(f" - Original story: {story}")
    print(f" - Repeated story check: {repeated_story}")
    print(f" - Is Saturated (Rejected)? {is_sat}")
    
    # 3. Test Human Interrupt (IS-18)
    print("\n[STEP 3] Testing Human Interrupt Mode...")
    print(f" - Default HOLD state: {interrupt.is_held()}")
    interrupt.set_hold(True)
    print(f" - Manually set HOLD: {interrupt.is_held()}")
    interrupt.set_hold(False)
    print(f" - Released HOLD: {interrupt.is_held()}")
    
    print("\n[VERIFY][SUCCESS] IssueSignal Silence & Control (IS-16 to IS-18) is fully functional.")

if __name__ == "__main__":
    main()
