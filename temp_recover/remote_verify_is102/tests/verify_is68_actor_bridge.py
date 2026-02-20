from src.issuesignal.actor_bridge import ActorBridgeEngine

def test_actor_bridge_logic():
    macro_facts = [
        {
            "fact_text": "US 10Y Yield spiked by 1.2% today.",
            "source": "Yahoo Finance",
            "evidence_grade": "HARD_FACT",
            "details": {
                "ticker": "US10Y",
                "change_pct": 1.2
            }
        },
        {
            "fact_text": "WTI Oil slightly increased.",
            "source": "MarketWatch",
            "evidence_grade": "MEDIUM",
            "details": {
                "ticker": "WTI",
                "change_pct": 0.2
            }
        }
    ]
    
    candidates = ActorBridgeEngine.bridge(macro_facts)
    
    print(f"Total promoted candidates: {len(candidates)}")
    for c in candidates:
        details = c['details']
        print(f"--- Promoted: {details['actor_name_ko']} ---")
        print(f"Type: {details['actor_type']}")
        print(f"Confidence: {details['actor_confidence']}")
        print(f"Reason: {details['actor_reason_ko']}")
        print(f"Evidence: {details['actor_evidence'][0]['grade']}")
        
    # Check assertions
    assert len(candidates) >= 1
    assert candidates[0]['details']['actor_name_ko'] == "미국 장기채"
    assert candidates[0]['details']['actor_confidence'] >= 80

if __name__ == "__main__":
    test_actor_bridge_logic()
    print("\n[VERIFY] IS-68 Actor Bridge Unit Test Passed!")
