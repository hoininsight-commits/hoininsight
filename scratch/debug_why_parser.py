import json
from pathlib import Path
from src.topic_engine.why_generator import WhyGenerator

def debug_why():
    generator = WhyGenerator()
    evidence = {
        "axis": "flow",
        "market_reaction": {"main_asset": "kospi", "intensity": 4.4},
        "related_events": ["[NEWS] [2026-04-23] Comcast beats revenue, earnings expectations"],
        "social_prediction": [],
        "supporting_assets": [],
        "contradictions": []
    }
    
    print("🚀 Calling Gemini for Debug...")
    hypothesis = generator.generate_hypothesis(evidence)
    
    print("\n--- HYPOTHESIS RESULT ---")
    print(json.dumps(hypothesis, ensure_ascii=False, indent=2))
    
    print("\n--- RAW TEXT CHECK (last_why_raw.txt) ---")
    raw_p = Path("data/debug/last_why_raw.txt")
    if raw_p.exists():
        print(raw_p.read_text())

if __name__ == "__main__":
    debug_why()
