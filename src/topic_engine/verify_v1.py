import os
import json
from pathlib import Path
from src.agents.detector import DetectorAgent

def verify_v1_engine():
    # Set up environment
    os.environ["HOIN_BASE_DIR"] = str(Path(__file__).resolve().parents[2])
    
    print("🔍 Testing Topic Selection Engine v1.0...")
    agent = DetectorAgent()
    agent.today = "20260422" # Force use latest data
    agent.raw_dir = agent.base_dir / f"data/raw/{agent.today}"
    agent.signal_dir = agent.base_dir / f"data/signals/{agent.today}"
    agent.signal_dir.mkdir(parents=True, exist_ok=True)
    
    results = agent.run()
    
    print("\n--- Topic Selection Results ---")
    if results.get("selected") and results["selected"].get("MAIN"):
        main = results["selected"]["MAIN"]
        print(f"🏆 MAIN Topic: {main['event']}")
        print(f"📊 Final Score: {main['final_score']}")
        print(f"💡 Why Now: {main['evaluation']['why_now_summary']}")
    else:
        print("❌ MAIN Topic selection failed.")

    # Check for output files
    topic_dir = Path(os.environ["HOIN_BASE_DIR"]) / "data/topics"
    files = ["topic_candidates.json", "topic_evaluations.json", "topic_selection.json"]
    for f in files:
        if (topic_dir / f).exists():
            print(f"✅ Created: {f}")
        else:
            print(f"❌ Missing: {f}")

if __name__ == "__main__":
    verify_v1_engine()
