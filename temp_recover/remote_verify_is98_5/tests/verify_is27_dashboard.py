import sys
from pathlib import Path
import json
import os

# Add root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.dashboard.build_dashboard import DashboardBuilder

def main():
    base_dir = Path(".")
    print(f"\n[VERIFY] Starting IssueSignal Dashboard Verification (IS-27)")
    
    # 1. Prepare temp fixtures
    temp_dir = base_dir / "data" / "decision" / "final_decision_cards"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a mock TRUST_LOCKED card
    mock_card = {
        "topic_id": "TEST-LOCKED-001",
        "title": "Verification Success",
        "status": "TRUST_LOCKED",
        "one_liner": "Dashboard logic verified with simulated data.",
        "trigger_type": "STRUCTURAL",
        "actor": "BOT",
        "must_item": "LOGIC",
        "tickers": [{"ticker": "TEST", "role": "OWNER"}],
        "kill_switch": "If tests fail."
    }
    with open(temp_dir / "TEST-LOCKED-001.json", "w", encoding="utf-8") as f:
        json.dump(mock_card, f)
        
    # 2. Run Builder
    builder = DashboardBuilder(base_dir)
    html_path = builder.build()
    
    # 3. Assertions
    if not html_path.exists():
        print("[VERIFY][FAIL] index.html not created.")
        return

    content = html_path.read_text(encoding="utf-8")
    sections = ["SUMMARY", "TRUST_LOCKED", "WATCHLIST", "SILENT QUEUE"]
    missing = [s for s in sections if s not in content.upper()]
    
    if not missing:
        print(f"[VERIFY][SUCCESS] Dashboard built successfully at {html_path}")
        print(f" - Contains key sections: {', '.join(sections)}")
    else:
        print(f"[VERIFY][FAIL] Missing sections in HTML: {missing}")

    # Clean up temp fixture (optional, keep for manual view)
    # os.remove(temp_dir / "TEST-LOCKED-001.json")

if __name__ == "__main__":
    main()
