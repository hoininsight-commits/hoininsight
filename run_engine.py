# run_engine.py
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add root to sys.path
sys.path.append(os.getcwd())

from src.topic_engine.engine import TopicSelectionEngine

def load_all_raw_data(raw_dir: Path) -> dict:
    raw_data = {}
    for p in raw_dir.glob("*.json"):
        try:
            raw_data[p.stem] = json.loads(p.read_text())
        except:
            continue
    return raw_data

def main():
    today = datetime.now().strftime("%Y%m%d")
    raw_dir = Path(f"data/raw/{today}")
    
    if not raw_dir.exists():
        print(f"❌ Raw data directory not found: {raw_dir}")
        return

    print(f"🎬 Topic Selection Engine 실행 시작 (Date: {today})")
    
    # Load raw data
    raw_data = load_all_raw_data(raw_dir)
    if not raw_data:
        print("❌ No raw data found in directory")
        return
        
    engine = TopicSelectionEngine(base_dir=Path("."))
    selection = engine.run(raw_data)
    
    if selection and selection.get("MAIN"):
        print(f"\n🏆 최종 선정 토픽: {selection['MAIN']['event']}")
        print(f"📌 Why Now: {selection['MAIN'].get('why_now', 'N/A')}")
    else:
        print("\n⚠️ 토픽 선정 실패 또는 결과 없음")

if __name__ == "__main__":
    main()
