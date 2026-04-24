
import json
import os
from pathlib import Path
from src.core.gemini_client import GeminiClient

def test_causal_logic():
    client = GeminiClient()
    
    # Mock Evidence Bundle (Intel -> Data Center Scenario)
    evidence = {
        "axis": "flow",
        "market_reaction": {"main_asset": "sp500", "intensity": 0.95},
        "related_events": [
            "[NEWS] Intel earnings tonight expected to show massive AI infrastructure growth.",
            "[NEWS] New data center cluster expansion announced in Texas."
        ],
        "social_prediction": [
            "[SOCIAL_HN] AI data centers are devouring local power grids (450 points)"
        ],
        "supporting_assets": [],
        "contradictions": [],
        "event_market_link": ["AI boom -> HW demand -> Supply bottleneck"]
    }

    system_prompt = """You are a elite macro analyst.
 1. Causal Reasoning: Connect current market signals to their 2nd and 3rd order effects (Bottlenecks, Resource Shocks).
 2. Logical Expansion: If AI/DataCenters move, consider Power, Cooling, Copper and Water.
 3. Use only provided data but apply deep logical deduction to predict the next logical bottleneck.
 4. Understand Korean Market Speak & Slang.
"""

    user_prompt = f"""Below is market evidence.
{json.dumps(evidence, indent=2)}

Task:
1. Identify the most plausible reason for the market movement.
2. Explain the mechanism (cause -> effect chain).
3. [CRITICAL] Predictive Reasoning: Predict the 3-stage chain reaction (A -> B -> C) triggered by this topic. (Example: AI Boom -> Data Center Heat -> Water/Power Scarcity).

Output format:
- Why Hypothesis:
- Mechanism:
- Predictive Chain: (Stage1 -> Stage2 -> Stage3)
- Confidence: (High / Medium / Low)
"""

    print("🚀 Sending Predictive Causal Prompt to Gemini...")
    try:
        res = client.call_controlled(f"{system_prompt}\n\n{user_prompt}", agent="TEST_DEBUG", tier=1) # Tier 1 for retries
        print("\n--- [GEMINI RESPONSE] ---")
        print(res)
        print("--------------------------")
        
        if "Water" in res or "Cooling" in res:
            print("\n✅ SUCCESS: Gemini identified the Water/Cooling bottleneck!")
        else:
            print("\n⚠️ PARTIAL: Gemini responded but didn't reach the 'Water' conclusion.")
            
    except Exception as e:
        print(f"\n❌ FAILED: {e}")

if __name__ == "__main__":
    test_causal_logic()
