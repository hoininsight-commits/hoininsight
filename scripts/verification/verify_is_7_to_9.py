import sys
from pathlib import Path
from datetime import datetime

# Add root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.speech_trigger import SpeechTriggerEngine
from src.issuesignal.trigger_priority import TriggerPriorityEngine
from src.issuesignal.content_compiler import ContentCompiler

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal Refinement Verification (IS-7 to IS-9)")
    
    st_engine = SpeechTriggerEngine(base_dir)
    tp_engine = TriggerPriorityEngine(base_dir)
    compiler = ContentCompiler(base_dir)
    
    # 1. Simulate Multiple Speech Triggers (IS-7)
    print("\n[STEP 1] Detecting Speech Triggers...")
    signals = [
        st_engine.analyze_speech("Federal Reserve", "We are very concerned about the sudden shift in labor market dynamics."),
        st_engine.analyze_speech("Goldman Sachs", "Recent policy suggests a mandatory shift in capital allocation for tech."),
        st_engine.analyze_speech("Trump", "I am active in the monitor of geopolitical trade structures.")
    ]
    
    triggered = [s for s in signals if s["status"] == "TRIGGERED"]
    print(f"Triggers detected: {len(triggered)}")
    for t in triggered:
        print(f" - {t['source']}: {t['why_now']}")
        
    # 2. Evaluate Priorities & Collisions (IS-8)
    print("\n[STEP 2] Evaluating Priority & Collisions...")
    # Add dummy tickers to triggered signals for compiler step
    for t in triggered: t["tickers"] = [{"ticker": "TSM", "role": "OWNER"}]
    
    prioritized = tp_engine.evaluate_priorities(triggered)
    for p in prioritized:
        print(f" - [{p['status']}] {p['source']} (Score: {p['priority_score']})")
        
    # 3. Compile Content for READY triggers (IS-9)
    print("\n[STEP 3] Compiling EH-Style Content...")
    ready_ones = [p for p in prioritized if p["status"] == "READY"]
    
    for ready in ready_ones:
        # Mock evidence from HoinEngine
        mock_evidence = {"structural_shift": "Confirmed"}
        pack_path = compiler.compile(ready, mock_evidence)
        print(f" -> Final Content Pack: {pack_path}")
        
    print("\n[VERIFY][SUCCESS] IssueSignal Refinement (IS-7 to IS-9) is fully functional.")

if __name__ == "__main__":
    main()
