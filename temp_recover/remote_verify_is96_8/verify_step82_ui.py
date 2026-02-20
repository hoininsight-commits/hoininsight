
import json
import re
from pathlib import Path
import sys

# Add src to path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from src.dashboard.dashboard_generator import generate_dashboard

def setup_mock_data(base_dir: Path):
    dashboard_dir = base_dir / "data" / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock Today
    today_data = {
        "date": "2026-06-15",
        "top_signal": {
            "title": "AI 데이터 센터 전력망 붕괴 위기",
            "why_now": "Escalated from Pre-Structural Signal: 30일 내 예비율 5% 하회 전망",
            "trigger": "Mechanism Activation",
            "intensity": "STRIKE",
            "rhythm": "SHOCK_DRIVE",
            "sectors": ["Power", "AI", "Infrastructure"],
            "status": "LOCK",
            "pressure_type": "Infrastructure",
            "escalation_count": 3,
            "scope_hint": "Multi-Sector Potential"
        }
    }
    (dashboard_dir / "today.json").write_text(json.dumps(today_data), encoding="utf-8")
    (dashboard_dir / "2026-06-15.json").write_text(json.dumps(today_data), encoding="utf-8")

    # Mock History 1
    hist1 = {
        "date": "2026-06-10",
        "top_signal": {
            "title": "국채 금리 발작과 유동성 경색",
            "why_now": "SmartMoney Divergence observed",
            "trigger": "Smart Money Divergence",
            "intensity": "FLASH",
            "rhythm": "STRUCTURE_FLOW",
            "sectors": ["Bond", "Banking"],
            "status": "WATCH",
            "pressure_type": "Liquidity",
            "escalation_count": 1,
            "scope_hint": "Multi-Sector Potential"
        }
    }
    (dashboard_dir / "2026-06-10.json").write_text(json.dumps(hist1), encoding="utf-8")

    # Mock History 2 (Single Sector)
    hist2 = {
        "date": "2026-06-05",
        "top_signal": {
            "title": "특정 반도체 공정 수율 저하",
            "why_now": "Scheduled Catalyst Arrival",
            "trigger": "Scheduled Catalyst Arrival",
            "intensity": "DEEP_HUNT",
            "rhythm": "DEEP_TRACE",
            "sectors": ["Semiconductor"],
            "status": "WATCH",
            "pressure_type": "Structural",
            "escalation_count": 0,
            "scope_hint": "Single-Sector"
        }
    }
    (dashboard_dir / "2026-06-05.json").write_text(json.dumps(hist2), encoding="utf-8")

def verify_output(base_dir: Path):
    html_path = base_dir / "dashboard" / "index.html"
    content = html_path.read_text(encoding="utf-8")
    
    checks = [
        "AI 데이터 센터 전력망 붕괴 위기", # Title Present (Top-1)
        "🟣 오늘의 구조적 핵심 이슈", # Header Present
        "SHOCK_DRIVE", # Rhythm Present
        "🔥 +3", # Escalation Present
        "국채 금리 발작과 유동성 경색", # History Item 1
        "특정 반도체 공정 수율 저하", # History Item 2
        "badge-whynow-smartmoney", # Badge class
        "Multi-Sector Potential"
    ]
    
    print("\n[Verification Results]")
    all_pass = True
    for c in checks:
        if c in content:
            print(f"✅ Found: {c}")
        else:
            print(f"❌ Missing: {c}")
            all_pass = False
            
    if all_pass:
        print("\nSUCCESS: Dashboard render verified.")
    else:
        print("\nFAILURE: Dashboard render incomplete.")
        sys.exit(1)

if __name__ == "__main__":
    setup_mock_data(root_dir)
    try:
        generate_dashboard(root_dir)
        verify_output(root_dir)
    except Exception as e:
        print(f"Runtime Warning: {e}")
        # Even if pipeline fails (e.g. missing other files), check if HTML was written
        verify_output(root_dir)
