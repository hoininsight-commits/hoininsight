import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.issuesignal.pre_trigger import PreTriggerEngine

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal PRE-TRIGGER Engine Verification (IS-21)")
    
    engine = PreTriggerEngine(base_dir)
    
    # 1. Success Case: Structurally inevitable event
    print("\n[STEP 1] Testing Valid PRE-TRIGGER Content...")
    data_ok = {
        "event": "보조금 삭감안 서명",
        "actor": "TSM",
        "action": "공장 가동 중단",
        "locked_reason": "전력 예비율 1% 돌파 및 추가 공급 불가",
        "commitment": "메인 변압기 주문 취소 및 외주 장비 반입 중단",
        "kill_switch_signal": "긴급 예비 전력망 조기 준공 공시",
        "tickers": [
            {"ticker": "TSM", "rationale": "가동 중단 시 글로벌 파운드리 병목의 핵심 주체이다."}
        ]
    }
    
    content = engine.generate_pre_content(data_ok)
    if content:
        print("\n--- Compiled PRE-TRIGGER Content Start ---")
        print(content)
        print("--- Compiled PRE-TRIGGER Content End ---")
        
        # Validation
        blocks = content.split("\n\n")
        print(f"\n[STEP 2] Validating Structure...")
        print(f" - Number of blocks: {len(blocks)} (Expected: 8)")
        
        # Template Check
        template_match = "아직 보조금 삭감안 서명은 터지지 않았지만, TSM는 이미 공장 가동 중단을 해야 하는 상태다."
        if template_match in content:
            print(" - [PASS] Headline template matched.")
        else:
            print(" - [FAIL] Headline template mismatch.")
            
    else:
        print(" - [FAIL] Valid PRE-TRIGGER content compilation rejected.")

    # 2. Failure Case: Speculative language
    print("\n[STEP 3] Testing Speculative Language Rejection...")
    data_fail = data_ok.copy()
    data_fail["locked_reason"] = "금리가 인하될 가능성 때문"
    
    content_fail = engine.generate_pre_content(data_fail)
    if not content_fail:
        print(" - [REJECT] Speculative content correctly rejected.")
    else:
        print(f" - [FAIL] Speculative content accepted: {content_fail}")

    if content and len(blocks) == 8 and template_match in content and not content_fail:
        print("\n[VERIFY][SUCCESS] IssueSignal PRE-TRIGGER Engine (IS-21) is fully functional.")
    else:
        print("\n[VERIFY][FAIL] Verification failed.")

if __name__ == "__main__":
    main()
