
import json
import io
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from src.dashboard.dashboard_generator import generate_dashboard
from src.ops.structural_memory_engine import StructuralMemoryEngine
from src.ops.snapshot_comparison_engine import SnapshotComparisonEngine

def setup_mock_data(base_dir: Path):
    now = datetime.utcnow()
    ymd = now.strftime("%Y-%m-%d")
    ymd_path = now.strftime("%Y/%m/%d")
    
    # 1. Setup Dirs
    dashboard_dir = base_dir / "data" / "dashboard"
    decision_dir = base_dir / "data" / "decision" / ymd_path
    memory_dir = base_dir / "data" / "snapshots" / "memory"
    
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    decision_dir.mkdir(parents=True, exist_ok=True)
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Create D-1 Snapshot (Yesterday)
    # Scenario: Same Topic, Lower Intensity -> Expect RECURRING + INTENSIFIED
    d1_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    d1_snap = {
        "date": d1_date,
        "top_signal": {
            "title": "AI 데이터 센터 전력망 붕괴 위기", # SAME TITLE
            "intensity": "STRIKE" # LOWER
        },
        "entities": [
            {"name": "효성중공업", "state": "OBSERVE"}
        ]
    }
    (memory_dir / f"{d1_date}.json").write_text(json.dumps(d1_snap), encoding="utf-8")
    
    # 3. Create Today Data
    today_data = {
        "date": ymd,
        "top_signal": {
            "title": "AI 데이터 센터 전력망 붕괴 위기",
            "pressure_type": "Infrastructure",
            "intensity": "DEEP_HUNT", # HIGHER
            "rhythm": "SHOCK_DRIVE",
            "escalation_count": 5
        }
    }
    (dashboard_dir / "today.json").write_text(json.dumps(today_data), encoding="utf-8")
    
    decision_data = {
        "top_topics": [
            {
                "title": "AI 데이터 센터 전력망 붕괴 위기",
                "leader_stocks": ["효성중공업", "KODEX 200선물인버스2X"]
            }
        ]
    }
    (decision_dir / "final_decision_card.json").write_text(json.dumps(decision_data), encoding="utf-8")
    
    return ymd

def verify_output(base_dir: Path, today_date: str):
    # 1. File Integrity Check
    snap_path = base_dir / "data" / "snapshots" / "memory" / f"{today_date}.json"
    if snap_path.exists():
        print(f"✅ Found Snapshot File: {snap_path.name}")
        content = json.loads(snap_path.read_text(encoding="utf-8"))
        if "memory_hash" in content:
            print("✅ Memory Hash exists")
        else:
            print("❌ Memory Hash missing")
            sys.exit(1)
    else:
        print(f"❌ Snapshot File Not Found: {snap_path}")
        sys.exit(1)
        
    # 2. Dashboard UI Check
    html_path = base_dir / "dashboard" / "index.html"
    html_content = html_path.read_text(encoding="utf-8")
    
    if "Recurring Structure" in html_content:
        print("✅ Found: Recurring Status (Correct)")
    else:
        print("❌ Missing Recurring Status. Content Preview:")
        print(html_content[:500])
        sys.exit(1)
        
    if "INTENSIFIED" in html_content:
        print("✅ Found: Intensity Delta (Correct)")
    else:
        print("❌ Missing Intensity Delta (Expected INTENSIFIED)")
        sys.exit(1)
        
    print("\nSUCCESS: Step 85 Memory & Comparison Verified.")

if __name__ == "__main__":
    today_date = setup_mock_data(root_dir)
    try:
        generate_dashboard(root_dir)
        verify_output(root_dir, today_date)
    except Exception as e:
        print(f"Runtime Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
