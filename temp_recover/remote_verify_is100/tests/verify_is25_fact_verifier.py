import sys
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.fact_verifier import FactVerifier, SourceType

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal Fact Verifier Verification (IS-25)")
    
    verifier = FactVerifier(base_dir)
    
    # CASE 1: PASS - GOV_DOC + COMPANY_FILINGS
    print("\n[CASE 1] Testing PASS (GOV_DOC + COMPANY_FILINGS)...")
    ev_1 = {
        "evidence": [
            {"text": "Subsidy cut bill signed", "source_type": "GOV_DOC", "is_original": True},
            {"text": "Factory expansion halted", "source_type": "COMPANY_FILINGS", "is_original": True}
        ]
    }
    passed_1, reason_1, debug_1 = verifier.verify({}, ev_1)
    print(f" - Result: {'PASS' if passed_1 else 'REJECT'} (Reason: {reason_1})")

    # CASE 2: PASS - COMPANY_FILINGS + FLOW_DATA
    print("\n[CASE 2] Testing PASS (COMPANY_FILINGS + FLOW_DATA)...")
    ev_2 = {
        "evidence": [
            {"text": "Official order cancellation", "source_type": "COMPANY_FILINGS", "is_original": True},
            {"text": "Capital outflow from semiconductor ETFs", "source_type": "FLOW_DATA", "is_original": True}
        ]
    }
    passed_2, _, _ = verifier.verify({}, ev_2)
    print(f" - Result: {'PASS' if passed_2 else 'REJECT'}")

    # CASE 3: PASS - REGULATORY + PHYSICAL_DATA
    print("\n[CASE 3] Testing PASS (REGULATORY + PHYSICAL_DATA)...")
    ev_3 = {
        "evidence": [
            {"text": "Export license denied", "source_type": "REGULATORY", "is_original": True},
            {"text": "Lead times increased to 40 weeks", "source_type": "PHYSICAL_DATA", "is_original": True}
        ]
    }
    passed_3, _, _ = verifier.verify({}, ev_3)
    print(f" - Result: {'PASS' if passed_3 else 'REJECT'}")

    # CASE 4: REJECT - MAJOR_MEDIA 단독
    print("\n[CASE 4] Testing REJECT (MAJOR_MEDIA only)...")
    ev_4 = {
        "evidence": [
            {"text": "Bloomberg reports potential subsidy cut", "source_type": "MAJOR_MEDIA", "is_original": True}
        ]
    }
    passed_4, reason_4, _ = verifier.verify({}, ev_4)
    print(f" - Result: {'PASS' if passed_4 else 'REJECT'} (Reason: {reason_4})")

    # CASE 5: REJECT - ANALYST_REPORT 단독
    print("\n[CASE 5] Testing REJECT (ANALYST_REPORT only)...")
    ev_5 = {
        "evidence": [
            {"text": "Morgan Stanley predicts supply glut", "source_type": "ANALYST_REPORT", "is_original": True}
        ]
    }
    passed_5, reason_5, _ = verifier.verify({}, ev_5)
    print(f" - Result: {'PASS' if passed_5 else 'REJECT'} (Reason: {reason_5})")

    # CASE 6: REJECT - 동일 기사 재인용 (No Original)
    print("\n[CASE 6] Testing REJECT (Redundant Re-quoting)...")
    ev_6 = {
        "evidence": [
            {"text": "Reuters reports X", "source_type": "MAJOR_MEDIA", "is_original": True},
            {"text": "Local news quotes Reuters reporting X", "source_type": "MAJOR_MEDIA", "is_original": False}
        ]
    }
    passed_6, reason_6, _ = verifier.verify({}, ev_6)
    print(f" - Result: {'PASS' if passed_6 else 'REJECT'} (Reason: {reason_6})")

    # CASE 7: REJECT - 발언만 존재 (Speech only but same type)
    print("\n[CASE 7] Testing REJECT (Single Type - Speech only)...")
    ev_7 = {
        "evidence": [
            {"text": "CEO said X", "source_type": "EARNINGS_CALL", "is_original": True}
        ]
    }
    passed_7, reason_7, _ = verifier.verify({}, ev_7)
    print(f" - Result: {'PASS' if passed_7 else 'REJECT'} (Reason: {reason_7})")

    if all([passed_1, passed_2, passed_3, not passed_4, not passed_5, not passed_6, not passed_7]):
        print("\n[VERIFY][SUCCESS] IssueSignal Fact Verifier (IS-25) is fully functional.")
    else:
        print("\n[VERIFY][FAIL] Verification failed.")

if __name__ == "__main__":
    main()
