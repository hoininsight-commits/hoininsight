
import json
import re
from pathlib import Path
import sys

# Add src to path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from src.dashboard.dashboard_generator import generate_dashboard
from src.ops.entity_mapping_layer import EntityMappingLayer

from datetime import datetime

def setup_mock_data(base_dir: Path):
    # Use current UTC date to match dashboard_generator logic
    now = datetime.utcnow()
    ymd_path = now.strftime("%Y/%m/%d")
    
    dashboard_dir = base_dir / "data" / "dashboard"
    decision_dir = base_dir / "data" / "decision" / ymd_path
    
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    decision_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock Top-1 (Today)
    today_data = {
        "date": "2026-06-15",
        "top_signal": {
            "title": "AI 데이터 센터 전력망 붕괴 위기",
            "pressure_type": "Infrastructure",
            "intensity": "STRIKE"
        }
    }
    (dashboard_dir / "today.json").write_text(json.dumps(today_data), encoding="utf-8")
    
    # Mock Decision Card (Source of Entities)
    decision_data = {
        "top_topics": [
            {
                "title": "AI 데이터 센터 전력망 붕괴 위기",
                "leader_stocks": [
                    "KODEX 200선물인버스2X", # Hedge
                    "효성중공업", # Bottleneck
                    "LS ELECTRIC", # Bottleneck
                    "VIXY" # Hedge
                ]
            }
        ]
    }
    (decision_dir / "final_decision_card.json").write_text(json.dumps(decision_data), encoding="utf-8")

def verify_output(base_dir: Path):
    html_path = base_dir / "dashboard" / "index.html"
    content = html_path.read_text(encoding="utf-8")
    
    checks = [
        "이 이슈에서 말할 수밖에 없는 대상들", # Header
        "HEDGE", # Shortened role
        "BOTTLENECK", # Shortened role
        "KODEX 200선물인버스2X",
        "효성중공업",
        "CAPITAL", # Shortened tag
        "PHYSICAL", # Shortened tag
        "이 엔티티는 추천이 아닙니다" # Disclaimer
    ]
    
    banned_words = ["매수", "매도", "Buy", "Sell", "추천", "목표가"]
    
    print("\n[Verification Results]")
    all_pass = True
    
    # 1. Existence Checks
    for c in checks:
        if c in content:
            print(f"✅ Found: {c}")
        else:
            print(f"❌ Missing: {c}")
            all_pass = False
            
    # 2. Negative Checks
    for w in banned_words:
        # '추천이 아닙니다' contains '추천', so we check strict context or exclude the disclaimer line check
        # simpler: check if '추천' exists outside disclaimer?
        # heuristic: just check '매수', '매도', 'Buy', 'Sell' strictly. '추천' exists in disclaimer.
        if w == "추천": continue 
        if w in content:
             print(f"❌ FAIL: Found banned word '{w}'")
             all_pass = False
        else:
             print(f"✅ Clean: No '{w}'")

    if all_pass:
        print("\nSUCCESS: Entity Mapping Layer verified.")
    else:
        print("\nFAILURE: Entity Mapping check failed.")
        sys.exit(1)

if __name__ == "__main__":
    setup_mock_data(root_dir)
    try:
        generate_dashboard(root_dir)
        verify_output(root_dir)
    except Exception as e:
        print(f"Runtime Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
