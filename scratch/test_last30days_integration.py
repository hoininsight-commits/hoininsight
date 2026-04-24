# scratch/test_last30days_integration.py

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.topic_engine.engine import TopicSelectionEngine

def test_integration():
    print("🧪 Testing TopicSelectionEngine with Social Intelligence...")
    
    # Use real raw data from 어제(4/23) or today
    raw_dir = Path("data/raw/20260424")
    
    # Simple fallback for market.json
    if not (raw_dir / "market.json").exists():
        market_files = sorted(Path("data/raw").glob("*/market.json"))
        if market_files:
            (raw_dir / "market.json").write_text(market_files[-1].read_text())
    
    # Try sentiment.json as well
    if not (raw_dir / "sentiment.json").exists():
        sentiment_files = sorted(Path("data/raw").glob("*/sentiment.json"))
        if sentiment_files:
            (raw_dir / "sentiment.json").write_text(sentiment_files[-1].read_text())

    engine = TopicSelectionEngine(base_dir=Path(os.getcwd()))
    
    # Load all required data into a dict
    raw_data = {}
    for name in ["market", "sentiment", "dart", "social"]:
        p = raw_dir / f"{name}.json"
        if p.exists():
            raw_data[name] = json.loads(p.read_text())
    
    # Add dummy events if sentiment is missing headlines
    if "sentiment" in raw_data:
        if "data" not in raw_data["sentiment"]: raw_data["sentiment"]["data"] = {}
        if "data" not in raw_data["sentiment"]["data"]: raw_data["sentiment"]["data"]["data"] = {}
        
        inner = raw_data["sentiment"]["data"]["data"]
        if not inner.get("news_headlines"):
            print("  ⚠️ No news headlines found, adding dummy data for test...")
            raw_data["sentiment"]["data"]["data"]["news_headlines"] = [
                {"title": "Fed hints at interest rate hike next month", "source": "Reuters"},
                {"title": "Nvidia stocks surge as AI demand peaks", "source": "CNBC"},
                {"title": "Polymarket odds show 80% chance of ceasefire", "source": "Social"}
            ]

    result = engine.run(raw_data)
    
    # Check if social_prediction is in the evidence_bundle
    main_topic = result.get("MAIN")
    if main_topic:
        bundle = main_topic.get("evidence_bundle", {})
        social = bundle.get("social_prediction", [])
        
        print("\n--- TEST RESULT ---")
        print(f"MAIN Topic: {main_topic['event']}")
        print(f"Axis: {main_topic['structure_axis']}")
        print("\n[Evidence Bundle: Social Highlights]")
        if social:
            for item in social:
                print(f"  ✅ {item}")
        else:
            print("  ❌ No social highlights matched for this topic.")
        
        print("\n[Why Hypothesis]")
        print(f"  {main_topic.get('why_hypothesis', 'N/A')}")
        
    else:
        print("❌ No MAIN topic selected. Test failed.")

if __name__ == "__main__":
    test_integration()
