import os
import sys
from pathlib import Path

# Add root to sys.path
sys.path.append(os.getcwd())

from src.agents.collector import CollectorAgent
from src.agents.writer import WriterAgent
from src.agents.publisher import PublisherAgent

def run_local_pipeline():
    today = "20260508"
    round_num = os.environ.get("HOIN_TARGET_ROUND", "3")
    
    print(f"🚀 [LOCAL_PIPELINE] Round {round_num} Start")
    
    # [COST_RESET] 세션 비용 초기화
    cost_path = Path("data/monitoring/session_cost.json")
    if cost_path.exists():
        import json
        from datetime import datetime
        cost_path.write_text(json.dumps({"session_cost": 0.0, "last_updated": datetime.now().isoformat()}))
    
    # 1. Collect
    collector = CollectorAgent()
    collector.run()
    
    # 2. Write (This now includes Arbiter/Strategic Hunt)
    writer = WriterAgent()
    writer.run()
    
    # 3. Publish
    publisher = PublisherAgent()
    publisher.run()
    
    print(f"✅ [LOCAL_PIPELINE] Round {round_num} Complete")

if __name__ == "__main__":
    run_local_pipeline()
