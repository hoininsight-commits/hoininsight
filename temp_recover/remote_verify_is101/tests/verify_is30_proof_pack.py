import os
import json
import sys
from pathlib import Path

# Add root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.proof_pack import ProofPackEngine
from src.issuesignal.dashboard.models import DecisionCard

def verify_is30():
    base_dir = Path(".")
    engine = ProofPackEngine(base_dir)
    
    print("--- IS-30 Verification Start ---")
    
    # Test Case 1: PASS (2 independent sources)
    card_pass = DecisionCard(topic_id="T1", title="Pass Test", status="TRUST_LOCKED", tickers=[{"symbol": "AAPL"}])
    artifacts_pass = [
        {
            "tickers": ["AAPL"],
            "hard_facts": [
                {"fact_type": "CONTRACT", "source_kind": "FILING", "independence_key": "K1"},
                {"fact_type": "CAPEX", "source_kind": "GOV", "independence_key": "K2"}
            ]
        }
    ]
    res_pass, logs_pass = engine.process_card(card_pass, artifacts_pass)
    assert res_pass.status == "TRUST_LOCKED", f"Failed PASS case: {res_pass.status}"
    assert len(res_pass.proof_packs) == 1, "Proof pack missing in PASS case"
    assert res_pass.proof_packs[0].proof_status == "PROOF_OK"
    print("✅ TEST 1: PASS Case (2 independent sources) verified.")

    # Test Case 2: FAIL (Only 1 source)
    card_fail = DecisionCard(topic_id="T2", title="Fail Test", status="TRUST_LOCKED", tickers=[{"symbol": "TSLA"}])
    artifacts_fail = [
        {
            "tickers": ["TSLA"],
            "hard_facts": [
                {"fact_type": "CONTRACT", "source_kind": "FILING", "independence_key": "K1"}
            ]
        }
    ]
    res_fail, logs_fail = engine.process_card(card_fail, artifacts_fail)
    assert res_fail.status == "REJECT", f"Failed FAIL case (1 source): {res_fail.status}"
    assert res_fail.reason == "NO_PROOF_TICKER"
    print("✅ TEST 2: FAIL Case (Only 1 source) verified.")

    # Test Case 3: FAIL (2 sources, not independent - same key)
    card_dep = DecisionCard(topic_id="T3", title="Dependency Test", status="TRUST_LOCKED", tickers=[{"symbol": "NVDA"}])
    artifacts_dep = [
        {
            "tickers": ["NVDA"],
            "hard_facts": [
                {"fact_type": "CONTRACT", "source_kind": "FILING", "independence_key": "K1"},
                {"fact_type": "EARNINGS", "source_kind": "FILING", "independence_key": "K1"} # Same key
            ]
        }
    ]
    res_dep, logs_dep = engine.process_card(card_dep, artifacts_dep)
    assert res_dep.status == "REJECT", f"Failed FAIL case (duplicate key): {res_dep.status}"
    print("✅ TEST 3: FAIL Case (Same independence key) verified.")

    # Test Case 4: Downgrade to HOLD (Partial Pass)
    card_partial = DecisionCard(topic_id="T4", title="Partial Test", status="TRUST_LOCKED", 
                                tickers=[{"symbol": "MSFT"}, {"symbol": "GOOG"}])
    artifacts_partial = [
        {
            "tickers": ["MSFT"],
            "hard_facts": [
                {"fact_type": "CONTRACT", "source_kind": "FILING", "independence_key": "K1"},
                {"fact_type": "CAPEX", "source_kind": "GOV", "independence_key": "K2"}
            ]
        },
        {
            "tickers": ["GOOG"],
            "hard_facts": [
                {"fact_type": "CONTRACT", "source_kind": "FILING", "independence_key": "K3"}
            ]
        }
    ]
    res_partial, logs_partial = engine.process_card(card_partial, artifacts_partial)
    assert res_partial.status == "HOLD", f"Failed Downgrade case: {res_partial.status}"
    assert len(res_partial.tickers) == 1, "Ticker GOOG should have been removed"
    assert res_partial.tickers[0]["symbol"] == "MSFT"
    print("✅ TEST 4: Downgrade Case (Partial Pass) verified.")

    print("--- IS-30 Verification SUCCESS ---")

if __name__ == "__main__":
    try:
        verify_is30()
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
