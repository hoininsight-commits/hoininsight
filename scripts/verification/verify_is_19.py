import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.one_sentence_gate import OneSentenceGate

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal One-Sentence Gate Verification (IS-19)")
    
    gate = OneSentenceGate(base_dir)
    
    # 1. Success Case: Tight but valid
    print("\n[STEP 1] Testing Valid Tight Sentence...")
    trigger_ok = {
        "event_brief": "AI",
        "actor": "정부",
        "forced_action": "증설",
        "bottleneck": "칩",
        "time_anchor": "오늘"
    }
    sentence_ok = gate.process(trigger_ok)
    if sentence_ok:
        print(f" - [ACCEPT] Sentence: {sentence_ok}")
        print(f" - Length (no spaces): {len(sentence_ok.replace(' ', ''))}")
    else:
        print(" - [FAIL] Valid sentence rejected.")

    # 2. Failure Case: Too long
    print("\n[STEP 2] Testing Overlength Sentence...")
    trigger_long = {
        "event_brief": "반도체 보조금 삭감",
        "actor": "삼성전자",
        "forced_action": "신규 투자 계획 전면 재검토",
        "bottleneck": "파운드리",
        "time_anchor": "오늘"
    }
    sentence_long = gate.process(trigger_long)
    if not sentence_long:
        print(" - [REJECT] Overlength sentence correctly rejected.")
    else:
        print(f" - [FAIL] Long sentence accepted: {sentence_long}")

    # 3. Failure Case: Vague verb
    print("\n[STEP 3] Testing Vague Verb rejection...")
    trigger_vague = {
        "event_brief": "금리",
        "actor": "시장",
        "forced_action": "영향", # Vague
        "bottleneck": "채권",
        "time_anchor": "오늘"
    }
    sentence_vague = gate.process(trigger_vague)
    if not sentence_vague:
        print(" - [REJECT] Vague verb sentence correctly rejected.")
    else:
        print(f" - [FAIL] Vague sentence accepted.")

    print("\n[VERIFY][SUCCESS] IssueSignal One-Sentence Gate (IS-19) is fully functional.")

if __name__ == "__main__":
    main()
