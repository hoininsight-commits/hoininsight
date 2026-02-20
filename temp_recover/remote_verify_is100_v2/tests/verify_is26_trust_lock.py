import sys
from pathlib import Path
import json

# Add root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.trust_lock import TrustLockEngine

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal Human Trust Lock Verification (IS-26)")
    
    engine = TrustLockEngine(base_dir)
    
    # 1. CASE 1: Perfect Structure -> TRUST_LOCKED
    print("\n[CASE 1] Testing TRUST_LOCKED (Perfect Structure)...")
    card_1 = {
        "what": "AI 보조금 삭감 집행",
        "why": "구조적 재정 적자 임계점 도달",
        "who": "GOVERNMENT",
        "where": "CHIP_DOMESTIC_CAPEX",
        "kill_switch": "세수 증대 시 무효화",
        "narrative": "오늘 보조금 삭감이 발생했고, 자본은 이동해야 한다."
    }
    state_1, fails_1, sig_1 = engine.evaluate(card_1, is_fact_passed=True, has_duplicate=False)
    print(f" - State: {state_1} (Fails: {fails_1})")
    print(f" - Signature: {sig_1}")

    # 2. CASE 2: Fact Integrity Fail -> REJECT
    print("\n[CASE 2] Testing REJECT (Fact Integrity Fail)...")
    state_2, fails_2, _ = engine.evaluate(card_1, is_fact_passed=False, has_duplicate=False)
    print(f" - State: {state_2} (Fails: {fails_2})")

    # 3. CASE 3: Incomplete Structure (Missing Kill Switch) -> REJECT
    print("\n[CASE 3] Testing REJECT (Missing Kill Switch)...")
    card_3 = card_1.copy()
    del card_3["kill_switch"]
    state_3, fails_3, _ = engine.evaluate(card_3, is_fact_passed=True, has_duplicate=False)
    print(f" - State: {state_3} (Fails: {fails_3})")

    # 4. CASE 4: Vague Expression -> HOLD
    print("\n[CASE 4] Testing HOLD (Vague Expression - '가능성')...")
    card_4 = card_1.copy()
    card_4["narrative"] = "보조금이 삭감될 가능성이 보인다."
    state_4, fails_4, _ = engine.evaluate(card_4, is_fact_passed=True, has_duplicate=False)
    print(f" - State: {state_4} (Fails: {fails_4})")

    # 5. CASE 5: Duplicate Structure -> REJECT
    print("\n[CASE 5] Testing REJECT (Duplicate Structure)...")
    state_5, fails_5, _ = engine.evaluate(card_1, is_fact_passed=True, has_duplicate=True)
    print(f" - State: {state_5} (Fails: {fails_5})")

    # 6. CASE 6: Low Readability (Over complex/long) -> HOLD
    print("\n[CASE 6] Testing HOLD (Low Readability - Over 200 chars)...")
    card_6 = card_1.copy()
    card_6["why"] = "이것은 매우 복잡한 구조적 문제로 인해 발생하는 현상이며, 자본의 흐름이 급격하게 변동할 수밖에 없는 필연적인 이유를 설명하기 위해 200자가 넘는 긴 문장을 작성하여 가독성을 테스트하는 목적을 가지고 있습니다. " * 3
    state_6, fails_6, _ = engine.evaluate(card_6, is_fact_passed=True, has_duplicate=False)
    print(f" - State: {state_6} (Fails: {fails_6})")

    # Final tally
    if state_1 == "TRUST_LOCKED" and state_2 == "REJECT" and state_3 == "REJECT" and \
       state_4 == "HOLD" and state_5 == "REJECT" and state_6 == "HOLD":
        print("\n[VERIFY][SUCCESS] IssueSignal Human Trust Lock Engine (IS-26) is fully functional.")
    else:
        print("\n[VERIFY][FAIL] Verification failed.")

if __name__ == "__main__":
    main()
