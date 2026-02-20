
import json
import sys
from pathlib import Path

# Add src to path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from src.ops.narrative_compressor import NarrativeCompressor

def test_narrative_compression():
    # Mock pattern data
    pattern_data = {
        "pattern_type": "SYSTEM_TRUST_STRESS",
        "narrative": "중앙은행의 통제력이나 시스템 신뢰에 대한 의구심이 확산되고 있습니다.",
        "signals": ["Central Bank Narrative", "Safe Haven Interest"]
    }
    
    # Mock replay block (with historical case)
    replay_block = {
        "replay_found": True,
        "similar_cases": [
            {
                "pattern_id": "SYSTEM_TRUST_STRESS",
                "first_seen": "2025-12-28T00:00:00Z",
                "common_features": ["Central Bank Narrative", "Safe Haven Interest"],
                "outcome": {
                    "sector_movement": "Gold and Safe Haven assets",
                    "volatility": "High",
                    "result_type": "Defensive"
                }
            }
        ],
        "common_points": "Similar pattern detected 1 time(s) in history.",
        "differences": "Current context may differ in timing or intensity."
    }
    
    # Mock context
    context = {
        "intensity": "DEEP_HUNT",
        "why_now": "POLICY_SHIFT"
    }
    
    # Compress
    narrative = NarrativeCompressor.compress(pattern_data, replay_block, context)
    
    # Verify
    print("📝 Generated Narrative:")
    print(f"Title: {narrative['title']}")
    print(f"Body: {narrative['body']}")
    print(f"Sentence Count: {narrative['sentence_count']}")
    
    # 1. Check sentence count (3-5)
    if 3 <= narrative['sentence_count'] <= 5:
        print("✅ Sentence count is within range (3-5)")
    else:
        print(f"❌ Sentence count out of range: {narrative['sentence_count']}")
        sys.exit(1)
    
    # 2. Check for banned words
    banned_found = []
    for word in NarrativeCompressor.BANNED_WORDS:
        if word in narrative['body'] or word in narrative['title']:
            banned_found.append(word)
    
    if banned_found:
        print(f"❌ Banned words found: {banned_found}")
        sys.exit(1)
    else:
        print("✅ No banned words detected")
    
    # 3. Check historical context is included
    if "2025-12-28" in narrative['body'] or "과거" in narrative['body']:
        print("✅ Historical context included")
    else:
        print("❌ Historical context missing")
        sys.exit(1)
    
    print("\nSUCCESS: Step 87 Narrative Compression Verified.")

if __name__ == "__main__":
    try:
        test_narrative_compression()
    except Exception as e:
        print(f"Runtime Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
