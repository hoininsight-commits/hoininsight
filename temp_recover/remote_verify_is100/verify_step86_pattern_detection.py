
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from src.dashboard.dashboard_generator import generate_dashboard

def setup_mock_data(base_dir: Path):
    now = datetime.utcnow()
    ymd = now.strftime("%Y-%m-%d")
    ymd_path = now.strftime("%Y/%m/%d")
    
    # 1. Setup Dirs
    dashboard_dir = base_dir / "data" / "dashboard"
    decision_dir = base_dir / "data" / "decision" / ymd_path
    pattern_dir = base_dir / "data" / "snapshots" / "patterns"
    
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    decision_dir.mkdir(parents=True, exist_ok=True)
    pattern_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Daily Data
    today_data = {
        "date": ymd,
        "top_signal": {
            "title": "중앙은행 신뢰 위기와 금리 경로",
            "intensity": "DEEP_HUNT"
        }
    }
    (dashboard_dir / "today.json").write_text(json.dumps(today_data), encoding="utf-8")
    
    # 3. Decision Card (Mocking Pattern Trigger Keywords)
    # Keywords: "중앙은행", "신뢰", "금", "Sticky", "국채" -> Should trigger SYSTEM_TRUST_STRESS & REAL_RATE_TENSION
    decision_data = {
        "top_topics": [],
        "raw_signals": "최근 중앙은행의 독립성에 대한 의구심이 커지며 신뢰가 흔들리고 있다. 이에 따라 금(Gold)과 같은 안전자산 선호가 강해지고 있음. 한편 인플레이션이 Sticky하게 유지되면서 국채 수익률의 변동성이 확대되고 있어 밸류에이션 부담이 가중됨."
    }
    # Using 'raw_signals' or just stringifying the whole dict for detection
    (decision_dir / "final_decision_card.json").write_text(json.dumps(decision_data), encoding="utf-8")
    
    return ymd

def verify_output(base_dir: Path, today_date: str):
    # 1. File Integrity
    snap_path = base_dir / "data" / "snapshots" / "patterns" / f"{today_date}.json"
    if snap_path.exists():
        print(f"✅ Found Pattern Snapshot: {snap_path.name}")
        content = json.loads(snap_path.read_text(encoding="utf-8"))
        if "pattern_hash" in content:
            print("✅ Pattern Hash exists")
        else:
            print("❌ Pattern Hash missing")
            sys.exit(1)
    else:
        print(f"❌ Pattern Snapshot Not Found: {snap_path}")
        sys.exit(1)
        
    # 2. Logic Check
    active_patterns = content.get("active_patterns", [])
    detected_types = [p["pattern_type"] for p in active_patterns]
    
    print(f"🧐 Detected Patterns: {detected_types}")
    
    if "SYSTEM_TRUST_STRESS" in detected_types:
        print("✅ Detected: SYSTEM_TRUST_STRESS")
    else:
        print("❌ Missing: SYSTEM_TRUST_STRESS")
        sys.exit(1)
        
    if "REAL_RATE_TENSION" in detected_types:
        print("✅ Detected: REAL_RATE_TENSION")
    else:
        print("❌ Missing: REAL_RATE_TENSION")
        sys.exit(1)
        
    print("\nSUCCESS: Step 86 Pattern Detection Verified.")

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
