import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.issuesignal.engines.statement_momentum_engine import StatementMomentumEngine
from src.issuesignal.run_issuesignal import main as run_pipeline
from src.issuesignal.dashboard.build_dashboard import DashboardBuilder

def verify_is94():
    base_dir = Path(__file__).parent.parent
    print("=== IS-94 Verification Started ===")

    # 1. Create Mock Historical Data (to ensure ESCALATING)
    # We need 7+ mentions with intensity keywords in the last 30 days
    stmt_dir = base_dir / "data" / "statements"
    stmt_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now()
    mock_history = []
    for i in range(10):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        mock_history.append({
            "source_type": "OFFICIAL",
            "person_or_org": "Elon Musk",
            "organization": "Tesla",
            "published_at": date,
            "content": f"AI infrastructure is absolutely critical and we must scale up massive capacity now. #{i}",
            "trust_level": "HARD_FACT",
            "source_url": "https://tesla.com/blog/mock"
        })
    
    mock_file = stmt_dir / "mock_momentum_history.json"
    with open(mock_file, "w", encoding="utf-8") as f:
        json.dump(mock_history, f, indent=2)
    print(f"Created mock history: {mock_file}")

    # 2. Test Engine directly
    engine = StatementMomentumEngine(base_dir)
    results = engine.process([mock_history[0]]) # Process today's latest statement
    
    print("\n--- Momentum Results ---")
    found_musk = False
    for res in results:
        print(f"Person: {res['person']}, Theme: {res['theme']}, Score: {res['momentum_score']}, State: {res['momentum_state']}")
        if res['person'] == "Elon Musk" and res['momentum_state'] == "ESCALATING":
            found_musk = True
            
    assert found_musk, "Failed to detect ESCALATING state for Elon Musk AI theme"
    print("✅ Engine correctly identified ESCALATING status.")

    # 3. Run Pipeline (Simulated)
    # We'll run a limited version or just check if the momentum file is created
    print("\n--- Running Pipeline Integration Test ---")
    run_pipeline() # This should use the mock history we just created
    
    ymd = datetime.now().strftime("%Y%m%d")
    momentum_report = base_dir / "data" / "momentum" / f"statement_momentum_{ymd}.json"
    assert momentum_report.exists(), "Momentum report JSON was not created by pipeline"
    print(f"✅ Momentum report created at {momentum_report.name}")

    # 4. Verify Dashboard Rendering
    print("\n--- Verifying Dashboard Rendering ---")
    builder = DashboardBuilder(base_dir)
    html_path = builder.build()
    
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    assert "발언 모멘텀 감지" in html, "'발언 모멘텀 감지' section missing from HTML"
    assert "ESCALATING" in html or "에스컬레이션" in html, "Escalating status badge missing from HTML"
    assert "Elon Musk" in html, "Person name missing from momentum section"
    print("✅ Dashboard rendering verified. New section and data are present.")

    # Cleanup mock data
    mock_file.unlink()
    
    print("\n=== IS-94 Verification COMPLETE: SUCCESS ===")

if __name__ == "__main__":
    try:
        verify_is94()
    except Exception as e:
        print(f"❌ Verification FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
