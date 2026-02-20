import os
import json
import sys
from pathlib import Path

# Add root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.quote_proof import QuoteProofEngine
from src.issuesignal.dashboard.models import DecisionCard, TriggerQuote

def verify_is31():
    base_dir = Path(".")
    engine = QuoteProofEngine(base_dir)
    
    print("--- IS-31 Verification Start ---")
    
    # 1) OFFICIAL_TRANSCRIPT only with full context → PASS
    card1 = DecisionCard(topic_id="C1", title="Transcript Test", status="TRUST_LOCKED")
    art1 = [{"trigger_quotes": [{"excerpt": "We will wait.", "fact_type": "OFFICIAL_TRANSCRIPT", "source_kind": "REGULATOR", "source_ref": "fed_link"}]}]
    res1, logs1 = engine.process_card(card1, art1)
    assert res1.trigger_quote.verification_status == "PASS", f"Scenario 1 failed: {res1.trigger_quote.verification_status}"
    print("✅ Scenario 1: Transcript PASS verified.")

    # 2) Strong+Medium independent → PASS
    card2 = DecisionCard(topic_id="C2", title="Independence Test", status="TRUST_LOCKED")
    art2 = [
        {"trigger_quotes": [{"excerpt": "Policy Change.", "fact_type": "OFFICIAL_STATEMENT", "source_kind": "GOV", "source_ref": "gov_link"}]},
        {"trigger_quotes": [{"excerpt": "Policy Change.", "fact_type": "OFFICIAL_STATEMENT", "source_kind": "OFFICIAL_PRESS", "source_ref": "press_link"}]}
    ]
    res2, logs2 = engine.process_card(card2, art2)
    assert res2.trigger_quote.verification_status == "PASS", "Scenario 2 failed"
    print("✅ Scenario 2: Strong+Medium PASS verified.")

    # 3) Single news article quoting “official said” without link → HOLD
    card3 = DecisionCard(topic_id="C3", title="Vague Test", status="TRUST_LOCKED")
    art3 = [{"trigger_quotes": [{"excerpt": "Official said the deal is off.", "fact_type": "OFFICIAL_STATEMENT", "source_kind": "NEWS", "source_ref": "news_link"}]}]
    res3, logs3 = engine.process_card(card3, art3)
    assert res3.status == "HOLD", f"Scenario 3 failed: {res3.status}"
    assert res3.trigger_quote.reason_code == "HOLD:VAGUE_QUOTE"
    print("✅ Scenario 3: Vague News HOLD verified.")

    # 4) Two articles citing same press release → REJECT (NON_INDEPENDENT)
    card4 = DecisionCard(topic_id="C4", title="Non-Independent Test", status="TRUST_LOCKED")
    art4 = [
        {"trigger_quotes": [{"excerpt": "Fixed.", "fact_type": "OFFICIAL_STATEMENT", "source_kind": "NEWS", "source_ref": "PR_001"}]},
        {"trigger_quotes": [{"excerpt": "Fixed.", "fact_type": "OFFICIAL_STATEMENT", "source_kind": "NEWS", "source_ref": "PR_001"}]}
    ]
    res4, logs4 = engine.process_card(card4, art4)
    assert res4.status == "REJECT", f"Scenario 4 failed: {res4.status}"
    assert res4.trigger_quote.reason_code == "REJECT:WIRE_CHAIN_DUPLICATION"
    print("✅ Scenario 4: Non-Independent REJECT verified.")

    # 5) Quote exceeds 2 lines / >240 chars → HOLD
    card5 = DecisionCard(topic_id="C5", title="Length Test", status="TRUST_LOCKED")
    long_quote = "A" * 241
    art5 = [{"trigger_quotes": [{"excerpt": long_quote, "fact_type": "OFFICIAL_STATEMENT", "source_kind": "GOV", "source_ref": "gov_link"}]}]
    res5, logs5 = engine.process_card(card5, art5)
    assert res5.status == "HOLD", f"Scenario 5 failed: {res5.status}"
    assert res5.trigger_quote.reason_code == "HOLD:LENGTH_EXCEEDED"
    print("✅ Scenario 5: Long Quote HOLD verified.")

    # 6) Calendar event schedule line item with explicit date/time → PASS
    card6 = DecisionCard(topic_id="C6", title="Calendar Test", status="TRUST_LOCKED")
    art6 = [{"trigger_quotes": [{"excerpt": "Hearing: 10:00 AM Jan 30", "fact_type": "CALENDAR_ITEM", "source_kind": "COURT", "source_ref": "docket"}]}]
    res6, logs6 = engine.process_card(card6, art6)
    assert res6.trigger_quote.verification_status == "PASS"
    print("✅ Scenario 6: Calendar PASS verified.")

    print("--- IS-31 Verification SUCCESS ---")

if __name__ == "__main__":
    try:
        verify_is31()
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
