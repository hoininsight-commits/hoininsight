import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Project Root
root = Path("/Users/jihopa/Downloads/HoinInsight_Remote")
sys.path.append(str(root))

def test_kst_consistency():
    from src.utils.target_date import get_target_ymd, get_now_kst
    
    now_utc = datetime.now(timezone.utc)
    expected_kst = now_utc + timedelta(hours=9)
    ymd = get_target_ymd()
    
    print(f"[VERIFY] KST Date: {ymd}")
    assert ymd == expected_kst.strftime("%Y-%m-%d"), f"Expected {expected_kst.strftime('%Y-%m-%d')}, got {ymd}"
    print(f"[OK] KST logic is consistent.")

def test_top1_preservation():
    from src.ops.whynow_escalation_layer import WhyNowEscalationLayer
    
    layer = WhyNowEscalationLayer(root)
    # Mock topics: one with pre_structural, one without
    mock_topics = [
        {"topic_id": "T1", "pre_structural_signal": {"signal_type": "deadline"}},
        {"topic_id": "T2"} # No pre_structural_signal
    ]
    
    results = layer.evaluate_signals(mock_topics)
    ids = [r["topic_id"] for r in results]
    
    print(f"[VERIFY] Topics after escalation: {ids}")
    assert "T1" in ids and "T2" in ids, f"T2 should be preserved. Got {ids}"
    print(f"[OK] WhyNowEscalationLayer preserves non-pre-structural topics.")

def test_mentionables_expansion():
    from src.topics.mentionables.mentionables_layer import MentionablesLayer
    
    layer = MentionablesLayer(root / "registry/mappings/mentionables_map_v1.yml")
    
    # Mock unit with keyword in narrative, not in interpretation_key
    mock_unit = {
        "interpretation_id": "TEST_ID",
        "interpretation_key": "GENERIC_KEY",
        "structural_narrative": "정책적으로 밸류업 프로그램이 실행되면서 금융주 수혜가 예상됨.",
        "evidence_tags": ["KR_POLICY", "FLOW_ROTATION"], # Added secondary tag for safety
        "target_sector": "금융"
    }
    mock_decision_bundle = {
        "interpretation_units": [mock_unit],
        "script_realization": [{"topic_id": "TEST_ID", "speakability": "READY"}]
    }
    
    results = layer.run(mock_decision_bundle)
    stocks = [m["name"] for r in results for m in r["mentionables"]]
    
    print(f"[VERIFY] Found stocks: {stocks}")
    # "신한지주" or "KB금융" should be found because of "밸류업" keyword in narrative
    assert any(s in stocks for s in ["신한지주", "KB금융"]), f"Should find financial stocks from narrative keywords. Got {stocks}"
    print(f"[OK] MentionablesLayer expanded search scope correctly.")

if __name__ == "__main__":
    try:
        test_kst_consistency()
        test_top1_preservation()
        test_mentionables_expansion()
        print("\n[SUCCESS] All STEP-8 fixes verified.")
    except Exception as e:
        print(f"\n[FAIL] Verification failed: {e}")
        sys.exit(1)
