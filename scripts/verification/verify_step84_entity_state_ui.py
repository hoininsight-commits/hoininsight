
import json
import io
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from src.dashboard.dashboard_generator import generate_dashboard
from src.ops.entity_state_classifier import EntityState, EntityStateClassifier

def setup_mock_data(base_dir: Path):
    now = datetime.utcnow()
    ymd_path = now.strftime("%Y/%m/%d")
    
    dashboard_dir = base_dir / "data" / "dashboard"
    decision_dir = base_dir / "data" / "decision" / ymd_path
    
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    decision_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock Top-1 (Deep Hunt Crisis)
    today_data = {
        "date": now.strftime("%Y-%m-%d"),
        "top_signal": {
            "title": "AI 데이터 센터 전력망 붕괴 위기",
            "pressure_type": "Infrastructure",
            "intensity": "DEEP_HUNT", # High Intensity
            "rhythm": "SHOCK_DRIVE",
            "escalation_count": 5 # Max Escalation
        }
    }
    (dashboard_dir / "today.json").write_text(json.dumps(today_data), encoding="utf-8")
    
    # Mock Decision Card
    decision_data = {
        "top_topics": [
            {
                "title": "AI 데이터 센터 전력망 붕괴 위기",
                "leader_stocks": [
                    "KODEX 200선물인버스2X", # Should be PRESSURE/RESOLUTION
                    "효성중공업", # Should be PRESSURE
                ]
            }
        ]
    }
    (decision_dir / "final_decision_card.json").write_text(json.dumps(decision_data), encoding="utf-8")

def verify_output(base_dir: Path):
    html_path = base_dir / "dashboard" / "index.html"
    content = html_path.read_text(encoding="utf-8")
    
    print("\n[Verification Results]")
    
    # 1. Header Check
    if "현재 인식해야 할 구조적 상태" in content:
        print("✅ Found Header: Decision Surface")
    else:
        print("❌ Missing Header")
        sys.exit(1)
        
    # 2. State Logic Check
    # In DEEP_HUNT + Escalation 5, we expect RESOLUTION or PRESSURE
    if "RESOLUTION" in content:
        print("✅ Found: RESOLUTION State (Correct High Intensity Logic)")
    elif "PRESSURE" in content:
        print("✅ Found: PRESSURE State")
    else:
        print("❌ Missing Expected States (RESOLUTION/PRESSURE)")
        print("Content Preview:", content[:500])
        sys.exit(1)
        
    # 3. Justification Check
    if "해소 국면에 진입했습니다" in content or "구조적 제약이 실제로 작동 중입니다" in content:
        print("✅ Found: Justification Logic")
    else:
        print("❌ Missing Justification Text")
        sys.exit(1)

    # 4. Disclaimer Check
    if "이 상태는 행동 지시가 아닙니다" in content:
         print("✅ Found: Disclaimer")
    else:
         print("❌ Missing Disclaimer")
         sys.exit(1)
         
    # 5. UI Class Check
    if "state-resolution" in content or "state-pressure" in content:
        print("✅ Found: CSS Classes")
    else:
        print("❌ Missing CSS Classes")
        sys.exit(1)

    print("\nSUCCESS: Step 84 UI Verified.")

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
